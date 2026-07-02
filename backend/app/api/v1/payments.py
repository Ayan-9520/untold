from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user
from app.db.session import get_db
from app.models import User
from app.schemas.monetization import (
    CreateOrderRequest,
    CreateOrderResponse,
    VerifyPaymentRequest,
    VerifyPaymentResponse,
)
from app.services.billing.webhook_service import BillingWebhookService
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])
webhook_router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/create-order", response_model=CreateOrderResponse)
def create_order(
    data: CreateOrderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    payment = PaymentService.create_order(
        db,
        current_user,
        data.plan_slug,
        data.currency.upper(),
        data.region,
        data.provider,
        promo_code=data.promo_code,
        billing_cycle=data.billing_cycle,
    )
    return PaymentService.build_order_response(payment)


@router.post("/verify", response_model=VerifyPaymentResponse)
def verify_payment(
    data: VerifyPaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = PaymentService.verify_payment(
        db,
        current_user,
        data.provider,
        data.payment_id,
        order_id=data.order_id,
        payment_external_id=data.payment_external_id,
        signature=data.signature,
    )
    return VerifyPaymentResponse(**result)


@webhook_router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    return BillingWebhookService.handle_stripe(db, payload, signature)


@webhook_router.post("/razorpay")
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)):
    import json

    body = await request.body()
    payload = json.loads(body)
    signature = request.headers.get("X-Razorpay-Signature")
    return BillingWebhookService.handle_razorpay(db, payload, body=body, signature=signature)
