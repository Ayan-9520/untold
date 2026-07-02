"""Enterprise billing — org subscriptions, invoices, usage, credits."""

from __future__ import annotations

from datetime import datetime
import enum

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, StrEnum
from app.models.monetization import PaymentProvider


class BillingPlanInterval(str, enum.Enum):
    MONTH = "month"
    YEAR = "year"


class OrgSubscriptionStatus(str, enum.Enum):
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    UNPAID = "unpaid"


class OrgInvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    VOID = "void"
    UNCOLLECTIBLE = "uncollectible"


class UsageMeterType(str, enum.Enum):
    SEATS = "seats"
    AI_CREDITS = "ai_credits"
    STORAGE_GB = "storage_gb"
    VIDEO_MINUTES = "video_minutes"


class BillingPaymentStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class RefundStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class BillingPlan(Base):
    """SaaS subscription plan for organizations."""

    __tablename__ = "billing_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    interval: Mapped[BillingPlanInterval] = mapped_column(
        StrEnum(BillingPlanInterval), default=BillingPlanInterval.MONTH, nullable=False
    )
    base_amount_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="usd", nullable=False)
    included_seats: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    seat_price_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    included_ai_credits: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    included_storage_gb: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    included_video_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    usage_rates: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    stripe_price_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_product_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    razorpay_plan_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())


class OrganizationSubscription(Base):
    __tablename__ = "organization_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    billing_plan_id: Mapped[int] = mapped_column(ForeignKey("billing_plans.id"), nullable=False, index=True)
    provider: Mapped[PaymentProvider] = mapped_column(StrEnum(PaymentProvider), nullable=False)
    status: Mapped[OrgSubscriptionStatus] = mapped_column(
        StrEnum(OrgSubscriptionStatus), default=OrgSubscriptionStatus.TRIALING, nullable=False, index=True
    )
    seat_quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    external_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    external_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    coupon_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    trial_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_payment_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    next_retry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    plan: Mapped["BillingPlan"] = relationship()


class TaxRate(Base):
    __tablename__ = "billing_tax_rates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    region: Mapped[str | None] = mapped_column(String(64), nullable=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    rate_percent: Mapped[float] = mapped_column(Float, nullable=False)
    inclusive: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    stripe_tax_rate_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class BillingCoupon(Base):
    __tablename__ = "billing_coupons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=True
    )
    percent_off: Mapped[float | None] = mapped_column(Float, nullable=True)
    amount_off_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="usd", nullable=False)
    max_redemptions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    times_redeemed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    valid_for_plans: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BillingCredit(Base):
    __tablename__ = "billing_credits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    balance_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="usd", nullable=False)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())


class OrganizationInvoice(Base):
    __tablename__ = "organization_invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    subscription_id: Mapped[int | None] = mapped_column(
        ForeignKey("organization_subscriptions.id", ondelete="SET NULL"), nullable=True
    )
    invoice_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    status: Mapped[OrgInvoiceStatus] = mapped_column(
        StrEnum(OrgInvoiceStatus), default=OrgInvoiceStatus.DRAFT, nullable=False, index=True
    )
    provider: Mapped[PaymentProvider | None] = mapped_column(StrEnum(PaymentProvider), nullable=True)
    external_invoice_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    subtotal_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tax_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    discount_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    credit_applied_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="usd", nullable=False)
    tax_rate_id: Mapped[int | None] = mapped_column(ForeignKey("billing_tax_rates.id"), nullable=True)
    coupon_id: Mapped[int | None] = mapped_column(ForeignKey("billing_coupons.id"), nullable=True)
    line_items: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    pdf_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    payments: Mapped[list["OrganizationBillingPayment"]] = relationship(back_populates="invoice")


class OrganizationBillingPayment(Base):
    __tablename__ = "organization_billing_payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    invoice_id: Mapped[int | None] = mapped_column(
        ForeignKey("organization_invoices.id", ondelete="SET NULL"), index=True, nullable=True
    )
    provider: Mapped[PaymentProvider] = mapped_column(StrEnum(PaymentProvider), nullable=False)
    external_payment_id: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    external_order_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="usd", nullable=False)
    status: Mapped[BillingPaymentStatus] = mapped_column(
        StrEnum(BillingPaymentStatus), default=BillingPaymentStatus.PENDING, nullable=False, index=True
    )
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    refunded_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    invoice: Mapped[OrganizationInvoice | None] = relationship(back_populates="payments")
    refunds: Mapped[list["BillingRefund"]] = relationship(back_populates="payment")


class BillingRefund(Base):
    __tablename__ = "billing_refunds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    payment_id: Mapped[int] = mapped_column(
        ForeignKey("organization_billing_payments.id", ondelete="CASCADE"), index=True, nullable=False
    )
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="usd", nullable=False)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[RefundStatus] = mapped_column(
        StrEnum(RefundStatus), default=RefundStatus.PENDING, nullable=False
    )
    external_refund_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    payment: Mapped[OrganizationBillingPayment] = relationship(back_populates="refunds")


class UsageMeterRecord(Base):
    __tablename__ = "usage_meter_records"
    __table_args__ = (
        UniqueConstraint(
            "organization_id", "meter_type", "period_key", name="uq_usage_meter_org_type_period"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    meter_type: Mapped[UsageMeterType] = mapped_column(StrEnum(UsageMeterType), nullable=False, index=True)
    quantity: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    period_key: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class BillingWebhookEvent(Base):
    __tablename__ = "billing_webhook_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider: Mapped[PaymentProvider] = mapped_column(StrEnum(PaymentProvider), nullable=False, index=True)
    event_id: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str] = mapped_column(String(120), nullable=False)
    organization_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("provider", "event_id", name="uq_billing_webhook_provider_event"),)
