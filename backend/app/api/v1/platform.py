"""Public OTT platform content — legal pages, FAQ, promo codes."""

import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_studio_user
from app.db.session import get_db
from app.models import User
from app.schemas.platform import (
    FaqItemResponse,
    FaqUpsertRequest,
    PlatformPageResponse,
    PlatformPageUpdate,
    PromoCodeCreate,
    PromoCodeResponse,
    PromoValidateRequest,
    PromoValidateResponse,
)
from app.services.platform_service import PlatformService

router = APIRouter(prefix="/platform", tags=["Platform"])
admin_router = APIRouter(prefix="/studio/platform", tags=["Studio Platform"])


@router.get("/pages", response_model=list[PlatformPageResponse])
def list_pages(category: str | None = None, db: Session = Depends(get_db)):
    pages = PlatformService.list_pages(db, category=category)
    return [PlatformPageResponse(slug=p.slug, category=p.category, title=p.title, content_md=p.content_md, updated_at=p.updated_at) for p in pages]


@router.get("/pages/{slug}", response_model=PlatformPageResponse)
def get_page(slug: str, db: Session = Depends(get_db)):
    p = PlatformService.get_page(db, slug)
    return PlatformPageResponse(slug=p.slug, category=p.category, title=p.title, content_md=p.content_md, updated_at=p.updated_at)


@router.get("/faq", response_model=list[FaqItemResponse])
def list_faq(db: Session = Depends(get_db)):
    items = PlatformService.list_faq(db)
    return [FaqItemResponse(id=i.faq_key, category=i.category, question=i.question, answer=i.answer) for i in items]


@router.post("/promo/validate", response_model=PromoValidateResponse)
def validate_promo(data: PromoValidateRequest, db: Session = Depends(get_db)):
    result = PlatformService.validate_promo(db, data.code, data.plan_slug)
    return PromoValidateResponse(**result)


# — Studio admin —

@admin_router.get("/pages", response_model=list[PlatformPageResponse])
def admin_list_pages(db: Session = Depends(get_db), _user: User = Depends(get_current_studio_user)):
    return list_pages(db=db)


@admin_router.patch("/pages/{slug}", response_model=PlatformPageResponse)
def admin_update_page(
    slug: str,
    data: PlatformPageUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_studio_user),
):
    p = PlatformService.update_page(db, slug, data.title, data.content_md)
    return PlatformPageResponse(slug=p.slug, category=p.category, title=p.title, content_md=p.content_md, updated_at=p.updated_at)


@admin_router.get("/faq", response_model=list[FaqItemResponse])
def admin_list_faq(db: Session = Depends(get_db), _user: User = Depends(get_current_studio_user)):
    return list_faq(db=db)


@admin_router.put("/faq", response_model=FaqItemResponse)
def admin_upsert_faq(
    data: FaqUpsertRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_studio_user),
):
    row = PlatformService.upsert_faq(db, data.faq_key, data.category, data.question, data.answer, data.sort_order)
    return FaqItemResponse(id=row.faq_key, category=row.category, question=row.question, answer=row.answer)


@admin_router.get("/promo-codes", response_model=list[PromoCodeResponse])
def admin_list_promos(db: Session = Depends(get_db), _user: User = Depends(get_current_studio_user)):
    rows = PlatformService.list_promo_codes(db)
    return [
        PromoCodeResponse(
            code=r.code,
            discount_percent=r.discount_percent,
            plan_slugs=json.loads(r.plan_slugs_json or "[]"),
            is_active=r.is_active,
            expires_at=r.expires_at,
        )
        for r in rows
    ]


@admin_router.post("/promo-codes", response_model=PromoCodeResponse, status_code=201)
def admin_create_promo(
    data: PromoCodeCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_studio_user),
):
    from app.models.platform import ConsumerPromoCode

    code = data.code.strip().upper()
    if db.query(ConsumerPromoCode).filter(ConsumerPromoCode.code == code).first():
        from app.core.exceptions import BadRequestError

        raise BadRequestError("Promo code already exists")
    row = ConsumerPromoCode(
        code=code,
        discount_percent=data.discount_percent,
        plan_slugs_json=json.dumps(data.plan_slugs),
        expires_at=data.expires_at,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return PromoCodeResponse(
        code=row.code,
        discount_percent=row.discount_percent,
        plan_slugs=data.plan_slugs,
        is_active=row.is_active,
        expires_at=row.expires_at,
    )
