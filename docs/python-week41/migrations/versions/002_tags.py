"""Add shared tags and a composite-primary-key association table."""

from alembic import op
import sqlalchemy as sa

revision = "w40_002"
down_revision = "w40_001"
branch_labels = depends_on = None


def upgrade():
    tags = op.create_table(
        "tags",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(30), nullable=False),
        sa.UniqueConstraint("name", name="uq_tags_name"),
    )
    op.create_table(
        "note_tags",
        sa.Column(
            "note_id", sa.Integer, sa.ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column(
            "tag_id", sa.Integer, sa.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
        ),
    )
    op.bulk_insert(tags, [{"name": name} for name in ("python", "api", "database")])


def downgrade():
    # This intentionally removes all tag assignments/tag rows. Use only a reviewed backup/test copy.
    op.drop_table("note_tags")
    op.drop_table("tags")
