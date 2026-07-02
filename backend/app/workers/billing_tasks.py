"""Celery tasks — billing retries and usage aggregation."""

import logging
from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.domain.tenancy.enums import OrganizationStatus
from app.models.studio.billing import (
    BillingPaymentStatus,
    OrganizationBillingPayment,
    OrganizationSubscription,
    OrgSubscriptionStatus,
)
from app.models.studio.tenancy import Organization
from app.services.billing.enterprise_billing_service import EnterpriseBillingService
from app.services.billing.stripe_adapter import StripeBillingAdapter
from app.services.billing.usage_service import UsageMeterService
from app.workers.celery_app import celery_app

logger = logging.getLogger("untold.billing.tasks")


@celery_app.task(name="untold.retry_failed_billing_payments")
def retry_failed_billing_payments() -> dict:
    """Retry past-due organization subscriptions with scheduled retry."""
    db = SessionLocal()
    retried = 0
    try:
        now = datetime.now(timezone.utc)
        subs = (
            db.query(OrganizationSubscription)
            .filter(
                OrganizationSubscription.status == OrgSubscriptionStatus.PAST_DUE,
                OrganizationSubscription.next_retry_at <= now,
                OrganizationSubscription.failed_payment_count < 5,
            )
            .all()
        )
        for sub in subs:
            payment = (
                db.query(OrganizationBillingPayment)
                .filter(
                    OrganizationBillingPayment.organization_id == sub.organization_id,
                    OrganizationBillingPayment.status == BillingPaymentStatus.FAILED,
                )
                .order_by(OrganizationBillingPayment.id.desc())
                .first()
            )
            if payment and payment.meta.get("stripe_invoice_id"):
                if StripeBillingAdapter.retry_invoice(payment.meta["stripe_invoice_id"]):
                    EnterpriseBillingService.mark_payment_succeeded(db, payment)
                    retried += 1
            sub.next_retry_at = None
        db.commit()
    finally:
        db.close()
    return {"retried": retried}


@celery_app.task(name="untold.aggregate_billing_usage")
def aggregate_billing_usage() -> dict:
    """Sync seat and storage meters for all active orgs."""
    db = SessionLocal()
    count = 0
    try:
        orgs = db.query(Organization).filter(Organization.status == OrganizationStatus.ACTIVE).all()
        for org in orgs:
            UsageMeterService.sync_seats(db, org)
            UsageMeterService.sync_storage_gb(db, org)
            count += 1
        db.commit()
    finally:
        db.close()
    return {"organizations": count}
