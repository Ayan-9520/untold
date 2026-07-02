"""Enterprise billing API — org subscriptions, invoices, usage."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_studio_user
from app.core.tenant_deps import get_tenant_context, require_org_permission
from app.db.session import get_db
from app.domain.tenancy.context import TenantContext
from app.models import User
from app.schemas.billing import (
    ApplyCreditRequest,
    CouponValidateRequest,
    CouponValidateResponse,
    CreditResponse,
    InvoiceResponse,
    PaymentHistoryResponse,
    RecordUsageRequest,
    RefundRequest,
    RefundResponse,
    SubscribeRequest,
    SubscriptionResponse,
    UpdateSubscriptionRequest,
    UsageSummaryResponse,
)
from app.services.billing.enterprise_billing_service import EnterpriseBillingService

router = APIRouter(prefix="/studio/billing", tags=["Billing"])


@router.get("/plans", response_model=list)
def list_plans(db: Session = Depends(get_db)):
    return EnterpriseBillingService.list_plans(db)


@router.get("/subscription", response_model=SubscriptionResponse | None)
def get_subscription(
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(require_org_permission("org.billing")),
):
    return EnterpriseBillingService.get_subscription(db, ctx.organization_id)


@router.post("/subscribe", response_model=dict)
def subscribe(
    data: SubscribeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    ctx: TenantContext = Depends(require_org_permission("org.billing")),
):
    sub, checkout = EnterpriseBillingService.subscribe(db, ctx, user, data)
    return {"subscription": sub, "checkout": checkout}


@router.patch("/subscription", response_model=SubscriptionResponse)
def update_subscription(
    data: UpdateSubscriptionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    ctx: TenantContext = Depends(require_org_permission("org.billing")),
):
    return EnterpriseBillingService.update_subscription(db, ctx, user, data)


@router.get("/invoices", response_model=list[InvoiceResponse])
def list_invoices(
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(require_org_permission("org.billing")),
):
    return EnterpriseBillingService.list_invoices(db, ctx.organization_id)


@router.get("/payments", response_model=list[PaymentHistoryResponse])
def payment_history(
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(require_org_permission("org.billing")),
):
    return EnterpriseBillingService.list_payments(db, ctx.organization_id)


@router.post("/payments/{payment_id}/refund", response_model=RefundResponse)
def refund_payment(
    payment_id: int,
    data: RefundRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    ctx: TenantContext = Depends(require_org_permission("org.billing")),
):
    return EnterpriseBillingService.create_refund(db, ctx, user, payment_id, data.amount_cents, data.reason)


@router.post("/coupons/validate", response_model=CouponValidateResponse)
def validate_coupon(
    data: CouponValidateRequest,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    return EnterpriseBillingService.validate_coupon(db, data.code, data.plan_slug, ctx.organization_id)


@router.get("/credits", response_model=list[CreditResponse])
def list_credits(
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(require_org_permission("org.billing")),
):
    return EnterpriseBillingService.list_credits(db, ctx.organization_id)


@router.post("/credits", response_model=CreditResponse, status_code=201)
def apply_credit(
    data: ApplyCreditRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    ctx: TenantContext = Depends(require_org_permission("org.billing")),
):
    return EnterpriseBillingService.apply_credit(db, ctx, user, data.amount_cents, data.reason)


@router.get("/usage", response_model=UsageSummaryResponse)
def usage_summary(
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(require_org_permission("org.read")),
):
    return EnterpriseBillingService.usage_summary(db, ctx.organization_id)


@router.post("/usage", status_code=204)
def record_usage(
    data: RecordUsageRequest,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(require_org_permission("org.billing")),
):
    EnterpriseBillingService.record_usage(db, ctx.organization_id, data.meter_type, data.quantity, data.meta)
