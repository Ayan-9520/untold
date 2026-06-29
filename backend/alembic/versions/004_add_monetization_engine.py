"""Add monetization engine tables and video access columns."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004_add_monetization_engine"
down_revision: Union[str, None] = "003_add_live_engine"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    paymentprovider = sa.Enum("stripe", "razorpay", "manual", name="paymentprovider")
    paymentstatus = sa.Enum("pending", "completed", "failed", "refunded", name="paymentstatus")
    invoicestatus = sa.Enum("draft", "paid", "void", name="invoicestatus")
    accesstier = sa.Enum("free", "premium", "vip", name="accesstier")

    paymentprovider.create(op.get_bind(), checkfirst=True)
    paymentstatus.create(op.get_bind(), checkfirst=True)
    invoicestatus.create(op.get_bind(), checkfirst=True)
    accesstier.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "subscription_plans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("tier", sa.Enum("free", "premium", "vip", name="subscriptionplan", create_type=False), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("prices_json", sa.Text(), nullable=False),
        sa.Column("features_json", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_subscription_plans_slug"), "subscription_plans", ["slug"], unique=True)

    op.add_column("subscriptions", sa.Column("plan_catalog_id", sa.Integer(), nullable=True))
    op.add_column("subscriptions", sa.Column("payment_provider", sa.String(length=20), nullable=True))
    op.add_column("subscriptions", sa.Column("external_subscription_id", sa.String(length=255), nullable=True))
    op.add_column("subscriptions", sa.Column("currency", sa.String(length=10), nullable=True))
    op.add_column("subscriptions", sa.Column("region", sa.String(length=50), nullable=True))

    op.add_column("videos", sa.Column("stream_key", sa.String(length=500), nullable=True))
    op.add_column("videos", sa.Column("hls_url", sa.String(length=1000), nullable=True))
    op.add_column("videos", sa.Column("access_tier", sa.String(length=20), server_default="free", nullable=False))
    op.create_index(op.f("ix_videos_access_tier"), "videos", ["access_tier"], unique=False)

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("subscription_id", sa.Integer(), nullable=True),
        sa.Column("provider", paymentprovider, nullable=False),
        sa.Column("external_payment_id", sa.String(length=255), nullable=True),
        sa.Column("external_order_id", sa.String(length=255), nullable=True),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("status", paymentstatus, nullable=False),
        sa.Column("plan_slug", sa.String(length=50), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["subscription_id"], ["subscriptions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("payment_id", sa.Integer(), nullable=True),
        sa.Column("invoice_number", sa.String(length=50), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("status", invoicestatus, nullable=False),
        sa.Column("pdf_url", sa.String(length=1000), nullable=True),
        sa.Column("issued_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["payment_id"], ["payments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("invoice_number"),
        sa.UniqueConstraint("payment_id"),
    )

    op.create_table(
        "watch_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("video_id", sa.Integer(), nullable=False),
        sa.Column("watched_seconds", sa.Integer(), server_default="0", nullable=False),
        sa.Column("completed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("watched_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["video_id"], ["videos.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "video_progress",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("video_id", sa.Integer(), nullable=False),
        sa.Column("position_seconds", sa.Integer(), server_default="0", nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("progress_percent", sa.Float(), server_default="0", nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["video_id"], ["videos.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "video_id", name="uq_video_progress_user_video"),
    )

    op.create_table(
        "video_access_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("video_id", sa.Integer(), nullable=False),
        sa.Column("access_granted", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("access_tier_required", sa.String(length=20), nullable=True),
        sa.Column("user_tier", sa.String(length=20), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["video_id"], ["videos.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "magazines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("issue_slug", sa.String(length=200), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("quarter", sa.String(length=20), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("access_tier", accesstier, nullable=False),
        sa.Column("prices_json", sa.Text(), nullable=True),
        sa.Column("pdf_storage_key", sa.String(length=500), nullable=True),
        sa.Column("cover_image_url", sa.String(length=1000), nullable=True),
        sa.Column("is_published", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_magazines_issue_slug"), "magazines", ["issue_slug"], unique=True)

    op.create_table(
        "magazine_downloads",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("magazine_id", sa.Integer(), nullable=False),
        sa.Column("download_url", sa.String(length=1000), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("downloaded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["magazine_id"], ["magazines.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("magazine_downloads")
    op.drop_table("magazines")
    op.drop_table("video_access_logs")
    op.drop_table("video_progress")
    op.drop_table("watch_history")
    op.drop_table("invoices")
    op.drop_table("payments")
    op.drop_column("videos", "access_tier")
    op.drop_column("videos", "hls_url")
    op.drop_column("videos", "stream_key")
    op.drop_column("subscriptions", "region")
    op.drop_column("subscriptions", "currency")
    op.drop_column("subscriptions", "external_subscription_id")
    op.drop_column("subscriptions", "payment_provider")
    op.drop_column("subscriptions", "plan_catalog_id")
    op.drop_table("subscription_plans")

    sa.Enum(name="accesstier").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="invoicestatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="paymentstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="paymentprovider").drop(op.get_bind(), checkfirst=True)
