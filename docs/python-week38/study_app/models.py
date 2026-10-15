from sqlalchemy import CheckConstraint,ForeignKey,Index,String,Table,Column,Text
from sqlalchemy.orm import Mapped,mapped_column,relationship
from .extensions import db

post_tags=Table("post_tags",db.metadata,
    Column("post_id",ForeignKey("posts.id",ondelete="CASCADE"),primary_key=True),
    Column("tag_id",ForeignKey("tags.id",ondelete="CASCADE"),primary_key=True))


class User(db.Model):
    __tablename__="users"
    id:Mapped[int]=mapped_column(primary_key=True)
    username:Mapped[str]=mapped_column(String(32),unique=True,nullable=False)
    password_hash:Mapped[str]=mapped_column(Text,nullable=False)
    posts:Mapped[list["Post"]]=relationship(back_populates="author")


class Post(db.Model):
    __tablename__="posts"
    id:Mapped[int]=mapped_column(primary_key=True)
    author_id:Mapped[int]=mapped_column(ForeignKey("users.id"),nullable=False)
    title:Mapped[str]=mapped_column(String(100),nullable=False)
    body:Mapped[str]=mapped_column(Text,nullable=False)
    author:Mapped[User]=relationship(back_populates="posts")
    tags:Mapped[list["Tag"]]=relationship(secondary=post_tags,back_populates="posts")
    __table_args__=(CheckConstraint("length(trim(title)) BETWEEN 1 AND 100"),
                   CheckConstraint("length(trim(body)) BETWEEN 1 AND 2000"),
                   Index("posts_author_id_id","author_id","id"))


class Tag(db.Model):
    __tablename__="tags"
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(32),unique=True,nullable=False)
    posts:Mapped[list[Post]]=relationship(secondary=post_tags,back_populates="tags")


class LoginSession(db.Model):
    __tablename__="login_sessions"
    id:Mapped[str]=mapped_column(String(64),primary_key=True)
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id"),nullable=False,index=True)
    expires_at:Mapped[int]=mapped_column(nullable=False)
