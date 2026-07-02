"""Mobile apps — device registration, push tokens, aggregated mobile APIs."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "046_mobile_platform"
down_revision: Union[str, None] = "045_plugin_marketplace"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "mobile_devices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("app_type", sa.String(length=32), nullable=False),
        sa.Column("platform", sa.String(length=16), nullable=False),
        sa.Column("device_token", sa.String(length=512), nullable=False),
        sa.Column("device_name", sa.String(length=200), nullable=True),
        sa.Column("push_enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("meta", sa.dialects.postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "device_token", name="uq_mobile_device_token"),
    )
    op.create_index("ix_mobile_devices_user", "mobile_devices", ["user_id"])
    op.create_index("ix_mobile_devices_app_type", "mobile_devices", ["app_type"])

    op.create_table(
        "mobile_push_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("payload", sa.dialects.postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("status", sa.String(length=32), server_default="queued", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["device_id"], ["mobile_devices.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("mobile_push_log")
    op.drop_table("mobile_devices")
