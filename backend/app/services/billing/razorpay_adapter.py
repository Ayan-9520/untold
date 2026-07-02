"""Razorpay adapter for organization subscriptions."""

from __future__ import annotations

import logging

from app.core.config import get_settings

logger = logging.getLogger("untold.billing.razorpay")
settings = get_settings()


class RazorpayBillingAdapter:
    @staticmethod
    def available() -> bool:
        return bool(settings.razorpay_key_id and settings.razorpay_key_secret)

    @staticmethod
    def _client():
        import razorpay

        return razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))

    @classmethod
    def create_order(cls, amount_cents: int, currency: str, org_id: int, receipt: str) -> dict:
        if not cls.available():
            return {"id": f"mock_order_{org_id}_{receipt}", "amount": amount_cents, "currency": currency}
        client = cls._client()
        return client.order.create(
            {
                "amount": amount_cents,
                "currency": currency.upper(),
                "receipt": receipt,
                "notes": {"organization_id": str(org_id)},
            }
        )

    @classmethod
    def create_subscription(cls, plan_id: str | None, customer_notify: int = 1) -> dict:
        if not cls.available() or not plan_id:
            return {"id": f"mock_rzp_sub_{plan_id}", "status": "created"}
        client = cls._client()
        return client.subscription.create({"plan_id": plan_id, "customer_notify": customer_notify})

    @classmethod
    def refund_payment(cls, payment_id: str, amount_cents: int | None = None) -> str:
        if not cls.available():
            return f"mock_rfnd_{payment_id}"
        client = cls._client()
        params: dict = {}
        if amount_cents:
            params["amount"] = amount_cents
        refund = client.payment.refund(payment_id, params)
        return refund["id"]

    @classmethod
    def verify_signature(cls, body: str, signature: str) -> bool:
        if not cls.available() or not settings.razorpay_webhook_secret:
            return True
        import hmac
        import hashlib

        expected = hmac.new(
            settings.razorpay_webhook_secret.encode(),
            body.encode() if isinstance(body, str) else body,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
