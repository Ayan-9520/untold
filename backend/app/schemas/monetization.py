from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class PlanResponse(BaseModel):
    id: int
    slug: str
    name: str
    tier: str
    description: str | None = None
    price: float
    currency: str
    features: list[str] = []
    highlight: bool = False


class PlansListResponse(BaseModel):
    plans: list[PlanResponse]
    currency: str
    region: str
    payment_providers: list[str]


class SubscribeRequest(BaseModel):
    plan_slug: str
    currency: str = "USD"
    region: str = "usa"
    provider: str = "stripe"


class SubscribeResponse(BaseModel):
    message: str
    plan: str
    subscription_id: int | None = None
    checkout: dict | None = None


class UserSubscriptionResponse(BaseModel):
    plan: str
    status: str
    started_at: datetime | None = None
    expires_at: datetime | None = None
    device_limit: int = 1


class PaymentHistoryItem(BaseModel):
    id: int
    amount: float
    currency: str
    status: str
    plan_slug: str | None = None
    provider: str
    created_at: datetime


class CancelSubscriptionResponse(BaseModel):
    message: str
    plan: str
    status: str


class CreateOrderRequest(BaseModel):
    plan_slug: str
    currency: str = "USD"
    region: str = "usa"
    provider: str = Field(description="stripe or razorpay")
    promo_code: str | None = None
    billing_cycle: str = Field(default="monthly", description="monthly or annual")


class CreateOrderResponse(BaseModel):
    payment_id: int
    provider: str
    order_id: str | None = None
    client_secret: str | None = None
    checkout_url: str | None = None
    razorpay_order_id: str | None = None
    razorpay_key_id: str | None = None
    amount: float
    currency: str
    plan_slug: str


class VerifyPaymentRequest(BaseModel):
    provider: str
    payment_id: int
    order_id: str | None = None
    payment_external_id: str | None = None
    signature: str | None = None


class VerifyPaymentResponse(BaseModel):
    message: str
    status: str
    plan: str | None = None
    invoice_number: str | None = None


class StreamResponse(BaseModel):
    video_id: int
    stream_url: str
    expires_in: int
    access_tier: str
    format: str = "hls"
    subtitle_url: str | None = None
    intro_end_seconds: int | None = None
    next_video_id: int | None = None


class WatchProgressRequest(BaseModel):
    video_id: int = Field(gt=0)
    position_seconds: int = Field(ge=0)
    duration_seconds: int | None = Field(default=None, ge=0)


class WatchProgressResponse(BaseModel):
    message: str
    progress_percent: float


class ContinueWatchingItem(ORMBase):
    video_id: int
    title: str
    image_url: str | None
    position_seconds: int
    duration_seconds: int | None
    progress_percent: float
    updated_at: datetime


class MagazineDownloadResponse(BaseModel):
    download_url: str
    expires_in: int
    magazine_id: int
    title: str
