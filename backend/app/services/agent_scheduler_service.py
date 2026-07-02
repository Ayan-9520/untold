"""Agent scheduling — per-installation cron jobs."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError
from app.models import User
from app.models.studio_platform import AgentSchedule
from app.services.agent_runtime_service import AgentRuntimeService
from app.services.studio_platform_service import StudioPlatformService


def _compute_next_cron(cron_expression: str, *, base: datetime | None = None) -> datetime:
    from croniter import croniter

    base = base or datetime.now(timezone.utc)
    nxt = croniter(cron_expression, base).get_next(datetime)
    if nxt.tzinfo is None:
        return nxt.replace(tzinfo=timezone.utc)
    return nxt


class AgentSchedulerService:
    @staticmethod
    def list_schedules(db: Session, user: User, installation_id: int) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        rows = (
            db.query(AgentSchedule)
            .filter(AgentSchedule.installation_id == installation_id)
            .order_by(AgentSchedule.created_at.desc())
            .all()
        )
        return [AgentSchedulerService._schedule_dict(s) for s in rows]

    @staticmethod
    def create_schedule(
        db: Session,
        user: User,
        installation_id: int,
        *,
        name: str,
        cron_expression: str,
        payload: dict | None = None,
    ) -> dict:
        from app.services.agent_memory_service import AgentMemoryService

        slug = AgentMemoryService._slug_for_installation(db, installation_id, user.id)
        ctx = AgentRuntimeService.build_context(db, user.id, slug)
        AgentRuntimeService.require_permission(ctx, "schedule.manage")
        try:
            next_run = _compute_next_cron(cron_expression)
        except Exception as exc:
            raise BadRequestError(f"Invalid cron expression: {exc}") from exc
        row = AgentSchedule(
            installation_id=installation_id,
            name=name.strip(),
            cron_expression=cron_expression,
            payload=payload or {},
            next_run_at=next_run,
            created_by_id=user.id,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return AgentSchedulerService._schedule_dict(row)

    @staticmethod
    def delete_schedule(db: Session, user: User, installation_id: int, schedule_id: int) -> None:
        row = (
            db.query(AgentSchedule)
            .filter(AgentSchedule.id == schedule_id, AgentSchedule.installation_id == installation_id)
            .first()
        )
        if not row:
            raise NotFoundError("Schedule")
        db.delete(row)
        db.commit()

    @staticmethod
    def process_due_schedules(db: Session) -> int:
        now = datetime.now(timezone.utc)
        schedules = (
            db.query(AgentSchedule)
            .filter(
                AgentSchedule.enabled.is_(True),
                AgentSchedule.next_run_at.isnot(None),
                AgentSchedule.next_run_at <= now,
            )
            .all()
        )
        fired = 0
        for sched in schedules:
            from app.models.studio_platform import AgentInstallation, MarketplaceAgent

            inst = db.query(AgentInstallation).filter(AgentInstallation.id == sched.installation_id).first()
            if not inst or not inst.enabled:
                continue
            agent = db.query(MarketplaceAgent).filter(MarketplaceAgent.id == inst.agent_id).first()
            if not agent:
                continue
            ctx = AgentRuntimeService.build_context(db, inst.user_id, agent.slug)
            payload = dict(sched.payload or {})
            timer = AgentRuntimeService.execution_timer()
            try:
                result = AgentRuntimeService.run_registered_agent(ctx, payload)
                AgentRuntimeService.log_execution(
                    db,
                    agent_slug=agent.slug,
                    installation_id=inst.id,
                    user_id=inst.user_id,
                    organization_id=inst.organization_id,
                    status="success",
                    duration_ms=timer.elapsed_ms(),
                    message=f"Scheduled run: {sched.name}",
                    meta={"schedule_id": sched.id, "result": result},
                )
            except Exception as exc:
                AgentRuntimeService.log_execution(
                    db,
                    agent_slug=agent.slug,
                    installation_id=inst.id,
                    user_id=inst.user_id,
                    status="failed",
                    duration_ms=timer.elapsed_ms(),
                    message=str(exc)[:500],
                    meta={"schedule_id": sched.id},
                )
            sched.last_run_at = now
            sched.next_run_at = _compute_next_cron(sched.cron_expression, base=now)
            fired += 1
        db.commit()
        return fired

    @staticmethod
    def _schedule_dict(s: AgentSchedule) -> dict:
        return {
            "id": s.id,
            "installation_id": s.installation_id,
            "name": s.name,
            "enabled": s.enabled,
            "cron_expression": s.cron_expression,
            "payload": s.payload or {},
            "next_run_at": s.next_run_at,
            "last_run_at": s.last_run_at,
            "created_at": s.created_at,
        }
