"""Research AI agent — structured insights, history, approval."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "017_research_ai_agent"
down_revision: Union[str, None] = "016_studio_analytics_admin"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("research_sessions", sa.Column("statistics", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("research_sessions", sa.Column("public_facts", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("research_sessions", sa.Column("follow_up_questions", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("research_sessions", sa.Column("rejection_notes", sa.Text(), nullable=True))

    op.create_table(
        "research_ai_interactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("research_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("response", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("provider", sa.String(length=64), server_default="demo", nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["research_id"], ["research_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_research_ai_interactions_research_id", "research_ai_interactions", ["research_id"])


def downgrade() -> None:
    op.drop_index("ix_research_ai_interactions_research_id", table_name="research_ai_interactions")
    op.drop_table("research_ai_interactions")
    op.drop_column("research_sessions", "rejection_notes")
    op.drop_column("research_sessions", "follow_up_questions")
    op.drop_column("research_sessions", "public_facts")
    op.drop_column("research_sessions", "statistics")
