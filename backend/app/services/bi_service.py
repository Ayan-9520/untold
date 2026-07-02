"""Business Intelligence — unified dashboards and KPI aggregation."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.studio.enums import AIGenerationStatus
from app.domain.tenancy.context import TenantContext
from app.models import Subscription, SubscriptionStatus, User
from app.models.studio import AICostEvent, AIGeneration, Production, UsageMeterRecord
from app.models.studio.bi import BIReportDefinition, BIMetricSnapshot
from app.models.studio.billing import OrgInvoiceStatus, OrgSubscriptionStatus, OrganizationInvoice, OrganizationSubscription
from app.models.studio.tenancy import Organization, OrganizationMember, Team, TeamMember
from app.services.studio_platform_service import StudioPlatformService


class BusinessIntelligenceService:
    @staticmethod
    def _require_access(db: Session, user: User) -> None:
        StudioPlatformService.require_permission(db, user, None, "analytics.read")

    @staticmethod
    def _period(days: int = 30) -> tuple[datetime, datetime]:
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=days)
        return start, end

    @staticmethod
    def _org_ids(db: Session, ctx: TenantContext) -> list[int] | None:
        if ctx.organization_id:
            return [ctx.organization_id]
        if ctx.user.is_admin:
            return None
        rows = db.query(OrganizationMember.organization_id).filter(OrganizationMember.user_id == ctx.user.id).all()
        return [r[0] for r in rows] or [-1]

    @staticmethod
    def _apply_org_filter(query, column, org_ids: list[int] | None):
        if org_ids is None:
            return query
        return query.filter(column.in_(org_ids))

    @staticmethod
    def executive_dashboard(db: Session, user: User, ctx: TenantContext, *, days: int = 30) -> dict:
        BusinessIntelligenceService._require_access(db, user)
        start, end = BusinessIntelligenceService._period(days)
        org_ids = BusinessIntelligenceService._org_ids(db, ctx)
        revenue = BusinessIntelligenceService.revenue_dashboard(db, user, ctx, days=days)
        ai_costs = BusinessIntelligenceService.ai_costs_dashboard(db, user, ctx, days=days)
        usage = BusinessIntelligenceService.usage_dashboard(db, user, ctx)
        projects = BusinessIntelligenceService.projects_dashboard(db, user, ctx)
        growth = BusinessIntelligenceService.growth_dashboard(db, user, ctx, days=days)

        q_orgs = db.query(func.count(Organization.id))
        if org_ids:
            q_orgs = q_orgs.filter(Organization.id.in_(org_ids))
        org_count = q_orgs.scalar() or 0

        return {
            "period_days": days,
            "organization_scope": ctx.organization_id,
            "kpis": {
                "mrr_usd": revenue["kpis"]["mrr_usd"],
                "arr_usd": revenue["kpis"]["arr_usd"],
                "ai_cost_usd": ai_costs["kpis"]["total_cost_usd"],
                "active_projects": projects["kpis"]["active_projects"],
                "organizations": org_count,
                "mrr_growth_pct": growth["kpis"]["mrr_growth_pct"],
                "ai_generations": ai_costs["kpis"]["generation_count"],
                "seat_utilization_pct": usage["kpis"]["seat_utilization_pct"],
            },
            "timeseries": {
                "revenue": revenue["timeseries"],
                "ai_cost": ai_costs["timeseries"],
                "projects": projects["timeseries"],
            },
            "highlights": [
                {"label": "Paid invoices (period)", "value": f"${revenue['kpis']['paid_invoice_usd']:.2f}"},
                {"label": "AI success rate", "value": f"{BusinessIntelligenceService.performance_dashboard(db, user, ctx, days=days)['kpis']['success_rate']:.1f}%"},
                {"label": "New orgs (period)", "value": growth["kpis"]["new_orgs"]},
            ],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def revenue_dashboard(db: Session, user: User, ctx: TenantContext, *, days: int = 30) -> dict:
        BusinessIntelligenceService._require_access(db, user)
        start, end = BusinessIntelligenceService._period(days)
        org_ids = BusinessIntelligenceService._org_ids(db, ctx)

        sub_q = db.query(OrganizationSubscription).filter(
            OrganizationSubscription.status.in_([OrgSubscriptionStatus.ACTIVE, OrgSubscriptionStatus.TRIALING])
        )
        if org_ids:
            sub_q = sub_q.filter(OrganizationSubscription.organization_id.in_(org_ids))
        subs = sub_q.all()

        mrr_cents = 0
        for sub in subs:
            plan = sub.plan
            if plan:
                mrr_cents += plan.base_amount_cents + max(0, sub.seat_quantity - plan.included_seats) * plan.seat_price_cents

        inv_q = db.query(func.coalesce(func.sum(OrganizationInvoice.total_cents), 0)).filter(
            OrganizationInvoice.status == OrgInvoiceStatus.PAID,
            OrganizationInvoice.paid_at >= start,
            OrganizationInvoice.paid_at < end,
        )
        if org_ids:
            inv_q = inv_q.filter(OrganizationInvoice.organization_id.in_(org_ids))
        paid_cents = int(inv_q.scalar() or 0)

        from app.services.revenue_service import PLAN_PRICES

        consumer_subs = (
            db.query(Subscription)
            .filter(Subscription.status == SubscriptionStatus.ACTIVE)
            .all()
        )
        consumer_mrr = int(
            sum(PLAN_PRICES.get(sub.plan, 0.0) for sub in consumer_subs) * 100
        )

        total_mrr_cents = mrr_cents + consumer_mrr
        timeseries = BusinessIntelligenceService._snapshot_timeseries(
            db, org_ids, "revenue", "mrr_cents", days=days, fallback_value=total_mrr_cents / max(days, 1)
        )

        return {
            "kpis": {
                "mrr_usd": round(total_mrr_cents / 100, 2),
                "arr_usd": round(total_mrr_cents * 12 / 100, 2),
                "paid_invoice_usd": round(paid_cents / 100, 2),
                "active_subscriptions": len(subs),
                "enterprise_mrr_usd": round(mrr_cents / 100, 2),
                "consumer_mrr_usd": round(consumer_mrr / 100, 2),
            },
            "by_plan": BusinessIntelligenceService._revenue_by_plan(db, subs),
            "timeseries": timeseries,
        }

    @staticmethod
    def _revenue_by_plan(db: Session, subs: list) -> list[dict]:
        buckets: dict[str, float] = {}
        for sub in subs:
            name = sub.plan.name if sub.plan else "unknown"
            plan_mrr = 0
            if sub.plan:
                plan_mrr = sub.plan.base_amount_cents + max(0, sub.seat_quantity - sub.plan.included_seats) * sub.plan.seat_price_cents
            buckets[name] = buckets.get(name, 0) + plan_mrr / 100
        return [{"plan": k, "mrr_usd": round(v, 2)} for k, v in sorted(buckets.items(), key=lambda x: -x[1])]

    @staticmethod
    def ai_costs_dashboard(db: Session, user: User, ctx: TenantContext, *, days: int = 30) -> dict:
        BusinessIntelligenceService._require_access(db, user)
        start, end = BusinessIntelligenceService._period(days)
        org_ids = BusinessIntelligenceService._org_ids(db, ctx)

        q = db.query(AICostEvent).filter(AICostEvent.created_at >= start, AICostEvent.created_at < end)
        if org_ids:
            q = q.filter(AICostEvent.organization_id.in_(org_ids))
        events = q.all()

        total_cost = sum(float(e.cost_usd or 0) for e in events)
        by_modality: dict[str, float] = {}
        by_provider: dict[str, float] = {}
        for e in events:
            mod = e.modality or "tokens"
            by_modality[mod] = by_modality.get(mod, 0) + float(e.cost_usd or 0)
            prov = e.provider or "unknown"
            by_provider[prov] = by_provider.get(prov, 0) + float(e.cost_usd or 0)

        gen_q = db.query(func.count(AIGeneration.id)).filter(
            AIGeneration.created_at >= start, AIGeneration.created_at < end
        )
        if org_ids:
            gen_q = gen_q.join(Production, Production.id == AIGeneration.project_id, isouter=True).filter(
                (Production.organization_id.in_(org_ids)) | (AIGeneration.project_id.is_(None))
            )
        gen_count = gen_q.scalar() or 0

        return {
            "kpis": {
                "total_cost_usd": round(total_cost, 4),
                "generation_count": int(gen_count),
                "avg_cost_per_gen_usd": round(total_cost / gen_count, 4) if gen_count else 0,
                "event_count": len(events),
            },
            "by_modality": [{"label": k, "cost_usd": round(v, 4)} for k, v in sorted(by_modality.items(), key=lambda x: -x[1])],
            "by_provider": [{"label": k, "cost_usd": round(v, 4)} for k, v in sorted(by_provider.items(), key=lambda x: -x[1])[:10]],
            "timeseries": BusinessIntelligenceService._daily_cost_timeseries(db, org_ids, start, end),
        }

    @staticmethod
    def _daily_cost_timeseries(db: Session, org_ids: list[int] | None, start: datetime, end: datetime) -> list[dict]:
        q = db.query(
            func.date_trunc("day", AICostEvent.created_at).label("day"),
            func.coalesce(func.sum(AICostEvent.cost_usd), 0),
        ).filter(AICostEvent.created_at >= start, AICostEvent.created_at < end)
        if org_ids:
            q = q.filter(AICostEvent.organization_id.in_(org_ids))
        rows = q.group_by("day").order_by("day").all()
        return [{"date": r[0].date().isoformat() if r[0] else "", "cost_usd": round(float(r[1] or 0), 4)} for r in rows]

    @staticmethod
    def usage_dashboard(db: Session, user: User, ctx: TenantContext) -> dict:
        BusinessIntelligenceService._require_access(db, user)
        org_ids = BusinessIntelligenceService._org_ids(db, ctx)
        pk = datetime.now(timezone.utc).strftime("%Y-%m")

        q = db.query(UsageMeterRecord).filter(UsageMeterRecord.period_key == pk)
        if org_ids:
            q = q.filter(UsageMeterRecord.organization_id.in_(org_ids))
        rows = q.all()

        totals: dict[str, float] = {}
        for r in rows:
            key = r.meter_type.value if hasattr(r.meter_type, "value") else str(r.meter_type)
            totals[key] = totals.get(key, 0) + float(r.quantity)

        org_q = db.query(Organization)
        if org_ids:
            org_q = org_q.filter(Organization.id.in_(org_ids))
        orgs = org_q.all()
        seat_limit = sum(o.seat_limit for o in orgs) or 1
        seats_used = sum(o.seats_used for o in orgs)
        storage_quota_gb = sum(o.storage_quota_bytes for o in orgs) / 1_073_741_824
        storage_used_gb = sum(o.storage_used_bytes for o in orgs) / 1_073_741_824

        return {
            "period_key": pk,
            "kpis": {
                "seats_used": seats_used,
                "seat_limit": seat_limit,
                "seat_utilization_pct": round(100 * seats_used / seat_limit, 1),
                "storage_used_gb": round(storage_used_gb, 2),
                "storage_quota_gb": round(storage_quota_gb, 2),
                "ai_credits": totals.get("ai_credits", 0),
                "video_minutes": totals.get("video_minutes", 0),
            },
            "meters": totals,
            "by_organization": BusinessIntelligenceService._usage_by_org(db, org_ids),
        }

    @staticmethod
    def _usage_by_org(db: Session, org_ids: list[int] | None) -> list[dict]:
        q = db.query(Organization)
        if org_ids:
            q = q.filter(Organization.id.in_(org_ids))
        return [
            {
                "organization_id": o.id,
                "name": o.name,
                "seats_used": o.seats_used,
                "seat_limit": o.seat_limit,
                "storage_gb": round(o.storage_used_bytes / 1_073_741_824, 2),
            }
            for o in q.limit(20).all()
        ]

    @staticmethod
    def performance_dashboard(db: Session, user: User, ctx: TenantContext, *, days: int = 30) -> dict:
        BusinessIntelligenceService._require_access(db, user)
        start, end = BusinessIntelligenceService._period(days)
        org_ids = BusinessIntelligenceService._org_ids(db, ctx)

        q = db.query(AIGeneration).filter(AIGeneration.created_at >= start, AIGeneration.created_at < end)
        if org_ids:
            q = q.join(Production, Production.id == AIGeneration.project_id, isouter=True).filter(
                (Production.organization_id.in_(org_ids)) | (AIGeneration.project_id.is_(None))
            )
        gens = q.all()
        total = len(gens) or 1
        completed = sum(1 for g in gens if g.status == AIGenerationStatus.COMPLETED)
        latencies = [g.latency_ms for g in gens if g.latency_ms]
        cache_hits = sum(1 for g in gens if (g.output_meta or {}).get("cache_hit"))

        return {
            "kpis": {
                "success_rate": round(100 * completed / total, 1),
                "avg_latency_ms": round(sum(latencies) / len(latencies), 1) if latencies else 0,
                "cache_hit_rate": round(100 * cache_hits / total, 1),
                "total_generations": total,
            },
            "by_module": BusinessIntelligenceService._gens_by_module(gens),
        }

    @staticmethod
    def _gens_by_module(gens: list) -> list[dict]:
        buckets: dict[str, dict] = {}
        for g in gens:
            mod = g.module.value if hasattr(g.module, "value") else str(g.module)
            b = buckets.setdefault(mod, {"count": 0, "latency_sum": 0, "latency_n": 0})
            b["count"] += 1
            if g.latency_ms:
                b["latency_sum"] += g.latency_ms
                b["latency_n"] += 1
        return [
            {
                "module": k,
                "count": v["count"],
                "avg_latency_ms": round(v["latency_sum"] / v["latency_n"], 1) if v["latency_n"] else 0,
            }
            for k, v in sorted(buckets.items(), key=lambda x: -x[1]["count"])
        ]

    @staticmethod
    def projects_dashboard(db: Session, user: User, ctx: TenantContext) -> dict:
        BusinessIntelligenceService._require_access(db, user)
        org_ids = BusinessIntelligenceService._org_ids(db, ctx)
        q = db.query(Production)
        if org_ids:
            q = q.filter(Production.organization_id.in_(org_ids))

        active = q.filter(Production.status == "active").count()
        completed = q.filter(Production.status == "completed").count()
        stage_q = db.query(Production.stage, func.count(Production.id))
        if org_ids:
            stage_q = stage_q.filter(Production.organization_id.in_(org_ids))
        by_stage = stage_q.group_by(Production.stage).all()

        return {
            "kpis": {
                "active_projects": active,
                "completed_projects": completed,
                "total_projects": active + completed,
            },
            "by_stage": [{"stage": s or "unknown", "count": int(c)} for s, c in by_stage],
            "timeseries": BusinessIntelligenceService._snapshot_timeseries(
                db, org_ids, "projects", "active_projects", days=30, fallback_value=active
            ),
        }

    @staticmethod
    def teams_dashboard(db: Session, user: User, ctx: TenantContext) -> dict:
        BusinessIntelligenceService._require_access(db, user)
        org_ids = BusinessIntelligenceService._org_ids(db, ctx)

        tq = db.query(Team)
        if org_ids:
            tq = tq.filter(Team.organization_id.in_(org_ids))
        teams = tq.all()
        team_ids = [t.id for t in teams]
        member_count = (
            db.query(func.count(TeamMember.id)).filter(TeamMember.team_id.in_(team_ids)).scalar() or 0
            if team_ids
            else 0
        )

        return {
            "kpis": {"team_count": len(teams), "member_count": int(member_count)},
            "teams": [
                {
                    "id": t.id,
                    "name": t.name,
                    "slug": t.slug,
                    "organization_id": t.organization_id,
                    "member_count": db.query(func.count(TeamMember.id)).filter(TeamMember.team_id == t.id).scalar() or 0,
                }
                for t in teams[:25]
            ],
        }

    @staticmethod
    def organizations_dashboard(db: Session, user: User, ctx: TenantContext) -> dict:
        BusinessIntelligenceService._require_access(db, user)
        org_ids = BusinessIntelligenceService._org_ids(db, ctx)
        q = db.query(Organization)
        if org_ids:
            q = q.filter(Organization.id.in_(org_ids))

        orgs = q.order_by(Organization.created_at.desc()).limit(50).all()
        members_q = db.query(func.count(OrganizationMember.id))
        if org_ids:
            members_q = members_q.filter(OrganizationMember.organization_id.in_(org_ids))
        total_members = members_q.scalar() or 0
        org_count_q = db.query(func.count(Organization.id))
        if org_ids:
            org_count_q = org_count_q.filter(Organization.id.in_(org_ids))
        total_orgs = org_count_q.scalar() or len(orgs)
        return {
            "kpis": {
                "total_organizations": int(total_orgs),
                "total_members": total_members,
            },
            "organizations": [
                {
                    "id": o.id,
                    "name": o.name,
                    "slug": o.slug,
                    "plan": o.plan.value if hasattr(o.plan, "value") else str(o.plan),
                    "seats_used": o.seats_used,
                    "seat_limit": o.seat_limit,
                    "status": o.status.value if hasattr(o.status, "value") else str(o.status),
                }
                for o in orgs
            ],
        }

    @staticmethod
    def retention_dashboard(db: Session, user: User, ctx: TenantContext, *, days: int = 90) -> dict:
        BusinessIntelligenceService._require_access(db, user)
        start, _ = BusinessIntelligenceService._period(days)
        org_ids = BusinessIntelligenceService._org_ids(db, ctx)

        cancelled = (
            db.query(func.count(OrganizationSubscription.id))
            .filter(
                OrganizationSubscription.status == OrgSubscriptionStatus.CANCELLED,
                OrganizationSubscription.cancelled_at >= start,
            )
        )
        if org_ids:
            cancelled = cancelled.filter(OrganizationSubscription.organization_id.in_(org_ids))
        churned = cancelled.scalar() or 0

        active = (
            db.query(func.count(OrganizationSubscription.id))
            .filter(OrganizationSubscription.status == OrgSubscriptionStatus.ACTIVE)
        )
        if org_ids:
            active = active.filter(OrganizationSubscription.organization_id.in_(org_ids))
        active_count = active.scalar() or 0
        renewal_rate = round(100 * active_count / max(active_count + churned, 1), 1)

        return {
            "period_days": days,
            "kpis": {
                "churned_subscriptions": int(churned),
                "active_subscriptions": int(active_count),
                "renewal_rate": renewal_rate,
            },
            "cohorts": BusinessIntelligenceService._snapshot_timeseries(
                db, org_ids, "retention", "renewal_rate", days=days, fallback_value=renewal_rate
            ),
        }

    @staticmethod
    def growth_dashboard(db: Session, user: User, ctx: TenantContext, *, days: int = 180) -> dict:
        BusinessIntelligenceService._require_access(db, user)
        start, end = BusinessIntelligenceService._period(days)
        org_ids = BusinessIntelligenceService._org_ids(db, ctx)

        new_orgs_q = db.query(func.count(Organization.id)).filter(Organization.created_at >= start)
        if org_ids:
            new_orgs_q = new_orgs_q.filter(Organization.id.in_(org_ids))
        new_orgs = new_orgs_q.scalar() or 0

        new_members_q = db.query(func.count(OrganizationMember.id)).filter(OrganizationMember.joined_at >= start)
        if org_ids:
            new_members_q = new_members_q.filter(OrganizationMember.organization_id.in_(org_ids))
        new_members = new_members_q.scalar() or 0

        new_projects_q = db.query(func.count(Production.id)).filter(Production.created_at >= start)
        if org_ids:
            new_projects_q = new_projects_q.filter(Production.organization_id.in_(org_ids))
        new_projects = new_projects_q.scalar() or 0

        prev_start = start - timedelta(days=days)
        prev_mrr = BusinessIntelligenceService._mrr_at(db, org_ids, prev_start)
        curr_mrr = BusinessIntelligenceService._mrr_at(db, org_ids, end)
        growth_pct = round(100 * (curr_mrr - prev_mrr) / max(prev_mrr, 1), 1)

        return {
            "period_days": days,
            "kpis": {
                "new_orgs": int(new_orgs),
                "new_members": int(new_members),
                "new_projects": int(new_projects),
                "mrr_growth_pct": growth_pct,
            },
            "timeseries": {
                "new_orgs": BusinessIntelligenceService._snapshot_timeseries(
                    db, org_ids, "growth", "new_orgs", days=min(days, 90), fallback_value=new_orgs / max(days, 1)
                ),
            },
        }

    @staticmethod
    def _mrr_at(db: Session, org_ids: list[int] | None, at: datetime) -> float:
        sub_q = db.query(OrganizationSubscription).filter(
            OrganizationSubscription.status.in_([OrgSubscriptionStatus.ACTIVE, OrgSubscriptionStatus.TRIALING])
        )
        if org_ids:
            sub_q = sub_q.filter(OrganizationSubscription.organization_id.in_(org_ids))
        cents = 0
        for sub in sub_q.all():
            if sub.plan:
                cents += sub.plan.base_amount_cents
        return cents / 100

    @staticmethod
    def _snapshot_timeseries(
        db: Session,
        org_ids: list[int] | None,
        namespace: str,
        metric_key: str,
        *,
        days: int,
        fallback_value: float = 0,
    ) -> list[dict]:
        start_date = date.today() - timedelta(days=days)
        q = db.query(BIMetricSnapshot).filter(
            BIMetricSnapshot.metric_namespace == namespace,
            BIMetricSnapshot.metric_key == metric_key,
            BIMetricSnapshot.snapshot_date >= start_date,
        )
        if org_ids:
            q = q.filter(BIMetricSnapshot.organization_id.in_(org_ids))
        rows = q.order_by(BIMetricSnapshot.snapshot_date).all()
        if rows:
            return [{"date": r.snapshot_date.isoformat(), "value": float(r.value)} for r in rows]
        return [{"date": (date.today() - timedelta(days=i)).isoformat(), "value": fallback_value} for i in range(min(days, 14), 0, -1)]

    @staticmethod
    def metric_catalog() -> dict:
        from app.domain.bi.metrics import BI_METRIC_CATALOG, BI_NAMESPACES

        return {"namespaces": list(BI_NAMESPACES), "metrics": BI_METRIC_CATALOG}
