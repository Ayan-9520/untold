"""Billing webhook handling — idempotent Stripe/Razorpay events."""

from __future__ import annotations

import hashlib
import json
import logging

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.monetization import PaymentProvider
from app.models.studio.billing import (
    BillingPaymentStatus,
    BillingWebhookEvent,
    OrganizationBillingPayment,
    OrganizationSubscription,
)
from app.services.billing.enterprise_billing_service import EnterpriseBillingService
from app.services.payment_service import PaymentService

logger = logging.getLogger("untold.billing.webhooks")
settings = get_settings()


class BillingWebhookService:
    @staticmethod
    def _record_event(
        db: Session,
        provider: PaymentProvider,
        event_id: str,
        event_type: str,
        payload: dict,
        organization_id: int | None = None,
    ) -> BillingWebhookEvent | None:
        payload_hash = hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()
        existing = (
            db.query(BillingWebhookEvent)
            .filter(BillingWebhookEvent.provider == provider, BillingWebhookEvent.event_id == event_id)
            .first()
        )
        if existing:
            return None
        row = BillingWebhookEvent(
            provider=provider,
            event_id=event_id,
            event_type=event_type,
            organization_id=organization_id,
            payload_hash=payload_hash,
            processed=False,
        )
        db.add(row)
        db.flush()
        return row

    @staticmethod
    def handle_stripe(db: Session, payload: bytes, signature: str | None) -> dict:
        # Consumer OTT payments (legacy)
        consumer_result = PaymentService.handle_stripe_webhook(db, payload, signature)

        if settings.stripe_webhook_secret and settings.stripe_secret_key:
            import stripe

            stripe.api_key = settings.stripe_secret_key
            event = stripe.Webhook.construct_event(payload, signature, settings.stripe_webhook_secret)
        elif settings.is_production:
            from app.core.exceptions import UnauthorizedError

            raise UnauthorizedError("Stripe webhook signature verification is required in production")
        else:
            if not signature:
                from app.core.exceptions import UnauthorizedError

                raise UnauthorizedError("Stripe webhook signature required")
            event = json.loads(payload)

        event_id = event.get("id", hashlib.sha256(payload).hexdigest()[:32])
        event_type = event.get("type", "unknown")
        row = BillingWebhookService._record_event(db, PaymentProvider.STRIPE, event_id, event_type, event)
        if not row:
            return {"status": "duplicate", **consumer_result}

        try:
            BillingWebhookService._process_stripe_event(db, event)
            row.processed = True
            db.commit()
        except Exception as exc:
            logger.exception("Stripe billing webhook failed: %s", exc)
            row.error_message = str(exc)[:500]
            db.commit()
            raise
        return {"status": "ok"}

    @staticmethod
    def _process_stripe_event(db: Session, event: dict) -> None:
        etype = event.get("type")
        obj = event.get("data", {}).get("object", {})

        if etype == "invoice.payment_succeeded":
            org_id = obj.get("metadata", {}).get("organization_id")
            sub_id = obj.get("subscription")
            if sub_id:
                sub = (
                    db.query(OrganizationSubscription)
                    .filter(OrganizationSubscription.external_subscription_id == sub_id)
                    .first()
                )
                if sub:
                    payment = (
                        db.query(OrganizationBillingPayment)
                        .filter(
                            OrganizationBillingPayment.organization_id == sub.organization_id,
                            OrganizationBillingPayment.status == BillingPaymentStatus.PENDING,
                        )
                        .order_by(OrganizationBillingPayment.id.desc())
                        .first()
                    )
                    if payment:
                        EnterpriseBillingService.mark_payment_succeeded(db, payment, obj.get("payment_intent"))

        elif etype == "invoice.payment_failed":
            sub_id = obj.get("subscription")
            if sub_id:
                sub = (
                    db.query(OrganizationSubscription)
                    .filter(OrganizationSubscription.external_subscription_id == sub_id)
                    .first()
                )
                if sub:
                    payment = (
                        db.query(OrganizationBillingPayment)
                        .filter(OrganizationBillingPayment.organization_id == sub.organization_id)
                        .order_by(OrganizationBillingPayment.id.desc())
                        .first()
                    )
                    if payment:
                        EnterpriseBillingService.mark_payment_failed(
                            db, payment, obj.get("last_finalization_error", {}).get("message", "payment_failed")
                        )

        elif etype == "customer.subscription.deleted":
            sub_id = obj.get("id")
            sub = (
                db.query(OrganizationSubscription)
                .filter(OrganizationSubscription.external_subscription_id == sub_id)
                .first()
            )
            if sub:
                from app.models.studio.billing import OrgSubscriptionStatus

                sub.status = OrgSubscriptionStatus.CANCELLED
                sub.cancelled_at = sub.cancelled_at or obj.get("canceled_at")

    @staticmethod
    def handle_razorpay(db: Session, payload: dict, body: bytes | None = None, signature: str | None = None) -> dict:
        consumer_result = PaymentService.handle_razorpay_webhook(db, payload, body=body, signature=signature)

        if body and signature:
            RazorpayBillingAdapter = __import__(
                "app.services.billing.razorpay_adapter", fromlist=["RazorpayBillingAdapter"]
            ).RazorpayBillingAdapter
            if not RazorpayBillingAdapter.verify_signature(body.decode() if isinstance(body, bytes) else body, signature):
                return {"status": "invalid_signature"}
        elif settings.is_production:
            from app.core.exceptions import UnauthorizedError

            raise UnauthorizedError("Razorpay webhook signature is required in production")

        event_id = payload.get("event_id") or payload.get("id") or hashlib.sha256(json.dumps(payload).encode()).hexdigest()[:32]
        event_type = payload.get("event", "unknown")
        row = BillingWebhookService._record_event(db, PaymentProvider.RAZORPAY, str(event_id), event_type, payload)
        if not row:
            return {"status": "duplicate", **consumer_result}

        try:
            if event_type == "subscription.charged":
                entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
                order_id = entity.get("order_id")
                payment = (
                    db.query(OrganizationBillingPayment)
                    .filter(OrganizationBillingPayment.external_order_id == order_id)
                    .first()
                )
                if payment:
                    EnterpriseBillingService.mark_payment_succeeded(db, payment, entity.get("id"))
            elif event_type == "payment.failed":
                entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
                order_id = entity.get("order_id")
                payment = (
                    db.query(OrganizationBillingPayment)
                    .filter(OrganizationBillingPayment.external_order_id == order_id)
                    .first()
                )
                if payment:
                    EnterpriseBillingService.mark_payment_failed(db, payment, entity.get("error_description", "failed"))
            row.processed = True
            db.commit()
        except Exception as exc:
            row.error_message = str(exc)[:500]
            db.commit()
            raise
        return {"status": "ok"}
