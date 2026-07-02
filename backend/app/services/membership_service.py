"""Membership plans, subscriptions, multi-currency pricing."""

import json
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError
from app.models import Subscription, SubscriptionPlan, SubscriptionStatus, User
from app.models.monetization import PlanCatalog
from app.db.seed_monetization import PLANS as SEED_PLANS

logger = logging.getLogger("untold")

DEFAULT_FEATURES = {
    "free": ["Limited catalog", "Ad-supported shorts", "Free magazine sample"],
    "premium": ["Full UNTOLD Originals", "HD streaming", "Continue watching", "E-Magazine access"],
    "vip": ["Everything in Premium", "4K streaming", "Early access", "VIP magazine downloads", "Exclusive live features"],
}

REGION_PROVIDERS = {
    "india": ["razorpay", "stripe"],
    "usa": ["stripe"],
    "europe": ["stripe"],
    "asia": ["stripe"],
    "russia": ["stripe"],
    "latin-america": ["stripe"],
    "middle-east": ["stripe"],
}


class MembershipService:
    @staticmethod
    def list_plans(db: Session, currency: str = "USD", region: str = "usa") -> dict:
        plans = (
            db.query(PlanCatalog)
            .filter(PlanCatalog.is_active.is_(True))
            .order_by(PlanCatalog.sort_order.asc())
            .all()
        )

        if not plans:
            plans_data = SEED_PLANS
            result = []
            for plan in plans_data:
                price = float(plan["prices"].get(currency, plan["prices"].get("USD", 0)))
                result.append(
                    {
                        "id": 0,
                        "slug": plan["slug"],
                        "name": plan["name"],
                        "tier": plan["tier"].value,
                        "description": plan["description"],
                        "price": price,
                        "currency": currency,
                        "features": plan["features"],
                        "highlight": plan["slug"] == "premium",
                    }
                )
            providers = REGION_PROVIDERS.get(region, ["stripe"])
            if currency == "INR" and "razorpay" not in providers:
                providers = ["razorpay", "stripe"]
            return {"plans": result, "currency": currency, "region": region, "payment_providers": providers}

        result = []
        for plan in plans:
            prices = json.loads(plan.prices_json or "{}")
            price = float(prices.get(currency, prices.get("USD", 0)))
            features = json.loads(plan.features_json) if plan.features_json else DEFAULT_FEATURES.get(plan.slug, [])
            result.append(
                {
                    "id": plan.id,
                    "slug": plan.slug,
                    "name": plan.name,
                    "tier": plan.tier.value,
                    "description": plan.description,
                    "price": price,
                    "currency": currency,
                    "features": features,
                    "highlight": plan.slug == "premium",
                }
            )

        providers = REGION_PROVIDERS.get(region, ["stripe"])
        if currency == "INR" and "razorpay" not in providers:
            providers = ["razorpay", "stripe"]

        return {"plans": result, "currency": currency, "region": region, "payment_providers": providers}

    @staticmethod
    def activate_subscription(
        db: Session,
        user: User,
        plan_slug: str,
        currency: str = "USD",
        region: str = "usa",
        provider: str | None = None,
        external_id: str | None = None,
    ) -> Subscription:
        plan_catalog = db.query(PlanCatalog).filter(PlanCatalog.slug == plan_slug).first()
        if not plan_catalog:
            raise NotFoundError("Plan")

        try:
            tier = SubscriptionPlan(plan_slug)
        except ValueError as exc:
            raise BadRequestError("Invalid plan") from exc

        sub = (
            db.query(Subscription)
            .filter(Subscription.user_id == user.id, Subscription.status == SubscriptionStatus.ACTIVE)
            .first()
        )

        expires = None if tier == SubscriptionPlan.FREE else datetime.now(timezone.utc) + timedelta(days=30)

        if sub:
            sub.plan = tier
            sub.plan_catalog_id = plan_catalog.id
            sub.payment_provider = provider
            sub.external_subscription_id = external_id
            sub.currency = currency
            sub.region = region
            sub.expires_at = expires
            sub.status = SubscriptionStatus.ACTIVE
        else:
            sub = Subscription(
                user_id=user.id,
                plan=tier,
                status=SubscriptionStatus.ACTIVE,
                plan_catalog_id=plan_catalog.id,
                payment_provider=provider,
                external_subscription_id=external_id,
                currency=currency,
                region=region,
                expires_at=expires,
            )
            db.add(sub)

        db.commit()
        db.refresh(sub)
        return sub

    @staticmethod
    def cancel_subscription(db: Session, user: User) -> Subscription:
        sub = MembershipService.get_active_subscription(db, user)
        if not sub:
            raise NotFoundError("Subscription")
        if sub.plan == SubscriptionPlan.FREE:
            raise BadRequestError("Free plan cannot be cancelled")
        sub.status = SubscriptionStatus.CANCELLED
        db.commit()
        db.refresh(sub)
        return sub

    @staticmethod
    def get_active_subscription(db: Session, user: User) -> Subscription | None:
        return (
            db.query(Subscription)
            .filter(Subscription.user_id == user.id, Subscription.status == SubscriptionStatus.ACTIVE)
            .order_by(Subscription.created_at.desc())
            .first()
        )
