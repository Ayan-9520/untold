"""Script Studio — workspace autosave, collaboration, comments, approval."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "010_script_studio"
down_revision: Union[str, None] = "009_research_studio"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("scripts", sa.Column("content_version", sa.Integer(), server_default="1", nullable=False))
    op.add_column("scripts", sa.Column("last_auto_saved_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("scripts", sa.Column("last_edited_by_id", sa.Integer(), nullable=True))
    op.add_column(
        "scripts",
        sa.Column("active_collaborators", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
    )
    op.add_column("scripts", sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("scripts", sa.Column("approved_by_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_scripts_last_edited_by", "scripts", "users", ["last_edited_by_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_scripts_approved_by", "scripts", "users", ["approved_by_id"], ["id"], ondelete="SET NULL")

    op.add_column("script_versions", sa.Column("snapshot_label", sa.String(length=200), nullable=True))

    op.create_table(
        "script_studio_comments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("script_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["script_id"], ["scripts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_script_studio_comments_script_id", "script_studio_comments", ["script_id"])


def downgrade() -> None:
    op.drop_index("ix_script_studio_comments_script_id", table_name="script_studio_comments")
    op.drop_table("script_studio_comments")
    op.drop_column("script_versions", "snapshot_label")
    op.drop_constraint("fk_scripts_approved_by", "scripts", type_="foreignkey")
    op.drop_constraint("fk_scripts_last_edited_by", "scripts", type_="foreignkey")
    op.drop_column("scripts", "approved_by_id")
    op.drop_column("scripts", "approved_at")
    op.drop_column("scripts", "active_collaborators")
    op.drop_column("scripts", "last_edited_by_id")
    op.drop_column("scripts", "last_auto_saved_at")
    op.drop_column("scripts", "content_version")
