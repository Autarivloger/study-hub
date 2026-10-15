"""Relational models: owned notes, shared tags and individually revocable logins."""
from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Index, Integer, MetaData, String, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": "ix_%(table_name)s_%(column_0_name)s", "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s", "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"})


note_tags = Table("note_tags", Base.metadata,
    Column("note_id", ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    Index("ix_note_tags_tag_note", "tag_id", "note_id"))


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=True)
    password_hash: Mapped[str] = mapped_column(String)
    notes: Mapped[list["Note"]] = relationship(back_populates="owner", cascade="all, delete-orphan", passive_deletes=True)
    logins: Mapped[list["LoginSession"]] = relationship(back_populates="user", cascade="all, delete-orphan", passive_deletes=True)


class Note(Base):
    __tablename__ = "notes"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(100))
    body: Mapped[str] = mapped_column(String(2000))
    completed: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    created_at: Mapped[str] = mapped_column(String)
    owner: Mapped[User] = relationship(back_populates="notes")
    tags: Mapped[list["Tag"]] = relationship(secondary=note_tags, back_populates="notes", passive_deletes=True, order_by="Tag.name")
    __table_args__ = (
        CheckConstraint("length(trim(title)) BETWEEN 1 AND 100", name="title_length"),
        CheckConstraint("length(trim(body)) BETWEEN 1 AND 2000", name="body_length"),
        CheckConstraint("completed IN (0,1)", name="completed_boolean"),
        Index("ix_notes_owner_id", "owner_id", "id"),
        Index("ix_notes_owner_completed_id", "owner_id", "completed", "id"),
    )


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    notes: Mapped[list[Note]] = relationship(secondary=note_tags, back_populates="tags", passive_deletes=True)


class LoginSession(Base):
    __tablename__ = "token_sessions"
    jti: Mapped[str] = mapped_column(String(100), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    expires_at: Mapped[int] = mapped_column(Integer)
    user: Mapped[User] = relationship(back_populates="logins")
