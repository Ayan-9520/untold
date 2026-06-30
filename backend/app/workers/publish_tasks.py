"""Celery tasks for publishing agent."""

import logging

from app.db.session import SessionLocal
from app.services.publishing_agent_service import PublishingAgentService
from app.workers.celery_app import celery_app

logger = logging.getLogger("untold.publishing.tasks")


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60, name="untold.process_publish_agent_run")
def process_publish_agent_run(self, run_id: int) -> dict:
    db = SessionLocal()
    try:
        result = PublishingAgentService.execute_run(db, run_id)
        return result
    except Exception as exc:
        logger.exception("Publish agent run %s failed", run_id)
        raise self.retry(exc=exc) from exc
    finally:
        db.close()


@celery_app.task(name="untold.process_due_publish_runs")
def process_due_publish_runs() -> dict:
    db = SessionLocal()
    try:
        return PublishingAgentService.process_due_scheduled(db)
    finally:
        db.close()
