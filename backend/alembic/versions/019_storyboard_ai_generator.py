"""Storyboard AI generator — migration 019."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "019_storyboard_ai_generator"
down_revision: Union[str, None] = "018_script_ai_writer"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("storyboard_scenes", sa.Column("dialogue", sa.Text(), nullable=True))
    op.add_column("storyboard_scenes", sa.Column("shot_type", sa.String(length=120), nullable=True))
    op.add_column("storyboard_scenes", sa.Column("mood", sa.String(length=120), nullable=True))
    op.add_column("storyboard_scenes", sa.Column("transition", sa.String(length=120), nullable=True))

    op.create_table(
        "storyboard_ai_interactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=True),
        sa.Column("response", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("provider", sa.String(length=64), server_default="demo", nullable=False),
        sa.Column("ai_generation_id", sa.Integer(), nullable=True),
        sa.Column("scenes_created", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["ai_generation_id"], ["ai_generations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["productions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_storyboard_ai_interactions_project_id", "storyboard_ai_interactions", ["project_id"])


def downgrade() -> None:
    op.drop_index("ix_storyboard_ai_interactions_project_id", table_name="storyboard_ai_interactions")
    op.drop_table("storyboard_ai_interactions")
    op.drop_column("storyboard_scenes", "transition")
    op.drop_column("storyboard_scenes", "mood")
    op.drop_column("storyboard_scenes", "shot_type")
    op.drop_column("storyboard_scenes", "dialogue")
