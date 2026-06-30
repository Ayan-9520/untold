"""Project management — due dates and project comments."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "008_project_management"
down_revision: Union[str, None] = "007_studio_auth"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("productions", sa.Column("due_date", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_productions_due_date", "productions", ["due_date"])

    op.create_table(
        "project_comments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["productions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_project_comments_project_id", "project_comments", ["project_id"])
    op.create_index("ix_project_comments_user_id", "project_comments", ["user_id"])

    # Normalize legacy stage values
    op.execute("UPDATE productions SET stage = 'editing' WHERE stage IN ('edit', 'video')")
    op.execute("UPDATE productions SET stage = 'publishing' WHERE stage = 'publish'")


def downgrade() -> None:
    op.drop_table("project_comments")
    op.drop_index("ix_productions_due_date", table_name="productions")
    op.drop_column("productions", "due_date")
