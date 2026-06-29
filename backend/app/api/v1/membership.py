from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user
from app.db.session import get_db
from app.models import User
from app.schemas.monetization import PlansListResponse, SubscribeRequest, SubscribeResponse
from app.services.membership_service import MembershipService
from app.services.payment_service import PaymentService

router = APIRouter(tags=["Membership"])


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
