from datetime import datetime

from pydantic import BaseModel, Field


class PlatformPageResponse(BaseModel):
    slug: str
    category: str
    title: str
    content_md: str
    updated_at: datetime | None = None


class PlatformPageUpdate(BaseModel):
    title: str | None = None
    content_md: str | None = None


class FaqItemResponse(BaseModel):
    id: str
    category: str
    question: str
    answer: str


class FaqUpsertRequest(BaseModel):
    faq_key: str = Field(max_length=80)
    category: str = Field(default="General", max_length=60)
    question: str
    answer: str
    sort_order: int = 0


class PromoCodeResponse(BaseModel):
    code: str
    discount_percent: int
    plan_slugs: list[str]
    is_active: bool = True
    expires_at: datetime | None = None


class PromoValidateRequest(BaseModel):
    code: str
    plan_slug: str


class PromoValidateResponse(BaseModel):
    code: str
    discount_percent: int
    plan_slugs: list[str]


class PromoCodeCreate(BaseModel):
    code: str
    discount_percent: int = Field(ge=1, le=100)
    plan_slugs: list[str] = ["premium", "vip"]
    expires_at: datetime | None = None
