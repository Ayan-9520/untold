"""Agent analytics and monitoring."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import User
from app.models.studio_platform import AgentExecutionLog, AgentInstallation, AgentMessage, MarketplaceAgent
from app.services.agent_marketplace_service import AgentMarketplaceService
from app.services.studio_platform_service import StudioPlatformService


class AgentAnalyticsService:
    @staticmethod
    def monitoring_overview(db: Session, user: User) -> dict:
        StudioPlatformService.require_permission(db, user, None, "analytics.read")
        AgentMarketplaceService.ensure_catalog(db)
        now = datetime.now(timezone.utc)
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        installations = (
            db.query(AgentInstallation)
            .filter(AgentInstallation.user_id == user.id)
            .all()
        )
        enabled = sum(1 for i in installations if i.enabled)

        runs_today = (
            db.query(AgentExecutionLog)
            .filter(AgentExecutionLog.user_id == user.id, AgentExecutionLog.created_at >= day_start)
            .count()
        )
        failed_today = (
            db.query(AgentExecutionLog)
            .filter(
                AgentExecutionLog.user_id == user.id,
                AgentExecutionLog.created_at >= day_start,
                AgentExecutionLog.status == "failed",
            )
            .count()
        )
        cost_today = (
            db.query(func.coalesce(func.sum(AgentExecutionLog.cost_usd), 0))
            .filter(AgentExecutionLog.user_id == user.id, AgentExecutionLog.created_at >= day_start)
            .scalar()
        )
        pending_messages = (
            db.query(AgentMessage)
            .join(AgentInstallation, AgentMessage.to_installation_id == AgentInstallation.id)
            .filter(AgentInstallation.user_id == user.id, AgentMessage.status == "pending")
            .count()
        )

        by_agent = (
            db.query(
                AgentExecutionLog.agent_slug,
                func.count(AgentExecutionLog.id),
                func.coalesce(func.sum(AgentExecutionLog.cost_usd), 0),
            )
            .filter(AgentExecutionLog.user_id == user.id, AgentExecutionLog.created_at >= day_start)
            .group_by(AgentExecutionLog.agent_slug)
            .order_by(func.count(AgentExecutionLog.id).desc())
            .limit(15)
            .all()
        )

        recent_logs = (
            db.query(AgentExecutionLog)
            .filter(AgentExecutionLog.user_id == user.id)
            .order_by(AgentExecutionLog.created_at.desc())
            .limit(20)
            .all()
        )

        return {
            "installed_count": len(installations),
            "enabled_count": enabled,
            "runs_today": runs_today,
            "failed_today": failed_today,
            "cost_today_usd": round(float(cost_today or 0), 4),
            "pending_messages": pending_messages,
            "by_agent": [
                {"slug": slug, "runs": int(cnt), "cost_usd": round(float(cost or 0), 4)}
                for slug, cnt, cost in by_agent
            ],
            "recent_logs": [AgentAnalyticsService._log_dict(r) for r in recent_logs],
        }

    @staticmethod
    def installation_analytics(db: Session, user: User, installation_id: int) -> dict:
        StudioPlatformService.require_permission(db, user, None, "analytics.read")
        inst = (
            db.query(AgentInstallation)
            .filter(AgentInstallation.id == installation_id, AgentInstallation.user_id == user.id)
            .first()
        )
        if not inst:
            from app.core.exceptions import NotFoundError

            raise NotFoundError("Installation")
        agent = db.query(MarketplaceAgent).filter(MarketplaceAgent.id == inst.agent_id).first()
        totals = (
            db.query(
                func.count(AgentExecutionLog.id),
                func.coalesce(func.sum(AgentExecutionLog.cost_usd), 0),
                func.coalesce(func.sum(AgentExecutionLog.input_tokens), 0),
                func.coalesce(func.sum(AgentExecutionLog.output_tokens), 0),
            )
            .filter(AgentExecutionLog.installation_id == installation_id)
            .one()
        )
        return {
            "installation_id": installation_id,
            "agent_slug": agent.slug if agent else "",
            "total_runs": int(totals[0] or 0),
            "total_cost_usd": round(float(totals[1] or 0), 4),
            "total_input_tokens": int(totals[2] or 0),
            "total_output_tokens": int(totals[3] or 0),
        }

    @staticmethod
    def execution_logs(
        db: Session,
        user: User,
        *,
        installation_id: int | None = None,
        agent_slug: str | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
        StudioPlatformService.require_permission(db, user, None, "analytics.read")
        q = db.query(AgentExecutionLog).filter(AgentExecutionLog.user_id == user.id)
        if installation_id:
            q = q.filter(AgentExecutionLog.installation_id == installation_id)
        if agent_slug:
            q = q.filter(AgentExecutionLog.agent_slug == agent_slug)
        if status:
            q = q.filter(AgentExecutionLog.status == status)
        total = q.count()
        rows = q.order_by(AgentExecutionLog.created_at.desc()).offset(offset).limit(limit).all()
        return {
            "items": [AgentAnalyticsService._log_dict(r) for r in rows],
            "total": total,
        }

    @staticmethod
    def _log_dict(r: AgentExecutionLog) -> dict:
        return {
            "id": r.id,
            "installation_id": r.installation_id,
            "agent_slug": r.agent_slug,
            "status": r.status,
            "duration_ms": r.duration_ms,
            "input_tokens": r.input_tokens,
            "output_tokens": r.output_tokens,
            "cost_usd": float(r.cost_usd or 0),
            "message": r.message,
            "project_id": r.project_id,
            "generation_id": r.generation_id,
            "created_at": r.created_at,
        }
