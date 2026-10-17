"""Baseline API tables, independently declared so future model edits cannot rewrite history."""

from alembic import op
import sqlalchemy as sa

revision = "w43_001"
down_revision = None
branch_labels = depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String(32), nullable=False),
        sa.Column("password_hash", sa.String, nullable=False),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )
    op.create_table(
        "notes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "owner_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("body", sa.String(2000), nullable=False),
        sa.Column("completed", sa.Boolean, server_default=sa.false(), nullable=False),
        sa.Column("created_at", sa.String, nullable=False),
        sa.CheckConstraint(
            "length(trim(title)) BETWEEN 1 AND 100", name=op.f("ck_notes_title_length")
        ),
        sa.CheckConstraint(
            "length(trim(body)) BETWEEN 1 AND 2000", name=op.f("ck_notes_body_length")
        ),
        sa.CheckConstraint("completed IN (false,true)", name=op.f("ck_notes_completed_boolean")),
    )
    op.create_index("ix_notes_owner_id", "notes", ["owner_id", "id"])
    op.create_table(
        "token_sessions",
        sa.Column("jti", sa.String(100), primary_key=True),
        sa.Column(
            "user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("expires_at", sa.Integer, nullable=False),
    )


def downgrade():
    op.drop_table("token_sessions")
    op.drop_index("ix_notes_owner_id", table_name="notes")
    op.drop_table("notes")
    op.drop_table("users")
