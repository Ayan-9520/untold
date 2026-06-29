"""Background tasks — news engine, AI agents, social publishing."""

import logging

from app.db.session import SessionLocal
from app.services.news_ai_service import NewsAIService
from app.services.news_fetch_service import NewsFetchService
from app.workers.celery_app import celery_app

logger = logging.getLogger("untold")


@celery_app.task(name="untold.fetch_news_sources")
def fetch_news_sources() -> dict:
    db = SessionLocal()
    try:
        count = NewsFetchService.fetch_all_active(db)
        logger.info("Fetched %d new articles", count)
        if count:
            process_pending_news_ai.delay()
        return {"status": "completed", "articles_created": count}
    finally:
        db.close()


@celery_app.task(name="untold.process_pending_news_ai")
def process_pending_news_ai(limit: int = 20) -> dict:
    from app.models.news import NewsArticle, NewsStatus

    db = SessionLocal()
    processed = 0
    try:
        articles = (
            db.query(NewsArticle)
            .filter(NewsArticle.status == NewsStatus.DRAFT, NewsArticle.ai_processed_at.is_(None))
            .order_by(NewsArticle.created_at.asc())
            .limit(limit)
            .all()
        )
        for article in articles:
            NewsAIService.process_article(db, article)
            processed += 1
        return {"status": "completed", "processed": processed}
    finally:
        db.close()


@celery_app.task(name="untold.generate_news_summary")
def generate_news_summary(article_id: int) -> dict:
    db = SessionLocal()
    try:
        from app.services.news_service import NewsService

        article = NewsService.get_admin_by_id(db, article_id)
        NewsAIService.process_article(db, article)
        return {"article_id": article_id, "status": "completed"}
    finally:
        db.close()


@celery_app.task(name="untold.publish_social_reel")
def publish_social_reel(video_id: int, platform: str) -> dict:
    return {"video_id": video_id, "platform": platform, "status": "queued"}


@celery_app.task(name="untold.localize_content")
def localize_content(job_id: int) -> dict:
    return {"job_id": job_id, "status": "processing"}


@celery_app.task(name="untold.sync_live_matches")
def sync_live_matches() -> dict:
    from app.services.live_sync_service import LiveSyncService

    db = SessionLocal()
    try:
        result = LiveSyncService.sync_all(db)
        logger.info("Live sync complete: %s", result)
        return {"status": "completed", **result}
    finally:
        db.close()
