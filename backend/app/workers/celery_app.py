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
    include=["app.workers.tasks", "app.workers.studio_tasks", "app.workers.publish_tasks", "app.workers.billing_tasks", "app.workers.compliance_tasks"],
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
        "process-agent-schedules": {
            "task": "untold.process_agent_schedules",
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
        "retry-failed-billing-payments": {
            "task": "untold.retry_failed_billing_payments",
            "schedule": crontab(hour="*/6", minute="15"),
        },
        "aggregate-billing-usage": {
            "task": "untold.aggregate_billing_usage",
            "schedule": crontab(hour="2", minute="0"),
        },
        "aggregate-bi-daily-snapshots": {
            "task": "untold.aggregate_bi_daily_snapshots",
            "schedule": crontab(hour="3", minute="0"),
        },
        "process-scheduled-bi-reports": {
            "task": "untold.process_scheduled_bi_reports",
            "schedule": crontab(minute="*/15"),
        },
        "compliance-retention-purge": {
            "task": "untold.compliance_retention_purge",
            "schedule": crontab(hour="4", minute="0"),
        },
    },
)
