"""AI cost optimization — migration 033."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "033_ai_cost_optimization"
down_revision: Union[str, None] = "032_agent_marketplace"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_cost_budgets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("scope_type", sa.String(length=16), nullable=False),
        sa.Column("scope_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("monthly_limit_usd", sa.Numeric(12, 2), nullable=False),
        sa.Column("alert_threshold_pct", sa.Integer(), server_default="80", nullable=False),
        sa.Column("hard_limit", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_cost_budgets_scope", "ai_cost_budgets", ["scope_type", "scope_id"])

    op.create_table(
        "ai_cost_alerts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("budget_id", sa.Integer(), nullable=False),
        sa.Column("alert_type", sa.String(length=32), nullable=False),
        sa.Column("threshold_pct", sa.Integer(), nullable=False),
        sa.Column("spend_usd", sa.Numeric(12, 4), nullable=False),
        sa.Column("limit_usd", sa.Numeric(12, 2), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("acknowledged", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["budget_id"], ["ai_cost_budgets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_cost_alerts_budget_id", "ai_cost_alerts", ["budget_id"])

    op.create_table(
        "ai_model_policies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("module", sa.String(length=64), nullable=False),
        sa.Column("selection_mode", sa.String(length=32), server_default="auto", nullable=False),
        sa.Column("primary_model", sa.String(length=128), nullable=True),
        sa.Column("primary_provider", sa.String(length=64), nullable=True),
        sa.Column("fallback_chain", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("max_cost_per_request_usd", sa.Numeric(10, 4), nullable=True),
        sa.Column("cache_enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("cache_ttl_hours", sa.Integer(), server_default="24", nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("module", name="uq_ai_model_policy_module"),
    )

    op.create_table(
        "ai_response_cache",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cache_key", sa.String(length=64), nullable=False),
        sa.Column("module", sa.String(length=64), nullable=False),
        sa.Column("prompt_hash", sa.String(length=64), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=True),
        sa.Column("provider", sa.String(length=64), nullable=True),
        sa.Column("response_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("hit_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("cost_saved_usd", sa.Numeric(12, 6), server_default="0", nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cache_key", name="uq_ai_response_cache_key"),
    )
    op.create_index("ix_ai_response_cache_module", "ai_response_cache", ["module"])
    op.create_index("ix_ai_response_cache_expires_at", "ai_response_cache", ["expires_at"])

    op.create_table(
        "ai_monthly_cost_reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("scope_type", sa.String(length=16), server_default="global", nullable=False),
        sa.Column("scope_id", sa.Integer(), nullable=True),
        sa.Column("report_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("generated_by_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["generated_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("year", "month", "scope_type", "scope_id", name="uq_ai_monthly_cost_report"),
    )


def downgrade() -> None:
    op.drop_table("ai_monthly_cost_reports")
    op.drop_table("ai_response_cache")
    op.drop_table("ai_model_policies")
    op.drop_table("ai_cost_alerts")
    op.drop_table("ai_cost_budgets")
