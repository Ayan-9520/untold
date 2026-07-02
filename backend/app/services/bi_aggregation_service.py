"""BI daily metric aggregation — populates snapshot warehouse."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.studio import AICostEvent, AIGeneration, Production, UsageMeterRecord
from app.models.studio.bi import BIMetricSnapshot
from app.models.studio.billing import OrganizationInvoice, OrganizationSubscription, OrgInvoiceStatus, OrgSubscriptionStatus
from app.models.studio.tenancy import Organization, OrganizationMember


class BIAggregationService:
    @staticmethod
    def upsert_snapshot(
        db: Session,
        *,
        organization_id: int | None,
        snapshot_date: date,
        namespace: str,
        metric_key: str,
        value: float,
        dimensions: dict | None = None,
    ) -> None:
        row = (
            db.query(BIMetricSnapshot)
            .filter(
                BIMetricSnapshot.organization_id == organization_id,
                BIMetricSnapshot.snapshot_date == snapshot_date,
                BIMetricSnapshot.metric_namespace == namespace,
                BIMetricSnapshot.metric_key == metric_key,
            )
            .first()
        )
        if row:
            row.value = value
            if dimensions:
                row.dimensions = {**(row.dimensions or {}), **dimensions}
        else:
            db.add(
                BIMetricSnapshot(
                    organization_id=organization_id,
                    snapshot_date=snapshot_date,
                    metric_namespace=namespace,
                    metric_key=metric_key,
                    value=value,
                    dimensions=dimensions or {},
                )
            )

    @staticmethod
    def aggregate_daily(db: Session, *, snapshot_date: date | None = None) -> dict:
        snapshot_date = snapshot_date or (datetime.now(timezone.utc).date() - timedelta(days=1))
        day_start = datetime.combine(snapshot_date, datetime.min.time(), tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)
        orgs = db.query(Organization).all()
        written = 0

        for org in orgs:
            oid = org.id
            mrr_cents = 0
            sub = (
                db.query(OrganizationSubscription)
                .filter(
                    OrganizationSubscription.organization_id == oid,
                    OrganizationSubscription.status.in_([OrgSubscriptionStatus.ACTIVE, OrgSubscriptionStatus.TRIALING]),
                )
                .first()
            )
            if sub and sub.plan:
                mrr_cents = sub.plan.base_amount_cents + max(0, sub.seat_quantity - sub.plan.included_seats) * sub.plan.seat_price_cents

            paid = (
                db.query(func.coalesce(func.sum(OrganizationInvoice.total_cents), 0))
                .filter(
                    OrganizationInvoice.organization_id == oid,
                    OrganizationInvoice.status == OrgInvoiceStatus.PAID,
                    OrganizationInvoice.paid_at >= day_start,
                    OrganizationInvoice.paid_at < day_end,
                )
                .scalar()
                or 0
            )

            ai_cost = (
                db.query(func.coalesce(func.sum(AICostEvent.cost_usd), 0))
                .filter(
                    AICostEvent.organization_id == oid,
                    AICostEvent.created_at >= day_start,
                    AICostEvent.created_at < day_end,
                )
                .scalar()
                or 0
            )

            gen_count = (
                db.query(func.count(AIGeneration.id))
                .join(Production, Production.id == AIGeneration.project_id)
                .filter(Production.organization_id == oid, AIGeneration.created_at >= day_start, AIGeneration.created_at < day_end)
                .scalar()
                or 0
            )

            active_projects = (
                db.query(func.count(Production.id))
                .filter(Production.organization_id == oid, Production.status == "active")
                .scalar()
                or 0
            )

            new_members = (
                db.query(func.count(OrganizationMember.id))
                .filter(OrganizationMember.organization_id == oid, OrganizationMember.joined_at >= day_start, OrganizationMember.joined_at < day_end)
                .scalar()
                or 0
            )

            pk = snapshot_date.strftime("%Y-%m")
            usage_rows = (
                db.query(UsageMeterRecord)
                .filter(UsageMeterRecord.organization_id == oid, UsageMeterRecord.period_key == pk)
                .all()
            )
            meters = {r.meter_type.value: float(r.quantity) for r in usage_rows}

            metrics = [
                ("revenue", "mrr_cents", float(mrr_cents)),
                ("revenue", "invoice_total_cents", float(paid)),
                ("ai_cost", "total_cost_usd", float(ai_cost)),
                ("ai_cost", "generation_count", float(gen_count)),
                ("projects", "active_projects", float(active_projects)),
                ("growth", "new_members", float(new_members)),
                ("usage", "seats", float(org.seats_used)),
                ("usage", "storage_gb", org.storage_used_bytes / 1_073_741_824),
                ("usage", "ai_credits", meters.get("ai_credits", 0)),
            ]
            for ns, key, val in metrics:
                BIAggregationService.upsert_snapshot(db, organization_id=oid, snapshot_date=snapshot_date, namespace=ns, metric_key=key, value=val)
                written += 1

        db.commit()
        return {"snapshot_date": snapshot_date.isoformat(), "organizations": len(orgs), "metrics_written": written}
