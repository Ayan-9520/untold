"""AI Cost Optimization — tracking, budgets, caching, model policies, reports."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ConflictError, ForbiddenError, NotFoundError
from app.domain.ai.cost_optimizer import DEFAULT_FALLBACK_CHAIN, build_cache_key, select_model
from app.domain.studio.enums import AIGenerationStatus
from app.models import User
from app.models.studio import Production
from app.models.studio_platform import (
    AICostAlert,
    AICostBudget,
    AIGeneration,
    AIModelPolicy,
    AIMonthlyCostReport,
    AIResponseCache,
    StudioNotification,
)
from app.schemas.ai_cost import BudgetCreate, BudgetUpdate, ModelPolicyUpdate
from app.services.studio_platform_service import StudioPlatformService

DEFAULT_POLICIES: list[dict] = [
    {"module": "*", "selection_mode": "auto", "fallback_chain": DEFAULT_FALLBACK_CHAIN, "cache_enabled": True},
    {"module": "research", "selection_mode": "auto", "primary_model": "gpt-4o-mini", "primary_provider": "openai"},
    {"module": "script", "selection_mode": "quality", "primary_model": "gpt-4o", "primary_provider": "openai"},
    {"module": "seo", "selection_mode": "cheapest", "primary_model": "gpt-4o-mini", "primary_provider": "openai"},
    {"module": "translation", "selection_mode": "auto", "primary_model": "gpt-4o-mini", "primary_provider": "openai"},
    {"module": "thumbnail", "selection_mode": "cheapest", "cache_ttl_hours": 48},
]


class AICostService:
    @staticmethod
    def _month_bounds(ref: datetime | None = None) -> tuple[datetime, datetime]:
        ref = ref or datetime.now(timezone.utc)
        start = ref.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if ref.month == 12:
            end = start.replace(year=start.year + 1, month=1)
        else:
            end = start.replace(month=start.month + 1)
        return start, end

    @staticmethod
    def ensure_policies(db: Session) -> None:
        if db.query(AIModelPolicy).count():
            return
        for p in DEFAULT_POLICIES:
            db.add(
                AIModelPolicy(
                    module=p["module"],
                    selection_mode=p.get("selection_mode", "auto"),
                    primary_model=p.get("primary_model"),
                    primary_provider=p.get("primary_provider"),
                    fallback_chain=p.get("fallback_chain", DEFAULT_FALLBACK_CHAIN),
                    cache_enabled=p.get("cache_enabled", True),
                    cache_ttl_hours=p.get("cache_ttl_hours", 24),
                )
            )
        db.commit()

    @staticmethod
    def _spend_query(db: Session, start: datetime, end: datetime):
        return (
            db.query(AIGeneration)
            .filter(
                AIGeneration.created_at >= start,
                AIGeneration.created_at < end,
                AIGeneration.status == AIGenerationStatus.COMPLETED,
            )
        )

    @staticmethod
    def _monthly_spend(
        db: Session,
        *,
        start: datetime,
        end: datetime,
        user_id: int | None = None,
        project_id: int | None = None,
    ) -> float:
        q = AICostService._spend_query(db, start, end)
        if user_id is not None:
            q = q.filter(AIGeneration.created_by_id == user_id)
        if project_id is not None:
            q = q.filter(AIGeneration.project_id == project_id)
        return float(q.with_entities(func.coalesce(func.sum(AIGeneration.cost_usd), 0)).scalar() or 0)

    @staticmethod
    def _monthly_spend_org(
        db: Session,
        *,
        start: datetime,
        end: datetime,
        organization_id: int,
    ) -> float:
        q = (
            AICostService._spend_query(db, start, end)
            .join(Production, AIGeneration.project_id == Production.id)
            .filter(Production.organization_id == organization_id)
        )
        return float(q.with_entities(func.coalesce(func.sum(AIGeneration.cost_usd), 0)).scalar() or 0)

    @staticmethod
    def _budget_spend(
        db: Session,
        budget: AICostBudget,
        *,
        start: datetime,
        end: datetime,
        gen: AIGeneration | None = None,
    ) -> float | None:
        if budget.scope_type == "global":
            return AICostService._monthly_spend(db, start=start, end=end)
        if budget.scope_type == "user" and budget.scope_id:
            if gen and gen.created_by_id != budget.scope_id:
                return None
            return AICostService._monthly_spend(db, start=start, end=end, user_id=budget.scope_id)
        if budget.scope_type == "project" and budget.scope_id:
            if gen and gen.project_id != budget.scope_id:
                return None
            return AICostService._monthly_spend(db, start=start, end=end, project_id=budget.scope_id)
        if budget.scope_type == "organization" and budget.scope_id:
            if gen and gen.project_id:
                prod = db.query(Production).filter(Production.id == gen.project_id).first()
                if not prod or prod.organization_id != budget.scope_id:
                    return None
            return AICostService._monthly_spend_org(db, start=start, end=end, organization_id=budget.scope_id)
        return None

    @staticmethod
    def get_policy(db: Session, module: str) -> AIModelPolicy | None:
        AICostService.ensure_policies(db)
        policy = db.query(AIModelPolicy).filter(AIModelPolicy.module == module, AIModelPolicy.enabled.is_(True)).first()
        if policy:
            return policy
        return db.query(AIModelPolicy).filter(AIModelPolicy.module == "*", AIModelPolicy.enabled.is_(True)).first()

    @staticmethod
    def check_budgets(db: Session, gen: AIGeneration) -> None:
        """Raise ForbiddenError if any applicable hard budget is exceeded."""
        start, end = AICostService._month_bounds()
        budgets = db.query(AICostBudget).filter(AICostBudget.enabled.is_(True)).all()
        for budget in budgets:
            spend = AICostService._budget_spend(db, budget, start=start, end=end, gen=gen)
            if spend is None:
                continue
            limit = float(budget.monthly_limit_usd)
            if limit <= 0:
                continue
            if budget.hard_limit and spend >= limit:
                raise ForbiddenError(
                    f"AI budget '{budget.name}' exceeded (${spend:.2f} / ${limit:.2f}) — generation blocked"
                )

    @staticmethod
    def evaluate_budget_alerts(db: Session, gen: AIGeneration) -> None:
        start, end = AICostService._month_bounds()
        budgets = db.query(AICostBudget).filter(AICostBudget.enabled.is_(True)).all()
        for budget in budgets:
            spend = AICostService._budget_spend(db, budget, start=start, end=end, gen=gen)
            if spend is None:
                continue
            notify_user_id = gen.created_by_id
            if budget.scope_type == "global":
                notify_user_id = budget.created_by_id or gen.created_by_id

            limit = float(budget.monthly_limit_usd)
            if limit <= 0:
                continue
            pct = int(spend / limit * 100)
            threshold = budget.alert_threshold_pct

            alert_type = None
            if pct >= 100:
                alert_type = "limit_exceeded"
            elif pct >= threshold:
                alert_type = "threshold"

            if not alert_type:
                continue

            recent = (
                db.query(AICostAlert)
                .filter(
                    AICostAlert.budget_id == budget.id,
                    AICostAlert.alert_type == alert_type,
                    AICostAlert.created_at >= start,
                )
                .first()
            )
            if recent:
                continue

            msg = f"Budget '{budget.name}' at {pct}% (${spend:.2f} of ${limit:.2f})"
            db.add(
                AICostAlert(
                    budget_id=budget.id,
                    alert_type=alert_type,
                    threshold_pct=threshold,
                    spend_usd=round(spend, 4),
                    limit_usd=limit,
                    message=msg,
                )
            )
            if notify_user_id:
                db.add(
                    StudioNotification(
                        user_id=notify_user_id,
                        notification_type="ai_budget_alert",
                        title="AI budget alert",
                        body=msg,
                        data={"budget_id": budget.id, "spend_usd": spend, "limit_usd": limit},
                    )
                )

    @staticmethod
    def get_cache_hit(db: Session, module: str, prompt: str, parameters: dict | None) -> dict | None:
        policy = AICostService.get_policy(db, module)
        if not policy or not policy.cache_enabled:
            return None
        if (parameters or {}).get("cache_disabled"):
            return None

        key = build_cache_key(module, prompt, parameters)
        now = datetime.now(timezone.utc)
        entry = (
            db.query(AIResponseCache)
            .filter(AIResponseCache.cache_key == key, AIResponseCache.expires_at > now)
            .first()
        )
        if not entry:
            return None

        entry.hit_count = (entry.hit_count or 0) + 1
        db.flush()
        payload = dict(entry.response_payload or {})
        payload["_cache_hit"] = True
        payload["_cost_saved_usd"] = float(entry.cost_saved_usd or 0)
        return payload

    @staticmethod
    def store_cache(
        db: Session,
        *,
        module: str,
        prompt: str,
        parameters: dict | None,
        payload: dict[str, Any],
        model: str | None,
        provider: str | None,
        cost_usd: float,
    ) -> None:
        policy = AICostService.get_policy(db, module)
        if not policy or not policy.cache_enabled:
            return
        if (parameters or {}).get("cache_disabled"):
            return

        from datetime import timedelta

        from app.domain.ai.cost_optimizer import prompt_hash

        key = build_cache_key(module, prompt, parameters)
        expires = datetime.now(timezone.utc) + timedelta(hours=policy.cache_ttl_hours or 24)
        existing = db.query(AIResponseCache).filter(AIResponseCache.cache_key == key).first()
        if existing:
            existing.response_payload = payload
            existing.expires_at = expires
            existing.model = model
            existing.provider = provider
            return

        db.add(
            AIResponseCache(
                cache_key=key,
                module=module,
                prompt_hash=prompt_hash(prompt),
                model=model,
                provider=provider,
                response_payload=payload,
                cost_saved_usd=cost_usd,
                expires_at=expires,
            )
        )

    @staticmethod
    def resolve_model_for_generation(db: Session, gen: AIGeneration) -> tuple[str | None, str | None]:
        module = gen.module.value if hasattr(gen.module, "value") else str(gen.module)
        policy = AICostService.get_policy(db, module)
        if not policy or not policy.enabled:
            return gen.provider, None

        selection = select_model(
            module,
            gen.prompt,
            selection_mode=policy.selection_mode,
            primary_model=policy.primary_model,
            primary_provider=policy.primary_provider,
            max_cost_per_request=float(policy.max_cost_per_request_usd) if policy.max_cost_per_request_usd else None,
        )
        return selection.provider, selection.model

    @staticmethod
    def get_fallback_chain(db: Session, module: str) -> list[dict[str, str]]:
        policy = AICostService.get_policy(db, module)
        if policy and policy.fallback_chain:
            return list(policy.fallback_chain)
        return list(DEFAULT_FALLBACK_CHAIN)

    @staticmethod
    def dashboard(db: Session, user: User, *, year: int | None = None, month: int | None = None) -> dict:
        StudioPlatformService.require_permission(db, user, None, "analytics.read")
        now = datetime.now(timezone.utc)
        y, m = year or now.year, month or now.month
        start = datetime(y, m, 1, tzinfo=timezone.utc)
        end = datetime(y + 1, 1, 1, tzinfo=timezone.utc) if m == 12 else datetime(y, m + 1, 1, tzinfo=timezone.utc)

        base = AICostService._spend_query(db, start, end)

        totals = base.with_entities(
            func.coalesce(func.sum(AIGeneration.input_tokens), 0),
            func.coalesce(func.sum(AIGeneration.output_tokens), 0),
            func.coalesce(func.sum(AIGeneration.cost_usd), 0),
            func.count(AIGeneration.id),
        ).one()

        cache_stats = (
            db.query(
                func.coalesce(func.sum(AIResponseCache.hit_count), 0),
                func.coalesce(func.sum(AIResponseCache.cost_saved_usd), 0),
            )
            .filter(AIResponseCache.created_at >= start, AIResponseCache.created_at < end)
            .one()
        )

        def _breakdown(group_col, label_fn=None):
            rows = (
                base.with_entities(
                    group_col,
                    func.coalesce(func.sum(AIGeneration.input_tokens), 0),
                    func.coalesce(func.sum(AIGeneration.output_tokens), 0),
                    func.coalesce(func.sum(AIGeneration.cost_usd), 0),
                    func.count(AIGeneration.id),
                )
                .group_by(group_col)
                .order_by(func.sum(AIGeneration.cost_usd).desc())
                .limit(25)
                .all()
            )
            items = []
            for key, inp, out, cost, cnt in rows:
                if key is None:
                    continue
                label = label_fn(key) if label_fn else str(key)
                items.append(
                    {
                        "key": str(key),
                        "label": label,
                        "input_tokens": int(inp),
                        "output_tokens": int(out),
                        "cost_usd": round(float(cost or 0), 4),
                        "request_count": int(cnt),
                    }
                )
            return items

        projects = {p.id: p.title for p in db.query(Production.id, Production.title).all()}
        users = {u.id: u.full_name or u.email for u in db.query(User.id, User.full_name, User.email).all()}

        budgets = db.query(AICostBudget).filter(AICostBudget.enabled.is_(True)).count()
        alerts = db.query(AICostAlert).filter(AICostAlert.acknowledged.is_(False)).count()

        by_module = _breakdown(AIGeneration.module)

        return {
            "period_start": start,
            "period_end": end,
            "total_input_tokens": int(totals[0]),
            "total_output_tokens": int(totals[1]),
            "total_cost_usd": round(float(totals[2] or 0), 4),
            "total_requests": int(totals[3]),
            "cache_hits": int(cache_stats[0]),
            "cache_savings_usd": round(float(cache_stats[1] or 0), 4),
            "by_project": _breakdown(AIGeneration.project_id, lambda k: projects.get(k, f"Project #{k}")),
            "by_user": _breakdown(AIGeneration.created_by_id, lambda k: users.get(k, f"User #{k}")),
            "by_model": _breakdown(AIGeneration.model),
            "by_provider": _breakdown(AIGeneration.provider),
            "by_module": by_module,
            "active_budgets": budgets,
            "unacknowledged_alerts": alerts,
        }

    @staticmethod
    def list_budgets(db: Session, user: User) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "admin.read")
        start, end = AICostService._month_bounds()
        rows = db.query(AICostBudget).order_by(AICostBudget.created_at.desc()).all()
        result = []
        for b in rows:
            spend = AICostService._budget_spend(db, b, start=start, end=end) or 0.0
            limit = float(b.monthly_limit_usd)
            result.append(
                {
                    "id": b.id,
                    "scope_type": b.scope_type,
                    "scope_id": b.scope_id,
                    "name": b.name,
                    "monthly_limit_usd": limit,
                    "alert_threshold_pct": b.alert_threshold_pct,
                    "hard_limit": b.hard_limit,
                    "enabled": b.enabled,
                    "current_spend_usd": round(spend, 4),
                    "utilization_pct": round(min(100, spend / limit * 100), 1) if limit else 0,
                    "created_at": b.created_at,
                }
            )
        return result

    @staticmethod
    def create_budget(db: Session, user: User, data: BudgetCreate) -> dict:
        StudioPlatformService.require_permission(db, user, None, "admin.manage")
        if data.scope_type != "global" and not data.scope_id:
            raise BadRequestError("scope_id required for organization/user/project budgets")
        budget = AICostBudget(
            scope_type=data.scope_type,
            scope_id=data.scope_id,
            name=data.name.strip(),
            monthly_limit_usd=data.monthly_limit_usd,
            alert_threshold_pct=data.alert_threshold_pct,
            hard_limit=data.hard_limit,
            enabled=data.enabled,
            created_by_id=user.id,
        )
        db.add(budget)
        db.commit()
        db.refresh(budget)
        start, end = AICostService._month_bounds()
        spend = AICostService._budget_spend(db, budget, start=start, end=end) or 0.0
        limit = float(budget.monthly_limit_usd)
        return {
            "id": budget.id,
            "scope_type": budget.scope_type,
            "scope_id": budget.scope_id,
            "name": budget.name,
            "monthly_limit_usd": limit,
            "alert_threshold_pct": budget.alert_threshold_pct,
            "hard_limit": budget.hard_limit,
            "enabled": budget.enabled,
            "current_spend_usd": round(spend, 4),
            "utilization_pct": round(min(100, spend / limit * 100), 1) if limit else 0,
            "created_at": budget.created_at,
        }

    @staticmethod
    def update_budget(db: Session, user: User, budget_id: int, data: BudgetUpdate) -> dict:
        StudioPlatformService.require_permission(db, user, None, "admin.manage")
        budget = db.query(AICostBudget).filter(AICostBudget.id == budget_id).first()
        if not budget:
            raise NotFoundError("Budget")
        if data.name is not None:
            budget.name = data.name.strip()
        if data.monthly_limit_usd is not None:
            budget.monthly_limit_usd = data.monthly_limit_usd
        if data.alert_threshold_pct is not None:
            budget.alert_threshold_pct = data.alert_threshold_pct
        if data.hard_limit is not None:
            budget.hard_limit = data.hard_limit
        if data.enabled is not None:
            budget.enabled = data.enabled
        db.commit()
        return next((b for b in AICostService.list_budgets(db, user) if b["id"] == budget_id), {})

    @staticmethod
    def delete_budget(db: Session, user: User, budget_id: int) -> None:
        StudioPlatformService.require_permission(db, user, None, "admin.manage")
        budget = db.query(AICostBudget).filter(AICostBudget.id == budget_id).first()
        if not budget:
            raise NotFoundError("Budget")
        db.delete(budget)
        db.commit()

    @staticmethod
    def list_policies(db: Session, user: User) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "admin.read")
        AICostService.ensure_policies(db)
        rows = db.query(AIModelPolicy).order_by(AIModelPolicy.module).all()
        return [
            {
                "id": p.id,
                "module": p.module,
                "selection_mode": p.selection_mode,
                "primary_model": p.primary_model,
                "primary_provider": p.primary_provider,
                "fallback_chain": p.fallback_chain or [],
                "max_cost_per_request_usd": float(p.max_cost_per_request_usd) if p.max_cost_per_request_usd else None,
                "cache_enabled": p.cache_enabled,
                "cache_ttl_hours": p.cache_ttl_hours,
                "enabled": p.enabled,
            }
            for p in rows
        ]

    @staticmethod
    def update_policy(db: Session, user: User, module: str, data: ModelPolicyUpdate) -> dict:
        StudioPlatformService.require_permission(db, user, None, "admin.manage")
        AICostService.ensure_policies(db)
        policy = db.query(AIModelPolicy).filter(AIModelPolicy.module == module).first()
        if not policy:
            policy = AIModelPolicy(module=module)
            db.add(policy)
            db.flush()
        if data.selection_mode is not None:
            policy.selection_mode = data.selection_mode
        if data.primary_model is not None:
            policy.primary_model = data.primary_model
        if data.primary_provider is not None:
            policy.primary_provider = data.primary_provider
        if data.fallback_chain is not None:
            policy.fallback_chain = data.fallback_chain
        if data.max_cost_per_request_usd is not None:
            policy.max_cost_per_request_usd = data.max_cost_per_request_usd
        if data.cache_enabled is not None:
            policy.cache_enabled = data.cache_enabled
        if data.cache_ttl_hours is not None:
            policy.cache_ttl_hours = data.cache_ttl_hours
        if data.enabled is not None:
            policy.enabled = data.enabled
        db.commit()
        return next((p for p in AICostService.list_policies(db, user) if p["module"] == module), {})

    @staticmethod
    def list_alerts(db: Session, user: User, *, acknowledged: bool | None = None) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "analytics.read")
        q = db.query(AICostAlert, AICostBudget).join(AICostBudget, AICostBudget.id == AICostAlert.budget_id)
        if acknowledged is not None:
            q = q.filter(AICostAlert.acknowledged == acknowledged)
        rows = q.order_by(AICostAlert.created_at.desc()).limit(100).all()
        return [
            {
                "id": a.id,
                "budget_id": a.budget_id,
                "budget_name": b.name,
                "alert_type": a.alert_type,
                "threshold_pct": a.threshold_pct,
                "spend_usd": float(a.spend_usd),
                "limit_usd": float(a.limit_usd),
                "message": a.message,
                "acknowledged": a.acknowledged,
                "created_at": a.created_at,
            }
            for a, b in rows
        ]

    @staticmethod
    def acknowledge_alert(db: Session, user: User, alert_id: int) -> dict:
        StudioPlatformService.require_permission(db, user, None, "admin.read")
        alert = db.query(AICostAlert).filter(AICostAlert.id == alert_id).first()
        if not alert:
            raise NotFoundError("Alert")
        alert.acknowledged = True
        db.commit()
        return {"id": alert.id, "acknowledged": True}

    @staticmethod
    def generate_monthly_report(
        db: Session,
        user: User,
        *,
        year: int,
        month: int,
        scope_type: str = "global",
        scope_id: int | None = None,
    ) -> dict:
        StudioPlatformService.require_permission(db, user, None, "analytics.read")
        dash = AICostService.dashboard(db, user, year=year, month=month)
        report_data = {
            **dash,
            "generated_by": user.id,
            "scope_type": scope_type,
            "scope_id": scope_id,
        }
        existing = (
            db.query(AIMonthlyCostReport)
            .filter(
                AIMonthlyCostReport.year == year,
                AIMonthlyCostReport.month == month,
                AIMonthlyCostReport.scope_type == scope_type,
                AIMonthlyCostReport.scope_id == scope_id,
            )
            .first()
        )
        if existing:
            existing.report_data = report_data
            existing.generated_at = datetime.now(timezone.utc)
            existing.generated_by_id = user.id
            db.commit()
            db.refresh(existing)
            row = existing
        else:
            row = AIMonthlyCostReport(
                year=year,
                month=month,
                scope_type=scope_type,
                scope_id=scope_id,
                report_data=report_data,
                generated_by_id=user.id,
            )
            db.add(row)
            db.commit()
            db.refresh(row)

        return {
            "id": row.id,
            "year": row.year,
            "month": row.month,
            "scope_type": row.scope_type,
            "scope_id": row.scope_id,
            "report_data": row.report_data,
            "generated_at": row.generated_at,
        }

    @staticmethod
    def list_monthly_reports(db: Session, user: User, limit: int = 12) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "analytics.read")
        rows = (
            db.query(AIMonthlyCostReport)
            .order_by(AIMonthlyCostReport.year.desc(), AIMonthlyCostReport.month.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": r.id,
                "year": r.year,
                "month": r.month,
                "scope_type": r.scope_type,
                "scope_id": r.scope_id,
                "report_data": r.report_data,
                "generated_at": r.generated_at,
            }
            for r in rows
        ]

    @staticmethod
    def cache_stats(db: Session, user: User) -> dict:
        StudioPlatformService.require_permission(db, user, None, "analytics.read")
        now = datetime.now(timezone.utc)
        active = db.query(AIResponseCache).filter(AIResponseCache.expires_at > now).count()
        totals = db.query(
            func.coalesce(func.sum(AIResponseCache.hit_count), 0),
            func.coalesce(func.sum(AIResponseCache.cost_saved_usd), 0),
        ).one()
        return {
            "active_entries": active,
            "total_hits": int(totals[0]),
            "total_savings_usd": round(float(totals[1] or 0), 4),
        }
