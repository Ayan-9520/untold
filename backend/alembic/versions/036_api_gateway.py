"""API Gateway — usage logs, webhooks, extended API key fields."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "036_api_gateway"
down_revision: Union[str, None] = "035_plugin_sdk"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("studio_api_keys", sa.Column("rate_limit_tier", sa.String(length=32), server_default="standard", nullable=False))
    op.add_column("studio_api_keys", sa.Column("api_version", sa.String(length=8), server_default="v1", nullable=False))
    op.add_column("studio_api_keys", sa.Column("scopes", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False))
    op.add_column("studio_api_keys", sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("studio_api_keys", sa.Column("total_requests", sa.Integer(), server_default="0", nullable=False))

    op.create_table(
        "api_gateway_usage_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("api_key_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("method", sa.String(length=8), nullable=False),
        sa.Column("path", sa.String(length=500), nullable=False),
        sa.Column("api_version", sa.String(length=8), server_default="v1", nullable=False),
        sa.Column("protocol", sa.String(length=16), server_default="rest", nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("request_id", sa.String(length=36), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["api_key_id"], ["studio_api_keys.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_api_gateway_usage_logs_api_key_id", "api_gateway_usage_logs", ["api_key_id"])
    op.create_index("ix_api_gateway_usage_logs_created_at", "api_gateway_usage_logs", ["created_at"])
    op.create_index("ix_api_gateway_usage_logs_path", "api_gateway_usage_logs", ["path"])

    op.create_table(
        "api_gateway_webhooks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("api_key_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("url", sa.String(length=2000), nullable=False),
        sa.Column("secret", sa.String(length=128), nullable=False),
        sa.Column("events", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("last_triggered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["api_key_id"], ["studio_api_keys.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_api_gateway_webhooks_user_id", "api_gateway_webhooks", ["user_id"])

    op.create_table(
        "api_gateway_webhook_deliveries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("webhook_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(length=32), server_default="pending", nullable=False),
        sa.Column("http_status", sa.Integer(), nullable=True),
        sa.Column("response_body", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("attempts", sa.Integer(), server_default="0", nullable=False),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["webhook_id"], ["api_gateway_webhooks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_api_gateway_webhook_deliveries_webhook_id", "api_gateway_webhook_deliveries", ["webhook_id"])


def downgrade() -> None:
    op.drop_table("api_gateway_webhook_deliveries")
    op.drop_table("api_gateway_webhooks")
    op.drop_table("api_gateway_usage_logs")
    op.drop_column("studio_api_keys", "total_requests")
    op.drop_column("studio_api_keys", "expires_at")
    op.drop_column("studio_api_keys", "scopes")
    op.drop_column("studio_api_keys", "api_version")
    op.drop_column("studio_api_keys", "rate_limit_tier")
