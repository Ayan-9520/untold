"""Unit tests for enterprise billing."""

import os
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine, text

from app.models.studio.billing import BillingCoupon, BillingPlan, UsageMeterType
from app.services.billing.enterprise_billing_service import EnterpriseBillingService
from app.services.billing.usage_service import UsageMeterService


def _postgres_available() -> bool:
    url = os.environ.get("DATABASE_URL", "")
    if not url.startswith("postgresql"):
        return False
    try:
        with create_engine(url, pool_pre_ping=True).connect() as conn:
            conn.execute(text("SELECT 1"))
            ext = conn.execute(
                text("SELECT 1 FROM pg_available_extensions WHERE name = 'vector'")
            ).fetchone()
            if ext is None:
                return False
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _postgres_available(),
    reason="PostgreSQL required for enterprise billing tests",
)


@pytest.mark.unit
def test_validate_coupon_percent_off(db_session):
    coupon = BillingCoupon(
        code="SAVE20",
        percent_off=20.0,
        is_active=True,
        times_redeemed=0,
    )
    db_session.add(coupon)
    db_session.flush()

    result = EnterpriseBillingService.validate_coupon(db_session, "save20", "studio-pro", org_id=1)
    assert result.valid is True
    assert result.percent_off == 20.0


@pytest.mark.unit
def test_validate_coupon_expired(db_session):
    coupon = BillingCoupon(
        code="OLD",
        percent_off=10.0,
        is_active=True,
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    db_session.add(coupon)
    db_session.flush()

    result = EnterpriseBillingService.validate_coupon(db_session, "OLD", None, org_id=1)
    assert result.valid is False
    assert "expired" in (result.message or "").lower()


@pytest.mark.unit
def test_calculate_amount_with_seats_and_coupon():
    plan = BillingPlan(
        slug="studio-pro",
        name="Pro",
        base_amount_cents=9900,
        included_seats=5,
        seat_price_cents=1500,
    )
    coupon = BillingCoupon(code="FLAT10", amount_off_cents=1000)

    amount = EnterpriseBillingService._calculate_amount_cents(plan, seats=8, coupon=coupon)
    # 9900 + 3*1500 = 14400 - 1000 = 13400
    assert amount == 13400


@pytest.mark.unit
def test_usage_overage_estimation(db_session):
    plan = BillingPlan(
        slug="studio-starter",
        name="Starter",
        included_ai_credits=100,
        included_storage_gb=5,
        included_video_minutes=60,
        included_seats=3,
        usage_rates={"ai_credits": 0.02, "storage_gb": 0.5, "video_minutes": 0.1, "seats": 15.0},
    )
    org_id = 1
    UsageMeterService.record(db_session, org_id, UsageMeterType.AI_CREDITS, 150)
    UsageMeterService.record(db_session, org_id, UsageMeterType.STORAGE_GB, 8)
    db_session.flush()

    summary = UsageMeterService.summary(db_session, org_id, plan)
    assert summary["overage"]["ai_credits"] == 50
    assert summary["overage"]["storage_gb"] == 3
    assert summary["estimated_overage_cents"] > 0
