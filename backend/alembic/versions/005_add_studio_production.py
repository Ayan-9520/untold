"""Add Studio production pipeline tables."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005_add_studio_production"
down_revision: Union[str, None] = "004_add_monetization_engine"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "productions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=200), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("stage", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("assignee", sa.String(length=120), nullable=False),
        sa.Column("sources_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("video_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["video_id"], ["videos.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_productions_id"), "productions", ["id"], unique=False)
    op.create_index(op.f("ix_productions_slug"), "productions", ["slug"], unique=True)
    op.create_index(op.f("ix_productions_stage"), "productions", ["stage"], unique=False)

    op.create_table(
        "ai_agent_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("agent_id", sa.String(length=40), nullable=False),
        sa.Column("production_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="queued"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["production_id"], ["productions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_agent_jobs_id"), "ai_agent_jobs", ["id"], unique=False)
    op.create_index(op.f("ix_ai_agent_jobs_agent_id"), "ai_agent_jobs", ["agent_id"], unique=False)
    op.create_index(op.f("ix_ai_agent_jobs_production_id"), "ai_agent_jobs", ["production_id"], unique=False)


def downgrade() -> None:
    op.drop_table("ai_agent_jobs")
    op.drop_table("productions")
