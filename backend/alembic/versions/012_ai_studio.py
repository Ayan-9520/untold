"""AI Studio — prompts, outputs, provider metadata."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "012_ai_studio"
down_revision: Union[str, None] = "011_storyboard_studio"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("ai_generations", sa.Column("provider", sa.String(length=64), server_default="demo", nullable=False))
    op.add_column("ai_generations", sa.Column("output_text", sa.Text(), nullable=True))
    op.add_column("ai_generations", sa.Column("output_meta", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("ai_generations", sa.Column("retry_count", sa.Integer(), server_default="0", nullable=False))
    op.add_column("ai_generations", sa.Column("started_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("ai_generations", sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "ai_generations",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
    )

    op.create_table(
        "ai_prompt_library",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("module", sa.String(length=64), nullable=False),
        sa.Column("prompt_template", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("parameters", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("is_public", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_prompt_library_module", "ai_prompt_library", ["module"])


def downgrade() -> None:
    op.drop_index("ix_ai_prompt_library_module", table_name="ai_prompt_library")
    op.drop_table("ai_prompt_library")
    op.drop_column("ai_generations", "updated_at")
    op.drop_column("ai_generations", "cancelled_at")
    op.drop_column("ai_generations", "started_at")
    op.drop_column("ai_generations", "retry_count")
    op.drop_column("ai_generations", "output_meta")
    op.drop_column("ai_generations", "output_text")
    op.drop_column("ai_generations", "provider")
