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
    include=["app.workers.tasks"],
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
    },
)
