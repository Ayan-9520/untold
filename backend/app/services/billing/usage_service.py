"""Usage metering for AI credits, storage, video minutes, seats."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.studio.billing import BillingPlan, OrganizationSubscription, UsageMeterRecord, UsageMeterType
from app.models.studio.tenancy import Organization


class UsageMeterService:
    @staticmethod
    def period_key(dt: datetime | None = None) -> str:
        dt = dt or datetime.now(timezone.utc)
        return dt.strftime("%Y-%m")

    @staticmethod
    def record(
        db: Session,
        organization_id: int,
        meter_type: UsageMeterType,
        quantity: float,
        *,
        increment: bool = True,
        meta: dict | None = None,
    ) -> UsageMeterRecord:
        pk = UsageMeterService.period_key()
        row = (
            db.query(UsageMeterRecord)
            .filter(
                UsageMeterRecord.organization_id == organization_id,
                UsageMeterRecord.meter_type == meter_type,
                UsageMeterRecord.period_key == pk,
            )
            .first()
        )
        if not row:
            row = UsageMeterRecord(
                organization_id=organization_id,
                meter_type=meter_type,
                period_key=pk,
                quantity=0,
                meta=meta or {},
            )
            db.add(row)
        if increment:
            row.quantity = float(row.quantity) + quantity
        else:
            row.quantity = quantity
        if meta:
            row.meta = {**(row.meta or {}), **meta}
        db.flush()
        return row

    @staticmethod
    def sync_seats(db: Session, organization: Organization) -> None:
        UsageMeterService.record(
            db,
            organization.id,
            UsageMeterType.SEATS,
            float(organization.seats_used),
            increment=False,
        )

    @staticmethod
    def sync_storage_gb(db: Session, organization: Organization) -> None:
        gb = organization.storage_used_bytes / 1_073_741_824
        UsageMeterService.record(
            db,
            organization.id,
            UsageMeterType.STORAGE_GB,
            gb,
            increment=False,
        )

    @staticmethod
    def summary(db: Session, organization_id: int, plan: BillingPlan | None) -> dict:
        pk = UsageMeterService.period_key()
        rows = (
            db.query(UsageMeterRecord)
            .filter(
                UsageMeterRecord.organization_id == organization_id,
                UsageMeterRecord.period_key == pk,
            )
            .all()
        )
        meters = {r.meter_type.value: float(r.quantity) for r in rows}
        included = {
            "seats": float(plan.included_seats if plan else 3),
            "ai_credits": float(plan.included_ai_credits if plan else 100),
            "storage_gb": float(plan.included_storage_gb if plan else 5),
            "video_minutes": float(plan.included_video_minutes if plan else 60),
        }
        overage = {}
        rates = plan.usage_rates if plan else {}
        overage_cents = 0
        mapping = {
            "ai_credits": UsageMeterType.AI_CREDITS.value,
            "storage_gb": UsageMeterType.STORAGE_GB.value,
            "video_minutes": UsageMeterType.VIDEO_MINUTES.value,
            "seats": UsageMeterType.SEATS.value,
        }
        for key, meter_key in mapping.items():
            used = meters.get(meter_key, 0)
            inc = included.get(key, 0)
            extra = max(0, used - inc)
            overage[key] = extra
            rate = float(rates.get(key, 0))
            overage_cents += int(extra * rate * 100) if key != "storage_gb" else int(extra * rate * 100)

        return {
            "period_key": pk,
            "meters": meters,
            "included": included,
            "overage": overage,
            "estimated_overage_cents": overage_cents,
        }
