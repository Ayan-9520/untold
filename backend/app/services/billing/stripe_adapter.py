"""Stripe adapter for organization subscriptions."""

from __future__ import annotations

import logging

from app.core.config import get_settings

logger = logging.getLogger("untold.billing.stripe")
settings = get_settings()


class StripeBillingAdapter:
    @staticmethod
    def available() -> bool:
        return bool(settings.stripe_secret_key)

    @staticmethod
    def _client():
        import stripe

        stripe.api_key = settings.stripe_secret_key
        return stripe

    @classmethod
    def create_customer(cls, email: str, name: str, org_id: int) -> str:
        if not cls.available():
            return f"mock_cus_{org_id}"
        stripe = cls._client()
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={"organization_id": str(org_id)},
        )
        return customer.id

    @classmethod
    def create_subscription(
        cls,
        customer_id: str,
        price_id: str | None,
        quantity: int,
        trial_days: int = 14,
        coupon_id: str | None = None,
    ) -> dict:
        if not cls.available():
            return {
                "id": f"mock_sub_{customer_id}",
                "status": "trialing",
                "client_secret": f"mock_secret_{customer_id}",
            }
        stripe = cls._client()
        params: dict = {
            "customer": customer_id,
            "items": [{"price": price_id or settings.stripe_default_price_id, "quantity": quantity}],
            "payment_behavior": "default_incomplete",
            "expand": ["latest_invoice.payment_intent"],
            "metadata": {},
        }
        if trial_days > 0:
            params["trial_period_days"] = trial_days
        if coupon_id:
            params["coupon"] = coupon_id
        sub = stripe.Subscription.create(**params)
        client_secret = None
        if sub.latest_invoice and sub.latest_invoice.payment_intent:
            client_secret = sub.latest_invoice.payment_intent.client_secret
        return {"id": sub.id, "status": sub.status, "client_secret": client_secret}

    @classmethod
    def update_subscription_quantity(cls, subscription_id: str, quantity: int) -> None:
        if not cls.available():
            return
        stripe = cls._client()
        sub = stripe.Subscription.retrieve(subscription_id)
        item_id = sub["items"]["data"][0]["id"]
        stripe.Subscription.modify(subscription_id, items=[{"id": item_id, "quantity": quantity}])

    @classmethod
    def cancel_subscription(cls, subscription_id: str, at_period_end: bool = True) -> None:
        if not cls.available():
            return
        stripe = cls._client()
        if at_period_end:
            stripe.Subscription.modify(subscription_id, cancel_at_period_end=True)
        else:
            stripe.Subscription.delete(subscription_id)

    @classmethod
    def create_refund(cls, payment_intent_id: str, amount_cents: int | None = None) -> str:
        if not cls.available():
            return f"mock_re_{payment_intent_id}"
        stripe = cls._client()
        params: dict = {"payment_intent": payment_intent_id}
        if amount_cents:
            params["amount"] = amount_cents
        refund = stripe.Refund.create(**params)
        return refund.id

    @classmethod
    def retry_invoice(cls, invoice_id: str) -> bool:
        if not cls.available():
            return True
        stripe = cls._client()
        inv = stripe.Invoice.retrieve(invoice_id)
        if inv.status == "open":
            stripe.Invoice.pay(invoice_id)
            return True
        return False
