"""Platform pages, FAQ, and consumer promo codes."""

import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError
from app.domain.platform.defaults import DEFAULT_PROMO_CODES, FAQ_ITEMS, PLATFORM_PAGES
from app.models.platform import ConsumerPromoCode, PlatformFaq, PlatformPage


class PlatformService:
    @staticmethod
    def ensure_seeded(db: Session) -> None:
        if not db.query(PlatformPage).first():
            for page in PLATFORM_PAGES:
                db.add(PlatformPage(**page))
        if not db.query(PlatformFaq).first():
            for i, item in enumerate(FAQ_ITEMS):
                db.add(
                    PlatformFaq(
                        faq_key=item["id"],
                        category=item["category"],
                        question=item["question"],
                        answer=item["answer"],
                        sort_order=i,
                    )
                )
        if not db.query(ConsumerPromoCode).first():
            for promo in DEFAULT_PROMO_CODES:
                db.add(
                    ConsumerPromoCode(
                        code=promo["code"],
                        discount_percent=promo["discount_percent"],
                        plan_slugs_json=json.dumps(promo["plan_slugs"]),
                    )
                )
        db.commit()

    @staticmethod
    def list_pages(db: Session, category: str | None = None) -> list[PlatformPage]:
        PlatformService.ensure_seeded(db)
        q = db.query(PlatformPage)
        if category:
            q = q.filter(PlatformPage.category == category)
        return q.order_by(PlatformPage.slug.asc()).all()

    @staticmethod
    def get_page(db: Session, slug: str) -> PlatformPage:
        PlatformService.ensure_seeded(db)
        page = db.query(PlatformPage).filter(PlatformPage.slug == slug).first()
        if not page:
            raise NotFoundError("Page")
        return page

    @staticmethod
    def update_page(db: Session, slug: str, title: str | None, content_md: str | None) -> PlatformPage:
        page = PlatformService.get_page(db, slug)
        if title is not None:
            page.title = title
        if content_md is not None:
            page.content_md = content_md
        db.commit()
        db.refresh(page)
        return page

    @staticmethod
    def list_faq(db: Session, active_only: bool = True) -> list[PlatformFaq]:
        PlatformService.ensure_seeded(db)
        q = db.query(PlatformFaq)
        if active_only:
            q = q.filter(PlatformFaq.is_active.is_(True))
        return q.order_by(PlatformFaq.sort_order.asc()).all()

    @staticmethod
    def upsert_faq(db: Session, faq_key: str, category: str, question: str, answer: str, sort_order: int = 0) -> PlatformFaq:
        row = db.query(PlatformFaq).filter(PlatformFaq.faq_key == faq_key).first()
        if row:
            row.category = category
            row.question = question
            row.answer = answer
            row.sort_order = sort_order
            row.is_active = True
        else:
            row = PlatformFaq(
                faq_key=faq_key,
                category=category,
                question=question,
                answer=answer,
                sort_order=sort_order,
            )
            db.add(row)
        db.commit()
        db.refresh(row)
        return row

    @staticmethod
    def list_promo_codes(db: Session) -> list[ConsumerPromoCode]:
        PlatformService.ensure_seeded(db)
        return db.query(ConsumerPromoCode).order_by(ConsumerPromoCode.code.asc()).all()

    @staticmethod
    def validate_promo(db: Session, code: str, plan_slug: str) -> dict:
        PlatformService.ensure_seeded(db)
        normalized = code.strip().upper()
        row = (
            db.query(ConsumerPromoCode)
            .filter(ConsumerPromoCode.code == normalized, ConsumerPromoCode.is_active.is_(True))
            .first()
        )
        if not row:
            raise BadRequestError("Invalid promo code")
        if row.expires_at and row.expires_at < datetime.now(timezone.utc):
            raise BadRequestError("Promo code expired")
        allowed = json.loads(row.plan_slugs_json or "[]")
        if allowed and plan_slug not in allowed:
            raise BadRequestError("Promo code not valid for this plan")
        return {
            "code": row.code,
            "discount_percent": row.discount_percent,
            "plan_slugs": allowed,
        }
