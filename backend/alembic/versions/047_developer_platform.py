"""Public developer platform — accounts, sandbox/production API keys."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "047_developer_platform"
down_revision: Union[str, None] = "046_mobile_platform"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "developer_accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("company_name", sa.String(length=200), nullable=True),
        sa.Column("website", sa.String(length=500), nullable=True),
        sa.Column("tier", sa.String(length=32), server_default="free", nullable=False),
        sa.Column("sandbox_enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("meta", sa.dialects.postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_developer_account_user"),
    )
    op.create_index("ix_developer_accounts_user_id", "developer_accounts", ["user_id"])

    op.add_column(
        "studio_api_keys",
        sa.Column("environment", sa.String(length=16), server_default="production", nullable=False),
    )
    op.add_column(
        "api_gateway_usage_logs",
        sa.Column("environment", sa.String(length=16), server_default="production", nullable=False),
    )
    op.create_index("ix_studio_api_keys_environment", "studio_api_keys", ["environment"])


def downgrade() -> None:
    op.drop_index("ix_studio_api_keys_environment", table_name="studio_api_keys")
    op.drop_column("api_gateway_usage_logs", "environment")
    op.drop_column("studio_api_keys", "environment")
    op.drop_table("developer_accounts")
