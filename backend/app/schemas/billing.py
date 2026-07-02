"""Billing Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.monetization import PaymentProvider
from app.models.studio.billing import (
    BillingPaymentStatus,
    OrgInvoiceStatus,
    OrgSubscriptionStatus,
    UsageMeterType,
)
from app.schemas.common import ORMBase


class BillingPlanResponse(ORMBase):
    id: int
    slug: str
    name: str
    description: str | None
    interval: str
    base_amount_cents: int
    currency: str
    included_seats: int
    seat_price_cents: int
    included_ai_credits: int
    included_storage_gb: int
    included_video_minutes: int
    usage_rates: dict


class SubscribeRequest(BaseModel):
    plan_slug: str
    provider: PaymentProvider = PaymentProvider.STRIPE
    seat_quantity: int = Field(default=1, ge=1, le=10_000)
    coupon_code: str | None = None
    country: str = Field(default="US", min_length=2, max_length=2)


class SubscriptionResponse(ORMBase):
    id: int
    organization_id: int
    billing_plan_id: int
    plan_slug: str | None = None
    plan_name: str | None = None
    provider: PaymentProvider
    status: OrgSubscriptionStatus
    seat_quantity: int
    current_period_start: datetime | None
    current_period_end: datetime | None
    cancel_at_period_end: bool
    failed_payment_count: int


class UpdateSubscriptionRequest(BaseModel):
    plan_slug: str | None = None
    seat_quantity: int | None = Field(default=None, ge=1, le=10_000)
    cancel_at_period_end: bool | None = None


class CheckoutResponse(BaseModel):
    payment_id: int
    provider: str
    client_secret: str | None = None
    checkout_url: str | None = None
    razorpay_order_id: str | None = None
    razorpay_key_id: str | None = None
    amount_cents: int
    currency: str


class InvoiceResponse(ORMBase):
    id: int
    invoice_number: str
    status: OrgInvoiceStatus
    subtotal_cents: int
    tax_cents: int
    discount_cents: int
    credit_applied_cents: int
    total_cents: int
    currency: str
    line_items: list
    period_start: datetime | None
    period_end: datetime | None
    paid_at: datetime | None
    pdf_url: str | None
    created_at: datetime | None


class PaymentHistoryResponse(ORMBase):
    id: int
    invoice_id: int | None
    provider: PaymentProvider
    amount_cents: int
    currency: str
    status: BillingPaymentStatus
    refunded_cents: int
    failure_reason: str | None
    created_at: datetime | None
    completed_at: datetime | None


class RefundRequest(BaseModel):
    amount_cents: int | None = Field(default=None, ge=1)
    reason: str | None = Field(default=None, max_length=500)


class RefundResponse(ORMBase):
    id: int
    payment_id: int
    amount_cents: int
    currency: str
    status: str
    external_refund_id: str | None


class CouponValidateRequest(BaseModel):
    code: str
    plan_slug: str | None = None


class CouponValidateResponse(BaseModel):
    valid: bool
    percent_off: float | None = None
    amount_off_cents: int | None = None
    message: str | None = None


class CreditResponse(ORMBase):
    id: int
    amount_cents: int
    balance_cents: int
    currency: str
    reason: str | None
    expires_at: datetime | None


class ApplyCreditRequest(BaseModel):
    amount_cents: int = Field(ge=1)
    reason: str | None = None
    expires_at: datetime | None = None


class UsageSummaryResponse(BaseModel):
    period_key: str
    meters: dict[str, float]
    included: dict[str, float]
    overage: dict[str, float]
    estimated_overage_cents: int


class RecordUsageRequest(BaseModel):
    meter_type: UsageMeterType
    quantity: float = Field(gt=0)
    meta: dict | None = None
