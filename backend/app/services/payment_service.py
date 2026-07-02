"""Stripe + Razorpay payment processing."""

import json
import logging
import secrets
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import BadRequestError, NotFoundError
from app.models import User
from app.models.monetization import Invoice, InvoiceStatus, Payment, PaymentProvider, PaymentStatus, PlanCatalog
from app.services.membership_service import MembershipService

logger = logging.getLogger("untold")
settings = get_settings()


class PaymentService:
    @staticmethod
    def create_order(
        db: Session,
        user: User,
        plan_slug: str,
        currency: str,
        region: str,
        provider: str,
        promo_code: str | None = None,
        billing_cycle: str = "monthly",
    ) -> Payment:
        if plan_slug == "free":
            MembershipService.activate_subscription(db, user, "free", currency, region)
            raise BadRequestError("Free plan does not require payment")

        plan = db.query(PlanCatalog).filter(PlanCatalog.slug == plan_slug).first()
        if not plan:
            raise NotFoundError("Plan")

        prices = json.loads(plan.prices_json or "{}")
        amount = float(prices.get(currency, prices.get("USD", 0)))
        if billing_cycle == "annual":
            amount = round(amount * 10, 2)  # ~2 months free
        if promo_code:
            from app.services.platform_service import PlatformService

            promo = PlatformService.validate_promo(db, promo_code, plan_slug)
            amount = round(amount * (1 - promo["discount_percent"] / 100), 2)
        if amount <= 0:
            raise BadRequestError("Invalid plan price")

        provider_enum = PaymentProvider(provider)
        payment = Payment(
            user_id=user.id,
            provider=provider_enum,
            amount=amount,
            currency=currency,
            status=PaymentStatus.PENDING,
            plan_slug=plan_slug,
            metadata_json=json.dumps({"region": region, "billing_cycle": billing_cycle, "promo_code": promo_code}),
        )
        db.add(payment)
        db.flush()

        if provider_enum == PaymentProvider.STRIPE:
            PaymentService._init_stripe_order(db, payment, user, plan_slug)
        elif provider_enum == PaymentProvider.RAZORPAY:
            PaymentService._init_razorpay_order(db, payment, user)

        db.commit()
        db.refresh(payment)
        return payment

    @staticmethod
    def _init_stripe_order(db: Session, payment: Payment, user: User, plan_slug: str) -> None:
        meta: dict = {}
        try:
            meta = json.loads(payment.metadata_json or "{}")
        except json.JSONDecodeError:
            pass

        if not settings.stripe_secret_key:
            payment.external_order_id = f"mock_stripe_{payment.id}_{secrets.token_hex(8)}"
            meta["mock"] = True
            meta["client_secret"] = f"mock_secret_{payment.id}"
            payment.metadata_json = json.dumps(meta)
            return

        import stripe

        stripe.api_key = settings.stripe_secret_key
        success_url = f"{settings.frontend_url.rstrip('/')}/membership?payment=success&payment_id={payment.id}"
        cancel_url = f"{settings.frontend_url.rstrip('/')}/membership?payment=cancelled"

        session = stripe.checkout.Session.create(
            mode="payment",
            customer_email=user.email,
            line_items=[
                {
                    "price_data": {
                        "currency": payment.currency.lower(),
                        "unit_amount": int(payment.amount * 100) if payment.currency != "JPY" else int(payment.amount),
                        "product_data": {
                            "name": f"UNTOLD {plan_slug.title()} Membership",
                            "description": f"30-day {plan_slug} plan access",
                        },
                    },
                    "quantity": 1,
                }
            ],
            metadata={
                "user_id": str(user.id),
                "plan_slug": plan_slug,
                "payment_id": str(payment.id),
            },
            success_url=success_url,
            cancel_url=cancel_url,
        )
        payment.external_order_id = session.id
        meta["checkout_url"] = session.url
        meta["client_secret"] = session.id
        payment.metadata_json = json.dumps(meta)

    @staticmethod
    def _init_razorpay_order(db: Session, payment: Payment, user: User) -> None:
        if not settings.razorpay_key_id or not settings.razorpay_key_secret:
            payment.external_order_id = f"mock_rzp_{payment.id}_{secrets.token_hex(8)}"
            return

        import razorpay

        client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))
        order = client.order.create(
            {
                "amount": int(payment.amount * 100),
                "currency": payment.currency,
                "receipt": f"untold_{payment.id}",
                "notes": {"user_id": str(user.id), "plan_slug": payment.plan_slug},
            }
        )
        payment.external_order_id = order["id"]

    @staticmethod
    def build_order_response(payment: Payment) -> dict:
        meta = {}
        try:
            meta = json.loads(payment.metadata_json or "{}")
        except json.JSONDecodeError:
            pass

        response = {
            "payment_id": payment.id,
            "provider": payment.provider.value,
            "order_id": payment.external_order_id,
            "amount": payment.amount,
            "currency": payment.currency,
            "plan_slug": payment.plan_slug,
            "client_secret": meta.get("client_secret"),
            "checkout_url": meta.get("checkout_url"),
            "razorpay_order_id": payment.external_order_id if payment.provider == PaymentProvider.RAZORPAY else None,
            "razorpay_key_id": settings.razorpay_key_id if payment.provider == PaymentProvider.RAZORPAY else None,
        }
        return response

    @staticmethod
    def verify_payment(
        db: Session,
        user: User,
        provider: str,
        payment_id: int,
        order_id: str | None = None,
        payment_external_id: str | None = None,
        signature: str | None = None,
    ) -> dict:
        payment = db.query(Payment).filter(Payment.id == payment_id, Payment.user_id == user.id).first()
        if not payment:
            raise NotFoundError("Payment")

        if payment.status == PaymentStatus.COMPLETED:
            return {"message": "Already verified", "status": "completed", "plan": payment.plan_slug}

        provider_enum = PaymentProvider(provider)
        if provider_enum == PaymentProvider.RAZORPAY:
            PaymentService._verify_razorpay(payment, order_id, payment_external_id, signature)
        elif provider_enum == PaymentProvider.STRIPE:
            PaymentService._verify_stripe(payment, payment_external_id or order_id)

        payment.status = PaymentStatus.COMPLETED
        payment.completed_at = datetime.now(timezone.utc)
        payment.external_payment_id = payment_external_id or order_id

        meta = json.loads(payment.metadata_json or "{}")
        region = meta.get("region", "usa")
        sub = MembershipService.activate_subscription(
            db,
            user,
            payment.plan_slug or "premium",
            payment.currency,
            region,
            provider=provider,
            external_id=payment.external_payment_id,
        )
        payment.subscription_id = sub.id

        invoice = PaymentService._create_invoice(db, user, payment)
        db.commit()

        return {
            "message": "Payment verified — subscription activated",
            "status": "completed",
            "plan": payment.plan_slug,
            "invoice_number": invoice.invoice_number,
        }

    @staticmethod
    def _verify_razorpay(payment: Payment, order_id: str | None, payment_id: str | None, signature: str | None) -> None:
        if settings.is_production and not settings.razorpay_key_secret:
            raise BadRequestError("Razorpay is not configured")
        if not settings.razorpay_key_secret:
            return
        if not all([order_id, payment_id, signature]):
            raise BadRequestError("Razorpay verification requires order_id, payment_id, signature")

        import razorpay

        client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))
        client.utility.verify_payment_signature(
            {"razorpay_order_id": order_id, "razorpay_payment_id": payment_id, "razorpay_signature": signature}
        )

    @staticmethod
    def _verify_stripe(payment: Payment, payment_intent_id: str | None) -> None:
        if not settings.stripe_secret_key or not payment_intent_id:
            return
        import stripe

        stripe.api_key = settings.stripe_secret_key
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        if intent.status != "succeeded":
            raise BadRequestError(f"Payment not completed: {intent.status}")

    @staticmethod
    def _create_invoice(db: Session, user: User, payment: Payment) -> Invoice:
        number = f"UNT-{datetime.now(timezone.utc).strftime('%Y%m')}-{payment.id:06d}"
        invoice = Invoice(
            user_id=user.id,
            payment_id=payment.id,
            invoice_number=number,
            amount=payment.amount,
            currency=payment.currency,
            status=InvoiceStatus.PAID,
        )
        db.add(invoice)
        db.flush()
        return invoice

    @staticmethod
    def handle_stripe_webhook(db: Session, payload: bytes, signature: str | None) -> dict:
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

        if event.get("type") == "payment_intent.succeeded":
            intent = event["data"]["object"]
            payment_id = intent.get("metadata", {}).get("payment_id")
            if payment_id:
                payment = db.query(Payment).filter(Payment.id == int(payment_id)).first()
                if payment and payment.status != PaymentStatus.COMPLETED:
                    user = db.query(User).filter(User.id == payment.user_id).first()
                    if user:
                        PaymentService.verify_payment(
                            db, user, "stripe", payment.id, payment_external_id=intent["id"]
                        )
        return {"status": "ok"}

    @staticmethod
    def handle_razorpay_webhook(db: Session, payload: dict, *, body: bytes | None = None, signature: str | None = None) -> dict:
        if settings.is_production:
            if not settings.razorpay_webhook_secret:
                from app.core.exceptions import UnauthorizedError

                raise UnauthorizedError("Razorpay webhook secret is required in production")
            if not body or not signature:
                from app.core.exceptions import UnauthorizedError

                raise UnauthorizedError("Razorpay webhook signature required")
            import razorpay

            client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))
            client.utility.verify_webhook_signature(body.decode() if isinstance(body, bytes) else body, signature, settings.razorpay_webhook_secret)
        elif body and signature and settings.razorpay_webhook_secret:
            import razorpay

            client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))
            client.utility.verify_webhook_signature(body.decode() if isinstance(body, bytes) else body, signature, settings.razorpay_webhook_secret)

        event = payload.get("event", "")
        if event == "payment.captured":
            entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
            order_id = entity.get("order_id")
            payment = db.query(Payment).filter(Payment.external_order_id == order_id).first()
            if payment and payment.status != PaymentStatus.COMPLETED:
                user = db.query(User).filter(User.id == payment.user_id).first()
                if user:
                    PaymentService.verify_payment(
                        db,
                        user,
                        "razorpay",
                        payment.id,
                        order_id=order_id,
                        payment_external_id=entity.get("id"),
                        signature=signature,
                    )
        return {"status": "ok"}

    @staticmethod
    def list_user_payments(db: Session, user: User) -> list[dict]:
        rows = (
            db.query(Payment)
            .filter(Payment.user_id == user.id)
            .order_by(Payment.created_at.desc())
            .limit(50)
            .all()
        )
        return [
            {
                "id": p.id,
                "amount": float(p.amount),
                "currency": p.currency,
                "status": p.status.value,
                "plan_slug": p.plan_slug,
                "provider": p.provider.value,
                "created_at": p.created_at,
            }
            for p in rows
        ]
