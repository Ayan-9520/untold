"""Sync live data from providers into PostgreSQL + Redis."""

import json
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.live import (
    Fixture,
    LiveEvent,
    LiveMatch,
    LiveProvider,
    LiveSport,
    MatchStat,
    MatchStatus,
)
from app.services.live_ai_service import LiveAIService
from app.services.live_cache import LiveCache
from app.services.live_provider_service import LiveProviderService
from app.utils.text import slugify

logger = logging.getLogger("untold")


class LiveSyncService:
    @staticmethod
    def sync_all(db: Session) -> dict:
        provider_matches = LiveProviderService.fetch_all_live()
        synced = 0
        events_created = 0

        for data in provider_matches:
            match = LiveSyncService._upsert_match(db, data)
            if match:
                synced += 1
                events_created += LiveSyncService._sync_match_stats(db, match, data)

        db.commit()
        LiveSyncService._refresh_caches(db)

        return {"matches_synced": synced, "events_created": events_created}

    @staticmethod
    def _upsert_match(db: Session, data: dict) -> LiveMatch | None:
        external_id = str(data.get("external_id", ""))
        provider = data["provider"]
        if not external_id:
            return None

        match = (
            db.query(LiveMatch)
            .filter(LiveMatch.provider == provider, LiveMatch.external_id == external_id)
            .first()
        )

        if not match:
            slug_base = slugify(f"{data['team_home']}-{data.get('team_away', 'tbd')}")
            slug = slug_base
            counter = 1
            while db.query(LiveMatch).filter(LiveMatch.slug == slug).first():
                slug = f"{slug_base}-{counter}"
                counter += 1

            match = LiveMatch(
                external_id=external_id,
                provider=provider,
                slug=slug,
                event_name=data["event_name"],
                sport=data["sport"],
                team_home=data["team_home"],
                team_away=data.get("team_away"),
                status=data.get("status", MatchStatus.LIVE),
                thumbnail_url=data.get("thumbnail_url"),
                league=data.get("league"),
            )
            db.add(match)

        match.score_home = data.get("score_home")
        match.score_away = data.get("score_away")
        match.score_display = data.get("score_display")
        match.timer = data.get("timer")
        match.status = data.get("status", match.status)
        match.last_synced_at = datetime.now(timezone.utc)

        for event_data in data.get("events", []):
            LiveSyncService._create_event_if_new(db, match, event_data)

        db.flush()
        return match

    @staticmethod
    def _create_event_if_new(db: Session, match: LiveMatch, event_data: dict) -> LiveEvent | None:
        external_id = str(event_data.get("external_id", ""))
        if external_id:
            exists = (
                db.query(LiveEvent)
                .filter(LiveEvent.match_id == match.id, LiveEvent.external_id == external_id)
                .first()
            )
            if exists:
                return None

        event = LiveEvent(
            match_id=match.id,
            event_type=event_data["event_type"],
            minute_or_over=event_data.get("minute_or_over"),
            raw_text=event_data["raw_text"],
            payload_json=json.dumps(event_data.get("payload", {})),
            external_id=external_id or None,
            occurred_at=event_data.get("occurred_at"),
        )
        db.add(event)
        db.flush()
        LiveAIService.process_event(db, match, event)
        return event

    @staticmethod
    def _sync_match_stats(db: Session, match: LiveMatch, data: dict) -> int:
        stats_data = data.get("stats", {})
        if not stats_data:
            return 0

        stat = db.query(MatchStat).filter(MatchStat.match_id == match.id).first()
        if not stat:
            stat = MatchStat(match_id=match.id, stats_json="{}")
            db.add(stat)
        stat.stats_json = json.dumps(stats_data)
        return 0

    @staticmethod
    def ingest_webhook(db: Session, provider: str, payload: dict) -> dict:
        parsed = LiveProviderService.parse_webhook(provider, payload)
        if not parsed:
            return {"status": "ignored"}

        provider_enum = LiveProvider(provider)
        match = None
        if parsed.get("match_external_id"):
            match = (
                db.query(LiveMatch)
                .filter(
                    LiveMatch.provider == provider_enum,
                    LiveMatch.external_id == str(parsed["match_external_id"]),
                )
                .first()
            )

        if not match:
            match = db.query(LiveMatch).filter(LiveMatch.status == MatchStatus.LIVE).first()

        if not match:
            return {"status": "no_match"}

        event = LiveEvent(
            match_id=match.id,
            event_type=parsed["event_type"],
            minute_or_over=parsed.get("minute_or_over"),
            raw_text=parsed["raw_text"],
            external_id=str(parsed.get("external_id", "")),
            occurred_at=parsed.get("occurred_at"),
        )
        db.add(event)
        db.flush()

        result = LiveAIService.process_event(db, match, event)
        db.commit()
        return {"status": "processed", **result}

    @staticmethod
    def _refresh_caches(db: Session) -> None:
        from app.services.live_service import LiveService

        matches = (
            db.query(LiveMatch)
            .filter(LiveMatch.status.in_([MatchStatus.LIVE, MatchStatus.HALFTIME]))
            .order_by(LiveMatch.is_featured.desc(), LiveMatch.updated_at.desc())
            .all()
        )
        serialized = [LiveService.serialize_match(m) for m in matches]
        LiveCache.set_matches(serialized)
        for sport in LiveSport:
            sport_matches = [s for s in serialized if s["sport"] == sport.value]
            LiveCache.set_matches(sport_matches, sport.value)

        for m in matches:
            data = LiveService.serialize_match(m)
            LiveCache.set_match(m.id, data)
            LiveCache.set_match(m.slug, data)

        if matches:
            featured = next((m for m in matches if m.is_featured), matches[0])
            LiveCache.publish_update(
                {
                    "type": "scores_refresh",
                    "matches": serialized[:10],
                    "featured_id": featured.slug,
                }
            )
