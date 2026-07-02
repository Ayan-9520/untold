"""Enterprise organization billing orchestration."""

from __future__ import annotations

import json
import logging
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.domain.tenancy.audit import TenantAuditService
from app.domain.tenancy.context import TenantContext
from app.models import User
from app.models.monetization import PaymentProvider
from app.models.studio.billing import (
    BillingCoupon,
    BillingCredit,
    BillingPaymentStatus,
    BillingPlan,
    BillingRefund,
    OrganizationBillingPayment,
    OrganizationInvoice,
    OrganizationSubscription,
    OrgInvoiceStatus,
    OrgSubscriptionStatus,
    RefundStatus,
    TaxRate,
    UsageMeterType,
)
from app.domain.tenancy.enums import OrganizationPlan
from app.models.studio.tenancy import Organization
from app.schemas.billing import (
    BillingPlanResponse,
    CheckoutResponse,
    CouponValidateResponse,
    CreditResponse,
    InvoiceResponse,
    PaymentHistoryResponse,
    RefundResponse,
    SubscribeRequest,
    SubscriptionResponse,
    UpdateSubscriptionRequest,
    UsageSummaryResponse,
)
from app.services.billing.razorpay_adapter import RazorpayBillingAdapter
from app.services.billing.stripe_adapter import StripeBillingAdapter
from app.services.billing.usage_service import UsageMeterService

logger = logging.getLogger("untold.billing")
settings = get_settings()


class EnterpriseBillingService:
    @staticmethod
    def list_plans(db: Session) -> list[BillingPlanResponse]:
        plans = db.query(BillingPlan).filter(BillingPlan.is_active.is_(True)).order_by(BillingPlan.sort_order).all()
        return [BillingPlanResponse.model_validate(p) for p in plans]

    @staticmethod
    def _get_plan(db: Session, slug: str) -> BillingPlan:
        plan = db.query(BillingPlan).filter(BillingPlan.slug == slug, BillingPlan.is_active.is_(True)).first()
        if not plan:
            raise NotFoundError("Billing plan")
        return plan

    @staticmethod
    def _subscription_response(db: Session, sub: OrganizationSubscription) -> SubscriptionResponse:
        plan = db.query(BillingPlan).filter(BillingPlan.id == sub.billing_plan_id).first()
        return SubscriptionResponse(
            id=sub.id,
            organization_id=sub.organization_id,
            billing_plan_id=sub.billing_plan_id,
            plan_slug=plan.slug if plan else None,
            plan_name=plan.name if plan else None,
            provider=sub.provider,
            status=sub.status,
            seat_quantity=sub.seat_quantity,
            current_period_start=sub.current_period_start,
            current_period_end=sub.current_period_end,
            cancel_at_period_end=sub.cancel_at_period_end,
            failed_payment_count=sub.failed_payment_count,
        )

    @staticmethod
    def get_subscription(db: Session, organization_id: int) -> SubscriptionResponse | None:
        sub = db.query(OrganizationSubscription).filter(OrganizationSubscription.organization_id == organization_id).first()
        if not sub:
            return None
        return EnterpriseBillingService._subscription_response(db, sub)

    @staticmethod
    def _calculate_amount_cents(plan: BillingPlan, seats: int, coupon: BillingCoupon | None) -> int:
        extra_seats = max(0, seats - plan.included_seats)
        subtotal = plan.base_amount_cents + extra_seats * plan.seat_price_cents
        if coupon:
            if coupon.percent_off:
                subtotal = int(subtotal * (1 - coupon.percent_off / 100))
            elif coupon.amount_off_cents:
                subtotal = max(0, subtotal - coupon.amount_off_cents)
        return subtotal

    @staticmethod
    def _apply_tax(subtotal_cents: int, country: str, db: Session) -> tuple[int, int | None]:
        tax = db.query(TaxRate).filter(TaxRate.country == country.upper(), TaxRate.is_active.is_(True)).first()
        if not tax:
            return 0, None
        tax_cents = int(subtotal_cents * tax.rate_percent / 100)
        return tax_cents, tax.id

    @staticmethod
    def _apply_credits(db: Session, organization_id: int, total_cents: int) -> tuple[int, int]:
        credits = (
            db.query(BillingCredit)
            .filter(
                BillingCredit.organization_id == organization_id,
                BillingCredit.balance_cents > 0,
            )
            .order_by(BillingCredit.created_at.asc())
            .all()
        )
        remaining = total_cents
        applied = 0
        for credit in credits:
            if remaining <= 0:
                break
            use = min(credit.balance_cents, remaining)
            credit.balance_cents -= use
            remaining -= use
            applied += use
        return applied, remaining

    @staticmethod
    def validate_coupon(db: Session, code: str, plan_slug: str | None, org_id: int) -> CouponValidateResponse:
        coupon = (
            db.query(BillingCoupon)
            .filter(BillingCoupon.code == code.upper(), BillingCoupon.is_active.is_(True))
            .first()
        )
        if not coupon:
            return CouponValidateResponse(valid=False, message="Invalid coupon")
        if coupon.organization_id and coupon.organization_id != org_id:
            return CouponValidateResponse(valid=False, message="Coupon not valid for this organization")
        if coupon.expires_at and coupon.expires_at < datetime.now(timezone.utc):
            return CouponValidateResponse(valid=False, message="Coupon expired")
        if coupon.max_redemptions and coupon.times_redeemed >= coupon.max_redemptions:
            return CouponValidateResponse(valid=False, message="Coupon fully redeemed")
        if coupon.valid_for_plans and plan_slug and plan_slug not in coupon.valid_for_plans:
            return CouponValidateResponse(valid=False, message="Coupon not valid for this plan")
        return CouponValidateResponse(
            valid=True,
            percent_off=coupon.percent_off,
            amount_off_cents=coupon.amount_off_cents,
            message="Coupon applied",
        )

    @staticmethod
    def subscribe(
        db: Session,
        ctx: TenantContext,
        user: User,
        data: SubscribeRequest,
    ) -> tuple[SubscriptionResponse, CheckoutResponse | None]:
        org = ctx.organization
        existing = db.query(OrganizationSubscription).filter(OrganizationSubscription.organization_id == org.id).first()
        if existing and existing.status in (OrgSubscriptionStatus.ACTIVE, OrgSubscriptionStatus.TRIALING):
            raise BadRequestError("Organization already has an active subscription")

        plan = EnterpriseBillingService._get_plan(db, data.plan_slug)
        coupon = None
        if data.coupon_code:
            validation = EnterpriseBillingService.validate_coupon(db, data.coupon_code, plan.slug, org.id)
            if not validation.valid:
                raise BadRequestError(validation.message or "Invalid coupon")
            coupon = db.query(BillingCoupon).filter(BillingCoupon.code == data.coupon_code.upper()).first()

        pre_coupon = plan.base_amount_cents + max(0, data.seat_quantity - plan.included_seats) * plan.seat_price_cents
        subtotal = EnterpriseBillingService._calculate_amount_cents(plan, data.seat_quantity, coupon)
        discount_cents = max(0, pre_coupon - subtotal)
        tax_cents, tax_id = EnterpriseBillingService._apply_tax(subtotal, data.country, db)
        credit_applied, total = EnterpriseBillingService._apply_credits(db, org.id, subtotal + tax_cents)

        now = datetime.now(timezone.utc)
        sub = existing or OrganizationSubscription(
            organization_id=org.id,
            billing_plan_id=plan.id,
            provider=data.provider,
        )
        sub.billing_plan_id = plan.id
        sub.provider = data.provider
        sub.seat_quantity = data.seat_quantity
        sub.status = OrgSubscriptionStatus.TRIALING if plan.base_amount_cents == 0 else OrgSubscriptionStatus.ACTIVE
        sub.trial_end = now + timedelta(days=14) if plan.slug != "studio-free" else None
        sub.current_period_start = now
        sub.current_period_end = now + timedelta(days=30)
        sub.coupon_code = data.coupon_code.upper() if data.coupon_code else None
        if not existing:
            db.add(sub)
        db.flush()

        plan_map = {
            "studio-free": OrganizationPlan.FREE,
            "studio-starter": OrganizationPlan.STARTER,
            "studio-pro": OrganizationPlan.PRO,
            "studio-enterprise": OrganizationPlan.ENTERPRISE,
        }
        org.plan = plan_map.get(plan.slug, OrganizationPlan.FREE)
        org.seat_limit = max(org.seat_limit, data.seat_quantity)

        invoice_number = f"ORG-{org.id}-{now.strftime('%Y%m')}-{secrets.token_hex(3).upper()}"
        line_items = [
            {"description": f"{plan.name} base", "amount_cents": plan.base_amount_cents, "quantity": 1},
        ]
        if data.seat_quantity > plan.included_seats:
            extra = data.seat_quantity - plan.included_seats
            line_items.append(
                {
                    "description": "Additional seats",
                    "amount_cents": plan.seat_price_cents,
                    "quantity": extra,
                }
            )

        invoice = OrganizationInvoice(
            organization_id=org.id,
            subscription_id=sub.id,
            invoice_number=invoice_number,
            status=OrgInvoiceStatus.OPEN if total > 0 else OrgInvoiceStatus.PAID,
            provider=data.provider,
            subtotal_cents=subtotal,
            tax_cents=tax_cents,
            discount_cents=discount_cents,
            credit_applied_cents=credit_applied,
            total_cents=total,
            currency=plan.currency,
            tax_rate_id=tax_id,
            coupon_id=coupon.id if coupon else None,
            line_items=line_items,
            period_start=now,
            period_end=sub.current_period_end,
            due_at=now + timedelta(days=7),
            paid_at=now if total == 0 else None,
        )
        db.add(invoice)
        db.flush()

        checkout: CheckoutResponse | None = None
        if total > 0:
            payment = OrganizationBillingPayment(
                organization_id=org.id,
                invoice_id=invoice.id,
                provider=data.provider,
                amount_cents=total,
                currency=plan.currency,
                status=BillingPaymentStatus.PENDING,
            )
            db.add(payment)
            db.flush()

            if data.provider == PaymentProvider.STRIPE:
                if not sub.external_customer_id:
                    sub.external_customer_id = StripeBillingAdapter.create_customer(user.email, org.name, org.id)
                stripe_sub = StripeBillingAdapter.create_subscription(
                    sub.external_customer_id,
                    plan.stripe_price_id,
                    data.seat_quantity,
                    trial_days=14 if plan.slug != "studio-free" else 0,
                )
                sub.external_subscription_id = stripe_sub.get("id")
                payment.external_order_id = stripe_sub.get("id")
                payment.meta = {"client_secret": stripe_sub.get("client_secret")}
                checkout = CheckoutResponse(
                    payment_id=payment.id,
                    provider="stripe",
                    client_secret=stripe_sub.get("client_secret"),
                    amount_cents=total,
                    currency=plan.currency,
                )
            elif data.provider == PaymentProvider.RAZORPAY:
                order = RazorpayBillingAdapter.create_order(total, plan.currency, org.id, invoice_number)
                payment.external_order_id = order["id"]
                checkout = CheckoutResponse(
                    payment_id=payment.id,
                    provider="razorpay",
                    razorpay_order_id=order["id"],
                    razorpay_key_id=settings.razorpay_key_id,
                    amount_cents=total,
                    currency=plan.currency,
                )
        else:
            sub.status = OrgSubscriptionStatus.ACTIVE

        if coupon:
            coupon.times_redeemed += 1

        UsageMeterService.sync_seats(db, org)
        TenantAuditService.log(
            db,
            organization_id=org.id,
            user_id=user.id,
            action="billing.subscribe",
            resource_type="subscription",
            resource_id=sub.id,
            meta={"plan": plan.slug, "seats": data.seat_quantity},
        )
        db.commit()
        db.refresh(sub)
        return EnterpriseBillingService._subscription_response(db, sub), checkout

    @staticmethod
    def update_subscription(db: Session, ctx: TenantContext, user: User, data: UpdateSubscriptionRequest) -> SubscriptionResponse:
        sub = db.query(OrganizationSubscription).filter(OrganizationSubscription.organization_id == ctx.organization_id).first()
        if not sub:
            raise NotFoundError("Subscription")

        if data.plan_slug:
            plan = EnterpriseBillingService._get_plan(db, data.plan_slug)
            sub.billing_plan_id = plan.id
        if data.seat_quantity is not None:
            sub.seat_quantity = data.seat_quantity
            ctx.organization.seat_limit = max(ctx.organization.seat_limit, data.seat_quantity)
            if sub.external_subscription_id and sub.provider == PaymentProvider.STRIPE:
                StripeBillingAdapter.update_subscription_quantity(sub.external_subscription_id, data.seat_quantity)
        if data.cancel_at_period_end is not None:
            sub.cancel_at_period_end = data.cancel_at_period_end
            if sub.external_subscription_id:
                StripeBillingAdapter.cancel_subscription(sub.external_subscription_id, data.cancel_at_period_end)
            if not data.cancel_at_period_end:
                sub.cancelled_at = None
            elif data.cancel_at_period_end:
                sub.cancelled_at = datetime.now(timezone.utc)

        UsageMeterService.sync_seats(db, ctx.organization)
        TenantAuditService.log(db, organization_id=ctx.organization_id, user_id=user.id, action="billing.subscription.updated")
        db.commit()
        db.refresh(sub)
        return EnterpriseBillingService._subscription_response(db, sub)

    @staticmethod
    def list_invoices(db: Session, organization_id: int) -> list[InvoiceResponse]:
        rows = (
            db.query(OrganizationInvoice)
            .filter(OrganizationInvoice.organization_id == organization_id)
            .order_by(OrganizationInvoice.created_at.desc())
            .limit(100)
            .all()
        )
        return [InvoiceResponse.model_validate(r) for r in rows]

    @staticmethod
    def list_payments(db: Session, organization_id: int) -> list[PaymentHistoryResponse]:
        rows = (
            db.query(OrganizationBillingPayment)
            .filter(OrganizationBillingPayment.organization_id == organization_id)
            .order_by(OrganizationBillingPayment.created_at.desc())
            .limit(100)
            .all()
        )
        return [PaymentHistoryResponse.model_validate(r) for r in rows]

    @staticmethod
    def mark_payment_succeeded(db: Session, payment: OrganizationBillingPayment, external_id: str | None = None) -> None:
        payment.status = BillingPaymentStatus.SUCCEEDED
        payment.external_payment_id = external_id
        payment.completed_at = datetime.now(timezone.utc)
        if payment.invoice_id:
            inv = db.query(OrganizationInvoice).filter(OrganizationInvoice.id == payment.invoice_id).first()
            if inv:
                inv.status = OrgInvoiceStatus.PAID
                inv.paid_at = datetime.now(timezone.utc)
        sub = db.query(OrganizationSubscription).filter(OrganizationSubscription.organization_id == payment.organization_id).first()
        if sub:
            sub.status = OrgSubscriptionStatus.ACTIVE
            sub.failed_payment_count = 0
            sub.next_retry_at = None

    @staticmethod
    def mark_payment_failed(db: Session, payment: OrganizationBillingPayment, reason: str) -> None:
        payment.status = BillingPaymentStatus.FAILED
        payment.failure_reason = reason
        sub = db.query(OrganizationSubscription).filter(OrganizationSubscription.organization_id == payment.organization_id).first()
        if sub:
            sub.failed_payment_count += 1
            sub.status = OrgSubscriptionStatus.PAST_DUE
            sub.next_retry_at = datetime.now(timezone.utc) + timedelta(days=min(sub.failed_payment_count, 5))

    @staticmethod
    def create_refund(
        db: Session,
        ctx: TenantContext,
        user: User,
        payment_id: int,
        amount_cents: int | None,
        reason: str | None,
    ) -> RefundResponse:
        payment = (
            db.query(OrganizationBillingPayment)
            .filter(
                OrganizationBillingPayment.id == payment_id,
                OrganizationBillingPayment.organization_id == ctx.organization_id,
            )
            .first()
        )
        if not payment:
            raise NotFoundError("Payment")
        if payment.status != BillingPaymentStatus.SUCCEEDED:
            raise BadRequestError("Only succeeded payments can be refunded")

        refundable = payment.amount_cents - payment.refunded_cents
        refund_amount = amount_cents or refundable
        if refund_amount > refundable:
            raise BadRequestError("Refund amount exceeds refundable balance")

        external_refund_id = None
        if payment.provider == PaymentProvider.STRIPE and payment.external_payment_id:
            external_refund_id = StripeBillingAdapter.create_refund(payment.external_payment_id, refund_amount)
        elif payment.provider == PaymentProvider.RAZORPAY and payment.external_payment_id:
            external_refund_id = RazorpayBillingAdapter.refund_payment(payment.external_payment_id, refund_amount)

        refund = BillingRefund(
            payment_id=payment.id,
            organization_id=ctx.organization_id,
            amount_cents=refund_amount,
            currency=payment.currency,
            reason=reason,
            status=RefundStatus.SUCCEEDED if external_refund_id else RefundStatus.PENDING,
            external_refund_id=external_refund_id,
            created_by_id=user.id,
        )
        db.add(refund)
        payment.refunded_cents += refund_amount
        if payment.refunded_cents >= payment.amount_cents:
            payment.status = BillingPaymentStatus.REFUNDED
        else:
            payment.status = BillingPaymentStatus.PARTIALLY_REFUNDED

        TenantAuditService.log(
            db,
            organization_id=ctx.organization_id,
            user_id=user.id,
            action="billing.refund",
            resource_type="payment",
            resource_id=payment.id,
            meta={"amount_cents": refund_amount},
        )
        db.commit()
        db.refresh(refund)
        return RefundResponse.model_validate(refund)

    @staticmethod
    def apply_credit(db: Session, ctx: TenantContext, user: User, amount_cents: int, reason: str | None) -> CreditResponse:
        credit = BillingCredit(
            organization_id=ctx.organization_id,
            amount_cents=amount_cents,
            balance_cents=amount_cents,
            currency="usd",
            reason=reason,
            created_by_id=user.id,
        )
        db.add(credit)
        TenantAuditService.log(
            db,
            organization_id=ctx.organization_id,
            user_id=user.id,
            action="billing.credit.applied",
            meta={"amount_cents": amount_cents},
        )
        db.commit()
        db.refresh(credit)
        return CreditResponse.model_validate(credit)

    @staticmethod
    def list_credits(db: Session, organization_id: int) -> list[CreditResponse]:
        rows = (
            db.query(BillingCredit)
            .filter(BillingCredit.organization_id == organization_id, BillingCredit.balance_cents > 0)
            .all()
        )
        return [CreditResponse.model_validate(r) for r in rows]

    @staticmethod
    def usage_summary(db: Session, organization_id: int) -> UsageSummaryResponse:
        sub = db.query(OrganizationSubscription).filter(OrganizationSubscription.organization_id == organization_id).first()
        plan = db.query(BillingPlan).filter(BillingPlan.id == sub.billing_plan_id).first() if sub else None
        org = db.query(Organization).filter(Organization.id == organization_id).first()
        if org:
            UsageMeterService.sync_seats(db, org)
            UsageMeterService.sync_storage_gb(db, org)
            db.flush()
        data = UsageMeterService.summary(db, organization_id, plan)
        return UsageSummaryResponse(**data)

    @staticmethod
    def record_usage(db: Session, organization_id: int, meter_type: UsageMeterType, quantity: float, meta: dict | None) -> None:
        UsageMeterService.record(db, organization_id, meter_type, quantity, meta=meta)
        db.commit()
