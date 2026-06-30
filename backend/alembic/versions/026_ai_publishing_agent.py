"""AI Publishing Agent migration."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "026_ai_publishing_agent"
down_revision: Union[str, None] = "025_ai_translation_studio"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "publish_agent_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("platforms", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), server_default="queued", nullable=False),
        sa.Column("requires_approval", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("approval_status", sa.String(length=32), server_default="pending", nullable=False),
        sa.Column("progress", sa.Integer(), server_default="0", nullable=False),
        sa.Column("output_meta", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("celery_task_id", sa.String(length=64), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["productions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_publish_agent_runs_project_id", "publish_agent_runs", ["project_id"])
    op.create_index("ix_publish_agent_runs_status", "publish_agent_runs", ["status"])

    op.create_table(
        "publish_webhooks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("url", sa.String(length=2000), nullable=False),
        sa.Column("events", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("secret", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("last_triggered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["productions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "publish_platform_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("agent_run_id", sa.Integer(), nullable=True),
        sa.Column("publish_job_id", sa.Integer(), nullable=True),
        sa.Column("platform", sa.String(length=32), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["agent_run_id"], ["publish_agent_runs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["productions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["publish_job_id"], ["publish_jobs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_publish_platform_events_project_id", "publish_platform_events", ["project_id"])
    op.create_index("ix_publish_platform_events_platform", "publish_platform_events", ["platform"])

    op.add_column("publish_jobs", sa.Column("agent_run_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_publish_jobs_agent_run_id",
        "publish_jobs",
        "publish_agent_runs",
        ["agent_run_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_publish_jobs_agent_run_id", "publish_jobs", ["agent_run_id"])


def downgrade() -> None:
    op.drop_index("ix_publish_jobs_agent_run_id", table_name="publish_jobs")
    op.drop_constraint("fk_publish_jobs_agent_run_id", "publish_jobs", type_="foreignkey")
    op.drop_column("publish_jobs", "agent_run_id")
    op.drop_index("ix_publish_platform_events_platform", table_name="publish_platform_events")
    op.drop_index("ix_publish_platform_events_project_id", table_name="publish_platform_events")
    op.drop_table("publish_platform_events")
    op.drop_table("publish_webhooks")
    op.drop_index("ix_publish_agent_runs_status", table_name="publish_agent_runs")
    op.drop_index("ix_publish_agent_runs_project_id", table_name="publish_agent_runs")
    op.drop_table("publish_agent_runs")
