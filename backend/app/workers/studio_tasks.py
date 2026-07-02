"""Celery tasks for UNTOLD Studio AI pipelines."""

import logging

from app.db.session import SessionLocal
from app.domain.studio.enums import AIGenerationStatus
from app.models.studio_platform import AIGeneration
from app.services.ai_studio_service import AIStudioService
from app.workers.celery_app import celery_app

logger = logging.getLogger("untold.studio.tasks")


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def run_ai_generation(self, generation_id: int) -> dict:
    db = SessionLocal()
    try:
        gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
        if not gen:
            return {"error": "not_found"}
        if gen.status == AIGenerationStatus.CANCELLED:
            return {"id": generation_id, "status": "cancelled"}

        AIStudioService.execute_job(db, generation_id)
        gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
        return {"id": generation_id, "status": gen.status.value if gen else "unknown"}
    except Exception as exc:
        logger.exception("AI generation %s failed", generation_id)
        gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
        if gen and gen.status != AIGenerationStatus.CANCELLED:
            gen.status = AIGenerationStatus.FAILED
            gen.error = str(exc)
            db.commit()
        raise self.retry(exc=exc) from exc
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=1, default_retry_delay=60)
def run_production_pipeline(self, run_id: int) -> dict:
    db = SessionLocal()
    try:
        from app.services.production_pipeline_service import ProductionPipelineService

        ProductionPipelineService.execute_run(db, run_id)
        return {"id": run_id, "status": "completed"}
    except Exception as exc:
        logger.exception("Production pipeline %s failed", run_id)
        raise self.retry(exc=exc) from exc
    finally:
        db.close()


@celery_app.task(name="untold.aggregate_bi_daily_snapshots")
def aggregate_bi_daily_snapshots() -> dict:
    db = SessionLocal()
    try:
        from app.services.bi_aggregation_service import BIAggregationService

        return BIAggregationService.aggregate_daily(db)
    finally:
        db.close()


@celery_app.task(name="untold.process_scheduled_bi_reports")
def process_scheduled_bi_reports() -> dict:
    db = SessionLocal()
    try:
        from app.services.bi_report_service import BIReportService

        fired = BIReportService.process_due_schedules(db)
        return {"fired": fired}
    finally:
        db.close()


@celery_app.task(name="untold.process_agent_schedules")
def process_agent_schedules() -> dict:
    db = SessionLocal()
    try:
        from app.services.agent_scheduler_service import AgentSchedulerService

        fired = AgentSchedulerService.process_due_schedules(db)
        return {"fired": fired}
    finally:
        db.close()


@celery_app.task(name="untold.process_workflow_cron_triggers")
def process_workflow_cron_triggers() -> dict:
    db = SessionLocal()
    try:
        from app.services.workflow_trigger_service import WorkflowTriggerService

        fired = WorkflowTriggerService.process_due_cron_triggers(db)
        return {"fired": fired}
    finally:
        db.close()


@celery_app.task(name="untold.process_scheduled_workflow_runs")
def process_scheduled_workflow_runs() -> dict:
    db = SessionLocal()
    try:
        from app.services.workflow_trigger_service import WorkflowTriggerService

        started = WorkflowTriggerService.process_scheduled_runs(db)
        return {"started": started}
    finally:
        db.close()


@celery_app.task(name="untold.generate_ai_monthly_cost_reports")
def generate_ai_monthly_cost_reports() -> dict:
    db = SessionLocal()
    try:
        from datetime import datetime, timezone

        from app.models import User
        from app.services.ai_cost_service import AICostService

        admin = db.query(User).filter(User.is_admin.is_(True)).order_by(User.id).first()
        if not admin:
            return {"generated": 0}
        now = datetime.now(timezone.utc)
        prev_month = now.month - 1 if now.month > 1 else 12
        prev_year = now.year if now.month > 1 else now.year - 1
        AICostService.generate_monthly_report(db, admin, year=prev_year, month=prev_month)
        return {"generated": 1, "year": prev_year, "month": prev_month}
    finally:
        db.close()
