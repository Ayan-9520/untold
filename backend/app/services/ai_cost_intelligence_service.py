"""AI Cost Intelligence service — events, predictions, optimization, routing."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.ai.cost_intelligence import (
    days_in_month,
    optimization_recommendations,
    predict_monthly_spend,
    provider_pricing_catalog,
    route_provider,
)
from app.models import User
from app.models.studio import AICostEvent, AIGeneration, Production
from app.services.ai_cost_service import AICostService
from app.services.studio_platform_service import StudioPlatformService


class AICostIntelligenceService:
    @staticmethod
    def _resolve_org_id(db: Session, gen: AIGeneration) -> int | None:
        if gen.project_id:
            prod = db.query(Production).filter(Production.id == gen.project_id).first()
            if prod and prod.organization_id:
                return prod.organization_id
        return None

    @staticmethod
    def record_event(db: Session, gen: AIGeneration, telemetry: dict) -> AICostEvent | None:
        """Persist granular cost event for intelligence dashboards."""
        if not telemetry:
            return None
        org_id = AICostIntelligenceService._resolve_org_id(db, gen)
        event = AICostEvent(
            generation_id=gen.id,
            organization_id=org_id,
            project_id=gen.project_id,
            user_id=gen.created_by_id,
            module=gen.module.value if hasattr(gen.module, "value") else str(gen.module),
            modality=str(telemetry.get("modality") or "tokens"),
            provider=str(telemetry.get("provider") or gen.provider or "demo"),
            model=telemetry.get("model") or gen.model,
            cost_usd=float(telemetry.get("cost_usd") or telemetry.get("estimated_cost_usd") or gen.cost_usd or 0),
            input_tokens=int(telemetry.get("input_tokens") or gen.input_tokens or 0),
            output_tokens=int(telemetry.get("output_tokens") or gen.output_tokens or 0),
            units=dict(telemetry.get("units") or {}),
            cache_hit=bool((gen.output_meta or {}).get("cache_hit")),
            meta={"generation_status": gen.status.value if hasattr(gen.status, "value") else str(gen.status)},
        )
        db.add(event)
        db.flush()
        return event

    @staticmethod
    def intelligence_dashboard(db: Session, user: User, *, year: int | None = None, month: int | None = None) -> dict:
        """Extended dashboard with modality breakdown, predictions, and optimization."""
        StudioPlatformService.require_permission(db, user, None, "analytics.read")
        base = AICostService.dashboard(db, user, year=year, month=month)

        now = datetime.now(timezone.utc)
        y, m = year or now.year, month or now.month
        start = datetime(y, m, 1, tzinfo=timezone.utc)
        end = datetime(y + 1, 1, 1, tzinfo=timezone.utc) if m == 12 else datetime(y, m + 1, 1, tzinfo=timezone.utc)

        events = (
            db.query(AICostEvent)
            .filter(AICostEvent.created_at >= start, AICostEvent.created_at < end)
            .all()
        )

        by_modality: dict[str, dict] = {}
        unit_totals: dict[str, float] = {}
        for ev in events:
            mod = ev.modality or "tokens"
            bucket = by_modality.setdefault(
                mod,
                {"modality": mod, "cost_usd": 0.0, "request_count": 0, "units": {}},
            )
            bucket["cost_usd"] += float(ev.cost_usd or 0)
            bucket["request_count"] += 1
            for uk, uv in (ev.units or {}).items():
                bucket["units"][uk] = bucket["units"].get(uk, 0) + float(uv)
                unit_totals[uk] = unit_totals.get(uk, 0) + float(uv)

        by_module = base.get("by_module") or []
        if not by_module:
            rows = (
                db.query(
                    AIGeneration.module,
                    func.coalesce(func.sum(AIGeneration.cost_usd), 0),
                    func.count(AIGeneration.id),
                )
                .filter(
                    AIGeneration.created_at >= start,
                    AIGeneration.created_at < end,
                )
                .group_by(AIGeneration.module)
                .all()
            )
            by_module = [
                {
                    "key": r[0].value if hasattr(r[0], "value") else str(r[0]),
                    "label": r[0].value if hasattr(r[0], "value") else str(r[0]),
                    "cost_usd": round(float(r[1] or 0), 4),
                    "request_count": int(r[2]),
                }
                for r in rows
            ]

        days_elapsed = max(1, (min(now, end) - start).days + 1) if y == now.year and m == now.month else days_in_month(y, m)
        dim = days_in_month(y, m)
        prediction = predict_monthly_spend(
            mtd_spend_usd=base["total_cost_usd"],
            mtd_requests=base["total_requests"],
            days_elapsed=days_elapsed,
            days_in_month=dim,
        )

        optimizations = optimization_recommendations(
            by_model=base.get("by_model", []),
            by_provider=base.get("by_provider", []),
            by_module=by_module,
            cache_savings_usd=base.get("cache_savings_usd", 0),
            total_cost_usd=base.get("total_cost_usd", 0),
        )

        return {
            **base,
            "by_module": by_module,
            "by_modality": [
                {
                    "modality": k,
                    "cost_usd": round(v["cost_usd"], 4),
                    "request_count": v["request_count"],
                    "units": {uk: round(uv, 2) for uk, uv in v["units"].items()},
                }
                for k, v in sorted(by_modality.items(), key=lambda x: x[1]["cost_usd"], reverse=True)
            ],
            "unit_totals": {k: round(v, 2) for k, v in unit_totals.items()},
            "prediction": prediction,
            "optimizations": optimizations,
            "pricing_catalog": provider_pricing_catalog(),
        }

    @staticmethod
    def resolve_routing(
        db: Session,
        user: User,
        *,
        module: str,
        prompt: str,
        max_cost_per_request: float | None = None,
    ) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        policy = AICostService.get_policy(db, module)
        decision = route_provider(
            module,
            prompt,
            selection_mode=policy.selection_mode if policy else "auto",
            primary_model=policy.primary_model if policy else None,
            primary_provider=policy.primary_provider if policy else None,
            max_cost_per_request=max_cost_per_request
            or (float(policy.max_cost_per_request_usd) if policy and policy.max_cost_per_request_usd else None),
            fallback_chain=list(policy.fallback_chain) if policy and policy.fallback_chain else None,
        )
        return {
            "provider": decision.provider,
            "model": decision.model,
            "estimated_cost_usd": decision.estimated_cost_usd,
            "selection_mode": decision.selection_mode,
            "fallback_chain": decision.fallback_chain,
            "rationale": decision.rationale,
        }

    @staticmethod
    def org_spend_summary(db: Session, organization_id: int, *, year: int | None = None, month: int | None = None) -> dict:
        now = datetime.now(timezone.utc)
        y, m = year or now.year, month or now.month
        start = datetime(y, m, 1, tzinfo=timezone.utc)
        end = datetime(y + 1, 1, 1, tzinfo=timezone.utc) if m == 12 else datetime(y, m + 1, 1, tzinfo=timezone.utc)

        totals = (
            db.query(
                func.coalesce(func.sum(AICostEvent.cost_usd), 0),
                func.count(AICostEvent.id),
            )
            .filter(
                AICostEvent.organization_id == organization_id,
                AICostEvent.created_at >= start,
                AICostEvent.created_at < end,
            )
            .one()
        )
        return {
            "organization_id": organization_id,
            "period_start": start,
            "period_end": end,
            "total_cost_usd": round(float(totals[0] or 0), 4),
            "total_events": int(totals[1] or 0),
        }
