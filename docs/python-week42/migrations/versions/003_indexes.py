"""Add measured filter/association indexes; rollback removes indexes, not notes."""

from alembic import op

revision = "w42_003"
down_revision = "w42_002"
branch_labels = depends_on = None


def upgrade():
    op.create_index("ix_notes_owner_completed_id", "notes", ["owner_id", "completed", "id"])
    op.create_index("ix_note_tags_tag_note", "note_tags", ["tag_id", "note_id"])


def downgrade():
    op.drop_index("ix_note_tags_tag_note", table_name="note_tags")
    op.drop_index("ix_notes_owner_completed_id", table_name="notes")
