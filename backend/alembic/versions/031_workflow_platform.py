"""Workflow platform — definitions, versions, triggers, graph execution."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "031_workflow_platform"
down_revision: Union[str, None] = "030_ai_generation_telemetry"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "workflow_definitions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("is_template", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_system", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("status", sa.String(length=32), server_default="draft", nullable=False),
        sa.Column("current_version_id", sa.Integer(), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["productions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_workflow_definitions_project_id", "workflow_definitions", ["project_id"])
    op.create_index("ix_workflow_definitions_is_template", "workflow_definitions", ["is_template"])

    op.create_table(
        "workflow_definition_versions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("definition_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("graph", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("changelog", sa.String(length=500), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["definition_id"], ["workflow_definitions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("definition_id", "version", name="uq_workflow_definition_version"),
    )
    op.create_index("ix_workflow_definition_versions_definition_id", "workflow_definition_versions", ["definition_id"])

    op.create_table(
        "workflow_triggers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("definition_id", sa.Integer(), nullable=False),
        sa.Column("version_id", sa.Integer(), nullable=True),
        sa.Column("trigger_type", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("webhook_secret", sa.String(length=64), nullable=True),
        sa.Column("cron_expression", sa.String(length=120), nullable=True),
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["definition_id"], ["workflow_definitions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["version_id"], ["workflow_definition_versions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_workflow_triggers_definition_id", "workflow_triggers", ["definition_id"])
    op.create_index("ix_workflow_triggers_trigger_type", "workflow_triggers", ["trigger_type"])
    op.create_index("ix_workflow_triggers_webhook_secret", "workflow_triggers", ["webhook_secret"], unique=True)

    op.add_column("production_pipeline_runs", sa.Column("workflow_definition_id", sa.Integer(), nullable=True))
    op.add_column("production_pipeline_runs", sa.Column("workflow_version_id", sa.Integer(), nullable=True))
    op.add_column("production_pipeline_runs", sa.Column("workflow_trigger_id", sa.Integer(), nullable=True))
    op.add_column("production_pipeline_runs", sa.Column("trigger_type", sa.String(length=32), nullable=True))
    op.add_column("production_pipeline_runs", sa.Column("graph_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("production_pipeline_runs", sa.Column("node_executions", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("production_pipeline_runs", sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key(
        "fk_pipeline_runs_workflow_definition",
        "production_pipeline_runs",
        "workflow_definitions",
        ["workflow_definition_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_pipeline_runs_workflow_version",
        "production_pipeline_runs",
        "workflow_definition_versions",
        ["workflow_version_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_pipeline_runs_workflow_trigger",
        "production_pipeline_runs",
        "workflow_triggers",
        ["workflow_trigger_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_foreign_key(
        "fk_workflow_definitions_current_version",
        "workflow_definitions",
        "workflow_definition_versions",
        ["current_version_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_workflow_definitions_current_version", "workflow_definitions", type_="foreignkey")
    op.drop_constraint("fk_pipeline_runs_workflow_trigger", "production_pipeline_runs", type_="foreignkey")
    op.drop_constraint("fk_pipeline_runs_workflow_version", "production_pipeline_runs", type_="foreignkey")
    op.drop_constraint("fk_pipeline_runs_workflow_definition", "production_pipeline_runs", type_="foreignkey")
    op.drop_column("production_pipeline_runs", "scheduled_at")
    op.drop_column("production_pipeline_runs", "node_executions")
    op.drop_column("production_pipeline_runs", "graph_snapshot")
    op.drop_column("production_pipeline_runs", "trigger_type")
    op.drop_column("production_pipeline_runs", "workflow_trigger_id")
    op.drop_column("production_pipeline_runs", "workflow_version_id")
    op.drop_column("production_pipeline_runs", "workflow_definition_id")
    op.drop_table("workflow_triggers")
    op.drop_table("workflow_definition_versions")
    op.drop_table("workflow_definitions")
