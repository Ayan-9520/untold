"""Fetch news from RSS, SportMonks, Sportradar, and CricAPI."""

import hashlib
import json
import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import httpx
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.news import NewsArticle, NewsSource, NewsSourceType, NewsStatus, NewsType
from app.utils.text import slugify

logger = logging.getLogger("untold")
settings = get_settings()


class NewsFetchService:
    @staticmethod
    def fetch_all_active(db: Session) -> int:
        sources = db.query(NewsSource).filter(NewsSource.is_active.is_(True)).all()
        queued = 0
        for source in sources:
            try:
                count = NewsFetchService.fetch_source(db, source)
                source.last_fetched_at = datetime.now(timezone.utc)
                source.last_error = None
                queued += count
            except Exception as exc:
                logger.exception("Failed to fetch source %s: %s", source.name, exc)
                source.last_error = str(exc)[:500]
            db.commit()
        return queued

    @staticmethod
    def fetch_source(db: Session, source: NewsSource) -> int:
        if source.source_type == NewsSourceType.RSS:
            return NewsFetchService._fetch_rss(db, source)
        if source.source_type == NewsSourceType.SPORTMONKS:
            return NewsFetchService._fetch_sportmonks(db, source)
        if source.source_type == NewsSourceType.SPORTRADAR:
            return NewsFetchService._fetch_sportradar(db, source)
        if source.source_type == NewsSourceType.CRICAPI:
            return NewsFetchService._fetch_cricapi(db, source)
        return 0

    @staticmethod
    def _fetch_rss(db: Session, source: NewsSource) -> int:
        import feedparser

        if not source.url:
            return 0

        feed = feedparser.parse(source.url)
        created = 0
        sport = source.sport or "Sports"

        for entry in feed.entries[:20]:
            external_id = entry.get("id") or entry.get("link") or hashlib.md5(
                entry.get("title", "").encode()
            ).hexdigest()
            exists = (
                db.query(NewsArticle)
                .filter(NewsArticle.source_id == source.id, NewsArticle.external_id == external_id)
                .first()
            )
            if exists:
                continue

            title = entry.get("title", "Untitled").strip()
            summary = entry.get("summary", entry.get("description", "")) or ""
            content = summary
            if hasattr(entry, "content") and entry.content:
                content = entry.content[0].get("value", summary)

            published = None
            if entry.get("published"):
                try:
                    published = parsedate_to_datetime(entry.published)
                except (TypeError, ValueError):
                    published = None

            news_type = NewsFetchService._infer_type(title, summary)
            article = NewsArticle(
                slug=NewsFetchService._unique_slug(db, title),
                title=title,
                excerpt=summary[:500] if summary else None,
                content=content,
                sport=sport,
                news_type=news_type,
                status=NewsStatus.DRAFT,
                is_breaking=news_type == NewsType.BREAKING,
                is_trending=False,
                thumbnail_url=NewsFetchService._extract_image(entry),
                source_url=entry.get("link"),
                external_id=external_id,
                source_id=source.id,
                author=entry.get("author", "UNTOLD Wire"),
                published_at=published,
            )
            db.add(article)
            created += 1

        db.flush()
        return created

    @staticmethod
    def _fetch_sportmonks(db: Session, source: NewsSource) -> int:
        api_key = settings.sportmonks_api_key
        if not api_key:
            logger.info("SportMonks API key not configured, skipping %s", source.name)
            return 0

        url = source.url or "https://api.sportmonks.com/v3/football/news"
        params = {"api_token": api_key}
        with httpx.Client(timeout=30) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()

        items = payload.get("data", payload.get("news", []))
        return NewsFetchService._ingest_provider_items(db, source, items, id_key="id", sport=source.sport or "Football")

    @staticmethod
    def _fetch_sportradar(db: Session, source: NewsSource) -> int:
        api_key = settings.sportradar_api_key
        if not api_key:
            logger.info("Sportradar API key not configured, skipping %s", source.name)
            return 0

        base = source.url or "https://api.sportradar.com/soccer/trial/v4/en"
        url = f"{base}/schedules/live/summaries.json"
        params = {"api_key": api_key}
        with httpx.Client(timeout=30) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()

        items = []
        for summary in payload.get("summaries", [])[:15]:
            sport_event = summary.get("sport_event", {})
            status = summary.get("sport_event_status", {})
            home = sport_event.get("competitors", [{}])[0].get("name", "Home")
            away = sport_event.get("competitors", [{}, {}])[1].get("name", "Away") if len(
                sport_event.get("competitors", [])
            ) > 1 else "Away"
            score_home = status.get("home_score", 0)
            score_away = status.get("away_score", 0)
            items.append(
                {
                    "id": sport_event.get("id"),
                    "title": f"{home} {score_home} - {score_away} {away}",
                    "summary": f"Live match update: {home} vs {away}",
                    "link": None,
                }
            )

        return NewsFetchService._ingest_provider_items(
            db, source, items, id_key="id", sport=source.sport or "Football", news_type=NewsType.MATCH_UPDATE
        )

    @staticmethod
    def _fetch_cricapi(db: Session, source: NewsSource) -> int:
        api_key = settings.cricapi_api_key
        if not api_key:
            logger.info("CricAPI key not configured, skipping %s", source.name)
            return 0

        url = source.url or "https://api.cricapi.com/v1/currentMatches"
        params = {"apikey": api_key}
        with httpx.Client(timeout=30) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()

        items = []
        for match in payload.get("data", [])[:15]:
            items.append(
                {
                    "id": match.get("id"),
                    "title": f"{match.get('teams', ['', ''])[0]} vs {match.get('teams', ['', ''])[1]}",
                    "summary": f"Status: {match.get('status', 'Live')} — {match.get('name', 'Cricket match')}",
                    "link": None,
                }
            )

        return NewsFetchService._ingest_provider_items(
            db, source, items, id_key="id", sport=source.sport or "Cricket", news_type=NewsType.MATCH_UPDATE
        )

    @staticmethod
    def _ingest_provider_items(
        db: Session,
        source: NewsSource,
        items: list[dict],
        id_key: str = "id",
        sport: str = "Sports",
        news_type: NewsType = NewsType.FEATURE,
    ) -> int:
        created = 0
        for item in items:
            external_id = str(item.get(id_key, ""))
            if not external_id:
                continue
            exists = (
                db.query(NewsArticle)
                .filter(NewsArticle.source_id == source.id, NewsArticle.external_id == external_id)
                .first()
            )
            if exists:
                continue

            title = str(item.get("title", "Sports Update")).strip()
            summary = str(item.get("summary", item.get("description", "")) or "")
            article = NewsArticle(
                slug=NewsFetchService._unique_slug(db, title),
                title=title,
                excerpt=summary[:500] if summary else None,
                content=summary,
                sport=sport,
                news_type=news_type,
                status=NewsStatus.DRAFT,
                is_breaking=news_type == NewsType.BREAKING,
                source_url=item.get("link"),
                external_id=external_id,
                source_id=source.id,
                author="UNTOLD Wire",
            )
            db.add(article)
            created += 1
        db.flush()
        return created

    @staticmethod
    def _infer_type(title: str, summary: str) -> NewsType:
        text = f"{title} {summary}".lower()
        if any(w in text for w in ("breaking", "urgent", "just in")):
            return NewsType.BREAKING
        if any(w in text for w in ("vs", "score", "match", "final", "innings", "goal")):
            return NewsType.MATCH_UPDATE
        if "untold" in text or "exclusive" in text:
            return NewsType.EXCLUSIVE
        return NewsType.FEATURE

    @staticmethod
    def _extract_image(entry) -> str | None:
        if entry.get("media_thumbnail"):
            return entry.media_thumbnail[0].get("url")
        if entry.get("media_content"):
            return entry.media_content[0].get("url")
        links = entry.get("links", [])
        for link in links:
            if link.get("type", "").startswith("image"):
                return link.get("href")
        return None

    @staticmethod
    def _unique_slug(db: Session, title: str) -> str:
        base = slugify(title)
        slug = base
        counter = 1
        while db.query(NewsArticle).filter(NewsArticle.slug == slug).first():
            slug = f"{base}-{counter}"
            counter += 1
        return slug
