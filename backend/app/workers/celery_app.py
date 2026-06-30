"""Celery worker — background jobs for AI agents, news, social publishing."""

from datetime import timedelta

from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "untold",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.tasks", "app.workers.studio_tasks", "app.workers.publish_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    beat_schedule={
        "fetch-news-sources": {
            "task": "untold.fetch_news_sources",
            "schedule": crontab(minute=f"*/{max(1, settings.news_fetch_interval_minutes)}"),
        },
        "process-news-ai": {
            "task": "untold.process_pending_news_ai",
            "schedule": crontab(minute="*/5"),
        },
        "sync-live-matches": {
            "task": "untold.sync_live_matches",
            "schedule": timedelta(seconds=max(15, settings.live_sync_interval_seconds)),
        },
        "process-due-publish-runs": {
            "task": "untold.process_due_publish_runs",
            "schedule": crontab(minute="*/2"),
        },
        "process-workflow-cron-triggers": {
            "task": "untold.process_workflow_cron_triggers",
            "schedule": crontab(minute="*"),
        },
        "process-scheduled-workflow-runs": {
            "task": "untold.process_scheduled_workflow_runs",
            "schedule": crontab(minute="*"),
        },
        "generate-ai-monthly-cost-reports": {
            "task": "untold.generate_ai_monthly_cost_reports",
            "schedule": crontab(day_of_month="1", hour="6", minute="0"),
        },
    },
)
