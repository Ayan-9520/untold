"""Storyboard Studio — revisions, reorder, script import."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "011_storyboard_studio"
down_revision: Union[str, None] = "010_script_studio"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("storyboard_scenes", sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False))
    op.add_column(
        "storyboard_scenes",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
    )

    op.execute(
        "UPDATE storyboard_scenes SET sort_order = scene_number WHERE sort_order = 0 OR sort_order IS NULL"
    )

    op.create_table(
        "storyboard_revisions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=300), nullable=True),
        sa.Column("scenes_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["productions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_storyboard_revisions_project_id", "storyboard_revisions", ["project_id"])


def downgrade() -> None:
    op.drop_index("ix_storyboard_revisions_project_id", table_name="storyboard_revisions")
    op.drop_table("storyboard_revisions")
    op.drop_column("storyboard_scenes", "updated_at")
    op.drop_column("storyboard_scenes", "sort_order")
