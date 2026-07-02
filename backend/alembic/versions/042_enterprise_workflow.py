"""Enterprise workflow automation — durable logs, triggers, org scope."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "042_enterprise_workflow"
down_revision: Union[str, None] = "041_ai_cost_intelligence"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("workflow_definitions", sa.Column("organization_id", sa.Integer(), nullable=True))
    op.create_index("ix_workflow_definitions_organization_id", "workflow_definitions", ["organization_id"])
    op.create_foreign_key(
        "fk_workflow_definitions_organization",
        "workflow_definitions",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column("workflow_triggers", sa.Column("api_key_hash", sa.String(length=64), nullable=True))
    op.add_column("workflow_triggers", sa.Column("api_key_prefix", sa.String(length=12), nullable=True))
    op.add_column("workflow_triggers", sa.Column("email_token", sa.String(length=64), nullable=True))
    op.create_index("ix_workflow_triggers_api_key_hash", "workflow_triggers", ["api_key_hash"], unique=True)
    op.create_index("ix_workflow_triggers_email_token", "workflow_triggers", ["email_token"], unique=True)

    op.create_table(
        "workflow_run_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False),
        sa.Column("node_id", sa.String(length=64), nullable=True),
        sa.Column("level", sa.String(length=16), server_default="info", nullable=False),
        sa.Column("stage", sa.String(length=64), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("meta", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["run_id"], ["production_pipeline_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_workflow_run_logs_run_id", "workflow_run_logs", ["run_id"])
    op.create_index("ix_workflow_run_logs_created_at", "workflow_run_logs", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_workflow_run_logs_created_at", table_name="workflow_run_logs")
    op.drop_index("ix_workflow_run_logs_run_id", table_name="workflow_run_logs")
    op.drop_table("workflow_run_logs")
    op.drop_index("ix_workflow_triggers_email_token", table_name="workflow_triggers")
    op.drop_index("ix_workflow_triggers_api_key_hash", table_name="workflow_triggers")
    op.drop_column("workflow_triggers", "email_token")
    op.drop_column("workflow_triggers", "api_key_prefix")
    op.drop_column("workflow_triggers", "api_key_hash")
    op.drop_constraint("fk_workflow_definitions_organization", "workflow_definitions", type_="foreignkey")
    op.drop_index("ix_workflow_definitions_organization_id", table_name="workflow_definitions")
    op.drop_column("workflow_definitions", "organization_id")
