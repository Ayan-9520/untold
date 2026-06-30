"""Workflow triggers — webhook, API, cron, manual."""

from __future__ import annotations

import secrets
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError
from app.models import User
from app.models.studio_platform import WorkflowDefinition, WorkflowTrigger
from app.schemas.workflow_builder import WorkflowExecuteRequest, WorkflowTriggerCreate, WorkflowTriggerUpdate
from app.services.workflow_builder_service import WorkflowBuilderService
from app.services.studio_platform_service import StudioPlatformService


def _compute_next_cron(cron_expression: str, *, base: datetime | None = None) -> datetime:
    try:
        from croniter import croniter
    except ImportError as exc:
        raise BadRequestError("Cron triggers require croniter package") from exc
    base = base or datetime.now(timezone.utc)
    itr = croniter(cron_expression, base)
    nxt = itr.get_next(datetime)
    if nxt.tzinfo is None:
        return nxt.replace(tzinfo=timezone.utc)
    return nxt


class WorkflowTriggerService:
    @staticmethod
    def _trigger_dict(trigger: WorkflowTrigger, *, reveal_secret: bool = False) -> dict:
        return {
            "id": trigger.id,
            "definition_id": trigger.definition_id,
            "version_id": trigger.version_id,
            "trigger_type": trigger.trigger_type,
            "name": trigger.name,
            "enabled": trigger.enabled,
            "config": trigger.config or {},
            "webhook_secret": trigger.webhook_secret if reveal_secret else ("***" if trigger.webhook_secret else None),
            "cron_expression": trigger.cron_expression,
            "next_run_at": trigger.next_run_at,
            "last_run_at": trigger.last_run_at,
            "created_at": trigger.created_at,
        }

    @staticmethod
    def list_triggers(db: Session, user: User, definition_id: int) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        rows = (
            db.query(WorkflowTrigger)
            .filter(WorkflowTrigger.definition_id == definition_id)
            .order_by(WorkflowTrigger.created_at.desc())
            .all()
        )
        return [WorkflowTriggerService._trigger_dict(t) for t in rows]

    @staticmethod
    def create_trigger(db: Session, user: User, definition_id: int, data: WorkflowTriggerCreate) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        defn = db.query(WorkflowDefinition).filter(WorkflowDefinition.id == definition_id).first()
        if not defn:
            raise NotFoundError("Workflow definition")

        webhook_secret = None
        next_run_at = None
        if data.trigger_type == "webhook":
            webhook_secret = secrets.token_urlsafe(32)
        if data.trigger_type == "cron":
            if not data.cron_expression:
                raise BadRequestError("cron_expression required for cron triggers")
            next_run_at = _compute_next_cron(data.cron_expression)

        trigger = WorkflowTrigger(
            definition_id=definition_id,
            version_id=data.version_id or defn.current_version_id,
            trigger_type=data.trigger_type,
            name=data.name.strip(),
            enabled=data.enabled,
            config=data.config,
            webhook_secret=webhook_secret,
            cron_expression=data.cron_expression,
            next_run_at=next_run_at,
            created_by_id=user.id,
        )
        db.add(trigger)
        db.commit()
        db.refresh(trigger)
        return WorkflowTriggerService._trigger_dict(trigger, reveal_secret=True)

    @staticmethod
    def update_trigger(db: Session, user: User, definition_id: int, trigger_id: int, data: WorkflowTriggerUpdate) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        trigger = (
            db.query(WorkflowTrigger)
            .filter(WorkflowTrigger.id == trigger_id, WorkflowTrigger.definition_id == definition_id)
            .first()
        )
        if not trigger:
            raise NotFoundError("Workflow trigger")
        if data.name is not None:
            trigger.name = data.name.strip()
        if data.enabled is not None:
            trigger.enabled = data.enabled
        if data.version_id is not None:
            trigger.version_id = data.version_id
        if data.config is not None:
            trigger.config = data.config
        if data.cron_expression is not None:
            trigger.cron_expression = data.cron_expression
            if trigger.trigger_type == "cron":
                trigger.next_run_at = _compute_next_cron(data.cron_expression)
        db.commit()
        db.refresh(trigger)
        return WorkflowTriggerService._trigger_dict(trigger)

    @staticmethod
    def delete_trigger(db: Session, user: User, definition_id: int, trigger_id: int) -> None:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        trigger = (
            db.query(WorkflowTrigger)
            .filter(WorkflowTrigger.id == trigger_id, WorkflowTrigger.definition_id == definition_id)
            .first()
        )
        if not trigger:
            raise NotFoundError("Workflow trigger")
        db.delete(trigger)
        db.commit()

    @staticmethod
    def fire_webhook(db: Session, secret: str, payload: dict) -> dict:
        trigger = (
            db.query(WorkflowTrigger)
            .filter(
                WorkflowTrigger.webhook_secret == secret,
                WorkflowTrigger.trigger_type == "webhook",
                WorkflowTrigger.enabled.is_(True),
            )
            .first()
        )
        if not trigger:
            raise NotFoundError("Webhook trigger")

        topic = (payload.get("topic") or trigger.config.get("default_topic") or "Webhook workflow run").strip()
        project_id = payload.get("project_id") or trigger.config.get("project_id")
        execute = WorkflowExecuteRequest(
            topic=topic[:500],
            project_id=project_id,
            version_id=trigger.version_id,
            trigger_type="webhook",
            auto_run=True,
            providers=payload.get("providers") or {},
            publish_platforms=payload.get("publish_platforms") or ["originals", "youtube"],
            translation_language=payload.get("translation_language"),
            prompts=payload.get("prompts"),
        )
        run = WorkflowBuilderService.execute_definition(db, None, trigger.definition_id, execute, trigger=trigger)
        trigger.last_run_at = datetime.now(timezone.utc)
        db.commit()
        return {"run_id": run.id, "status": run.status}

    @staticmethod
    def process_due_cron_triggers(db: Session) -> int:
        now = datetime.now(timezone.utc)
        triggers = (
            db.query(WorkflowTrigger)
            .filter(
                WorkflowTrigger.trigger_type == "cron",
                WorkflowTrigger.enabled.is_(True),
                WorkflowTrigger.next_run_at.isnot(None),
                WorkflowTrigger.next_run_at <= now,
            )
            .all()
        )
        fired = 0
        for trigger in triggers:
            topic = trigger.config.get("default_topic") or f"Cron: {trigger.name}"
            execute = WorkflowExecuteRequest(
                topic=topic,
                project_id=trigger.config.get("project_id"),
                version_id=trigger.version_id,
                trigger_type="cron",
                auto_run=True,
            )
            WorkflowBuilderService.execute_definition(db, None, trigger.definition_id, execute, trigger=trigger)
            trigger.last_run_at = now
            if trigger.cron_expression:
                trigger.next_run_at = _compute_next_cron(trigger.cron_expression, base=now)
            fired += 1
        db.commit()
        return fired

    @staticmethod
    def process_scheduled_runs(db: Session) -> int:
        now = datetime.now(timezone.utc)
        from app.models.studio_platform import ProductionPipelineRun
        from app.services.production_pipeline_service import ProductionPipelineService

        runs = (
            db.query(ProductionPipelineRun)
            .filter(
                ProductionPipelineRun.status == "scheduled",
                ProductionPipelineRun.scheduled_at.isnot(None),
                ProductionPipelineRun.scheduled_at <= now,
            )
            .all()
        )
        started = 0
        for run in runs:
            run.status = "queued"
            ProductionPipelineService._dispatch(db, run, run.created_by_id)
            started += 1
        db.commit()
        return started
