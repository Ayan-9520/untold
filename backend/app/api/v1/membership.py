from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user
from app.db.session import get_db
from app.models import User
from app.schemas.monetization import (
    CancelSubscriptionResponse,
    PaymentHistoryItem,
    PlansListResponse,
    SubscribeRequest,
    SubscribeResponse,
    UserSubscriptionResponse,
)
from app.services.membership_service import MembershipService
from app.services.payment_service import PaymentService

DEVICE_LIMITS = {"free": 1, "premium": 2, "vip": 4}

router = APIRouter(tags=["Membership"])


@router.get("/membership/me", response_model=UserSubscriptionResponse)
def get_my_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    sub = MembershipService.get_active_subscription(db, current_user)
    if not sub:
        return UserSubscriptionResponse(plan="free", status="active", device_limit=DEVICE_LIMITS["free"])
    return UserSubscriptionResponse(
        plan=sub.plan.value,
        status=sub.status.value,
        started_at=sub.started_at,
        expires_at=sub.expires_at,
        device_limit=DEVICE_LIMITS.get(sub.plan.value, 1),
    )


@router.post("/membership/cancel", response_model=CancelSubscriptionResponse)
def cancel_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    sub = MembershipService.cancel_subscription(db, current_user)
    return CancelSubscriptionResponse(
        message="Subscription cancelled. Access continues until period end.",
        plan=sub.plan.value,
        status=sub.status.value,
    )


@router.get("/membership/payments", response_model=list[PaymentHistoryItem])
def payment_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return PaymentService.list_user_payments(db, current_user)


@router.get("/plans", response_model=PlansListResponse)
def list_plans(
    currency: str = Query("USD", max_length=10),
    region: str = Query("usa", max_length=50),
    db: Session = Depends(get_db),
):
    return MembershipService.list_plans(db, currency=currency.upper(), region=region)


@router.post("/subscribe", response_model=SubscribeResponse)
def subscribe(
    data: SubscribeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if data.plan_slug == "free":
        sub = MembershipService.activate_subscription(
            db, current_user, "free", data.currency.upper(), data.region
        )
        return SubscribeResponse(message="Free plan activated", plan="free", subscription_id=sub.id)

    payment = PaymentService.create_order(
        db,
        current_user,
        data.plan_slug,
        data.currency.upper(),
        data.region,
        data.provider,
    )
    checkout = PaymentService.build_order_response(payment)
    return SubscribeResponse(
        message="Checkout created",
        plan=data.plan_slug,
        subscription_id=None,
        checkout=checkout,
    )
