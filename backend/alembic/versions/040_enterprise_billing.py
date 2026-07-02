"""Enterprise billing — org subscriptions, usage meters, invoices."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "040_enterprise_billing"
down_revision: Union[str, None] = "039_multi_tenant_saas"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _pg_enum(name: str, *values: str) -> postgresql.ENUM:
    enum_type = postgresql.ENUM(*values, name=name)
    enum_type.create(op.get_bind(), checkfirst=True)
    return postgresql.ENUM(*values, name=name, create_type=False)


def upgrade() -> None:
    paymentprovider = postgresql.ENUM("stripe", "razorpay", "manual", name="paymentprovider", create_type=False)
    plan_interval = _pg_enum("billingplaninterval", "month", "year")
    sub_status = _pg_enum(
        "orgsubscriptionstatus", "trialing", "active", "past_due", "cancelled", "unpaid"
    )
    inv_status = _pg_enum("orginvoicestatus", "draft", "open", "paid", "void", "uncollectible")
    meter_type = _pg_enum("usagemetertype", "seats", "ai_credits", "storage_gb", "video_minutes")
    pay_status = _pg_enum(
        "billingpaymentstatus", "pending", "succeeded", "failed", "refunded", "partially_refunded"
    )
    refund_status = _pg_enum("refundstatus", "pending", "succeeded", "failed")

    op.create_table(
        "billing_plans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("interval", plan_interval, server_default="month", nullable=False),
        sa.Column("base_amount_cents", sa.Integer(), server_default="0", nullable=False),
        sa.Column("currency", sa.String(length=10), server_default="usd", nullable=False),
        sa.Column("included_seats", sa.Integer(), server_default="3", nullable=False),
        sa.Column("seat_price_cents", sa.Integer(), server_default="0", nullable=False),
        sa.Column("included_ai_credits", sa.Integer(), server_default="100", nullable=False),
        sa.Column("included_storage_gb", sa.Integer(), server_default="5", nullable=False),
        sa.Column("included_video_minutes", sa.Integer(), server_default="60", nullable=False),
        sa.Column("usage_rates", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("stripe_price_id", sa.String(length=255), nullable=True),
        sa.Column("stripe_product_id", sa.String(length=255), nullable=True),
        sa.Column("razorpay_plan_id", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    op.create_table(
        "billing_tax_rates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("country", sa.String(length=2), nullable=False),
        sa.Column("region", sa.String(length=64), nullable=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("rate_percent", sa.Float(), nullable=False),
        sa.Column("inclusive", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("stripe_tax_rate_id", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "billing_coupons",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("percent_off", sa.Float(), nullable=True),
        sa.Column("amount_off_cents", sa.Integer(), nullable=True),
        sa.Column("currency", sa.String(length=10), server_default="usd", nullable=False),
        sa.Column("max_redemptions", sa.Integer(), nullable=True),
        sa.Column("times_redeemed", sa.Integer(), server_default="0", nullable=False),
        sa.Column("valid_for_plans", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.create_table(
        "organization_subscriptions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("billing_plan_id", sa.Integer(), nullable=False),
        sa.Column("provider", paymentprovider, nullable=False),
        sa.Column("status", sub_status, server_default="trialing", nullable=False),
        sa.Column("seat_quantity", sa.Integer(), server_default="1", nullable=False),
        sa.Column("external_customer_id", sa.String(length=255), nullable=True),
        sa.Column("external_subscription_id", sa.String(length=255), nullable=True),
        sa.Column("coupon_code", sa.String(length=64), nullable=True),
        sa.Column("trial_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancel_at_period_end", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_payment_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("next_retry_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("meta", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["billing_plan_id"], ["billing_plans.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id"),
    )

    op.create_table(
        "billing_credits",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("balance_cents", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=10), server_default="usd", nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "organization_invoices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("subscription_id", sa.Integer(), nullable=True),
        sa.Column("invoice_number", sa.String(length=64), nullable=False),
        sa.Column("status", inv_status, server_default="draft", nullable=False),
        sa.Column("provider", paymentprovider, nullable=True),
        sa.Column("external_invoice_id", sa.String(length=255), nullable=True),
        sa.Column("subtotal_cents", sa.Integer(), server_default="0", nullable=False),
        sa.Column("tax_cents", sa.Integer(), server_default="0", nullable=False),
        sa.Column("discount_cents", sa.Integer(), server_default="0", nullable=False),
        sa.Column("credit_applied_cents", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_cents", sa.Integer(), server_default="0", nullable=False),
        sa.Column("currency", sa.String(length=10), server_default="usd", nullable=False),
        sa.Column("tax_rate_id", sa.Integer(), nullable=True),
        sa.Column("coupon_id", sa.Integer(), nullable=True),
        sa.Column("line_items", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("pdf_url", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["coupon_id"], ["billing_coupons.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["subscription_id"], ["organization_subscriptions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tax_rate_id"], ["billing_tax_rates.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("invoice_number"),
    )

    op.create_table(
        "organization_billing_payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("invoice_id", sa.Integer(), nullable=True),
        sa.Column("provider", paymentprovider, nullable=False),
        sa.Column("external_payment_id", sa.String(length=255), nullable=True),
        sa.Column("external_order_id", sa.String(length=255), nullable=True),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=10), server_default="usd", nullable=False),
        sa.Column("status", pay_status, server_default="pending", nullable=False),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("refunded_cents", sa.Integer(), server_default="0", nullable=False),
        sa.Column("meta", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["invoice_id"], ["organization_invoices.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "billing_refunds",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("payment_id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=10), server_default="usd", nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=True),
        sa.Column("status", refund_status, server_default="pending", nullable=False),
        sa.Column("external_refund_id", sa.String(length=255), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["payment_id"], ["organization_billing_payments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "usage_meter_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("meter_type", meter_type, nullable=False),
        sa.Column("quantity", sa.Float(), server_default="0", nullable=False),
        sa.Column("period_key", sa.String(length=16), nullable=False),
        sa.Column("meta", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "meter_type", "period_key", name="uq_usage_meter_org_type_period"),
    )

    op.create_table(
        "billing_webhook_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("provider", paymentprovider, nullable=False),
        sa.Column("event_id", sa.String(length=255), nullable=False),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("processed", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider", "event_id", name="uq_billing_webhook_provider_event"),
    )

    # Seed SaaS plans
    op.execute(
        """
        INSERT INTO billing_plans (slug, name, description, base_amount_cents, currency,
            included_seats, seat_price_cents, included_ai_credits, included_storage_gb,
            included_video_minutes, usage_rates, sort_order)
        VALUES
        ('studio-free', 'Studio Free', 'Trial / small teams', 0, 'usd', 3, 0, 100, 5, 60,
            '{"ai_credits": 10, "storage_gb": 50, "video_minutes": 5}', 0),
        ('studio-starter', 'Studio Starter', 'Growing productions', 4900, 'usd', 10, 1500, 1000, 50, 600,
            '{"ai_credits": 5, "storage_gb": 100, "video_minutes": 10}', 1),
        ('studio-pro', 'Studio Pro', 'Professional studio', 19900, 'usd', 50, 1200, 10000, 500, 6000,
            '{"ai_credits": 3, "storage_gb": 50, "video_minutes": 8}', 2),
        ('studio-enterprise', 'Studio Enterprise', 'Custom limits', 0, 'usd', 1000, 0, 1000000, 10000, 100000,
            '{"ai_credits": 2, "storage_gb": 25, "video_minutes": 5}', 3)
        ON CONFLICT (slug) DO NOTHING
        """
    )

    op.execute(
        """
        INSERT INTO billing_tax_rates (country, name, rate_percent, inclusive)
        SELECT 'US', 'US Sales Tax (avg)', 8.0, false
        WHERE NOT EXISTS (SELECT 1 FROM billing_tax_rates WHERE country = 'US' AND name = 'US Sales Tax (avg)')
        """
    )
    op.execute(
        """
        INSERT INTO billing_tax_rates (country, name, rate_percent, inclusive)
        SELECT 'IN', 'India GST', 18.0, false
        WHERE NOT EXISTS (SELECT 1 FROM billing_tax_rates WHERE country = 'IN')
        """
    )
    op.execute(
        """
        INSERT INTO billing_tax_rates (country, name, rate_percent, inclusive)
        SELECT 'GB', 'UK VAT', 20.0, false
        WHERE NOT EXISTS (SELECT 1 FROM billing_tax_rates WHERE country = 'GB')
        """
    )


def downgrade() -> None:
    op.drop_table("billing_webhook_events")
    op.drop_table("usage_meter_records")
    op.drop_table("billing_refunds")
    op.drop_table("organization_billing_payments")
    op.drop_table("organization_invoices")
    op.drop_table("billing_credits")
    op.drop_table("organization_subscriptions")
    op.drop_table("billing_coupons")
    op.drop_table("billing_tax_rates")
    op.drop_table("billing_plans")
    for name in (
        "refundstatus",
        "billingpaymentstatus",
        "usagemetertype",
        "orginvoicestatus",
        "orgsubscriptionstatus",
        "billingplaninterval",
    ):
        sa.Enum(name=name).drop(op.get_bind(), checkfirst=True)
