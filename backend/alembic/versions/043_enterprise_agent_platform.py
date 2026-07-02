"""Enterprise AI agent platform — execution logs, memory, schedules, messaging."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "043_enterprise_agent_platform"
down_revision: Union[str, None] = "042_enterprise_workflow"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("agent_installations", sa.Column("organization_id", sa.Integer(), nullable=True))
    op.create_index("ix_agent_installations_organization_id", "agent_installations", ["organization_id"])
    op.create_foreign_key(
        "fk_agent_installations_organization",
        "agent_installations",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "agent_execution_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("installation_id", sa.Integer(), nullable=True),
        sa.Column("agent_slug", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("run_id", sa.Integer(), nullable=True),
        sa.Column("generation_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), server_default="success", nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("input_tokens", sa.Integer(), server_default="0", nullable=False),
        sa.Column("output_tokens", sa.Integer(), server_default="0", nullable=False),
        sa.Column("cost_usd", sa.Float(), server_default="0", nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("meta", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["installation_id"], ["agent_installations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["productions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["generation_id"], ["ai_generations.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_execution_logs_slug_created", "agent_execution_logs", ["agent_slug", "created_at"])
    op.create_index("ix_agent_execution_logs_installation", "agent_execution_logs", ["installation_id"])

    op.create_table(
        "agent_memory_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("installation_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("memory_key", sa.String(length=200), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding_id", sa.String(length=128), nullable=True),
        sa.Column("meta", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["installation_id"], ["agent_installations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["productions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_memory_installation_key", "agent_memory_entries", ["installation_id", "memory_key"])

    op.create_table(
        "agent_schedules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("installation_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("cron_expression", sa.String(length=120), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["installation_id"], ["agent_installations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_schedules_next_run", "agent_schedules", ["next_run_at"])

    op.create_table(
        "agent_messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("from_installation_id", sa.Integer(), nullable=True),
        sa.Column("to_installation_id", sa.Integer(), nullable=True),
        sa.Column("from_slug", sa.String(length=64), nullable=False),
        sa.Column("to_slug", sa.String(length=64), nullable=False),
        sa.Column("message_type", sa.String(length=32), server_default="task", nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("status", sa.String(length=32), server_default="pending", nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["from_installation_id"], ["agent_installations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["to_installation_id"], ["agent_installations.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_messages_to_status", "agent_messages", ["to_installation_id", "status"])


def downgrade() -> None:
    op.drop_index("ix_agent_messages_to_status", table_name="agent_messages")
    op.drop_table("agent_messages")
    op.drop_index("ix_agent_schedules_next_run", table_name="agent_schedules")
    op.drop_table("agent_schedules")
    op.drop_index("ix_agent_memory_installation_key", table_name="agent_memory_entries")
    op.drop_table("agent_memory_entries")
    op.drop_index("ix_agent_execution_logs_installation", table_name="agent_execution_logs")
    op.drop_index("ix_agent_execution_logs_slug_created", table_name="agent_execution_logs")
    op.drop_table("agent_execution_logs")
    op.drop_constraint("fk_agent_installations_organization", "agent_installations", type_="foreignkey")
    op.drop_index("ix_agent_installations_organization_id", table_name="agent_installations")
    op.drop_column("agent_installations", "organization_id")
