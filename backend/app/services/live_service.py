"""UNTOLD Live — production sports engine with DB, Redis, and AI."""

import json
import logging

from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import NotFoundError
from app.models.live import LiveCommentary, LiveEvent, LiveMatch, LiveSport, MatchStat, MatchStatus
from app.services.live_ai_service import LiveAIService
from app.services.live_cache import LiveCache

logger = logging.getLogger("untold")

THUMBNAILS = {
    LiveSport.CRICKET: "https://images.unsplash.com/photo-1531415074968-076ba3e9f2e4?w=1200&q=80",
    LiveSport.FOOTBALL: "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=1200&q=80",
    LiveSport.TENNIS: "https://images.unsplash.com/photo-1554068865-24cecd4e24b8?w=1200&q=80",
    LiveSport.FORMULA_1: "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=1200&q=80",
}


class LiveService:
    @staticmethod
    def serialize_match(match: LiveMatch) -> dict:
        teams = [match.team_home]
        if match.team_away:
            teams.append(match.team_away)

        return {
            "id": match.slug,
            "db_id": match.id,
            "event_name": match.event_name,
            "eventName": match.event_name,
            "sport": match.sport.value if hasattr(match.sport, "value") else match.sport,
            "teams_or_players": teams,
            "teamsOrPlayers": teams,
            "score": {
                "home": match.score_home,
                "away": match.score_away,
                "display": match.score_display or f"{match.score_home or 0} - {match.score_away or 0}",
            },
            "status": match.status.value if hasattr(match.status, "value") else match.status,
            "timer": match.timer,
            "thumbnail": match.thumbnail_url or THUMBNAILS.get(match.sport, ""),
            "location": match.location,
            "league": match.league,
            "featured": match.is_featured,
            "provider": match.provider.value if match.provider else None,
        }

    @staticmethod
    def _active_query(db: Session):
        return db.query(LiveMatch).filter(
            LiveMatch.status.in_([MatchStatus.LIVE, MatchStatus.HALFTIME])
        )

    @staticmethod
    def get_overview(db: Session) -> dict:
        cached = LiveCache.get_matches()
        if cached:
            featured = next((m for m in cached if m.get("featured")), cached[0] if cached else None)
            return {"featured": featured, "matches": cached, "total": len(cached)}

        matches = (
            LiveService._active_query(db)
            .order_by(LiveMatch.is_featured.desc(), LiveMatch.updated_at.desc())
            .all()
        )
        serialized = [LiveService.serialize_match(m) for m in matches]
        LiveCache.set_matches(serialized)
        featured = next((m for m in matches if m.is_featured), matches[0] if matches else None)
        return {
            "featured": LiveService.serialize_match(featured) if featured else None,
            "matches": serialized,
            "total": len(serialized),
        }

    @staticmethod
    def get_featured(db: Session) -> dict | None:
        overview = LiveService.get_overview(db)
        return overview.get("featured")

    @staticmethod
    def list_matches(db: Session, sport: str | None = None) -> list[dict]:
        if sport and sport != "All":
            cached = LiveCache.get_matches(sport)
            if cached:
                return cached

        query = LiveService._active_query(db)
        if sport and sport != "All":
            try:
                query = query.filter(LiveMatch.sport == LiveSport(sport))
            except ValueError:
                query = query.filter(LiveMatch.sport == sport)

        matches = query.order_by(LiveMatch.is_featured.desc(), LiveMatch.updated_at.desc()).all()
        serialized = [LiveService.serialize_match(m) for m in matches]

        if sport and sport != "All":
            LiveCache.set_matches(serialized, sport)
        else:
            LiveCache.set_matches(serialized)

        return serialized

    @staticmethod
    def _resolve_match(db: Session, match_id: str) -> LiveMatch:
        cached = LiveCache.get_match(match_id)
        if cached and cached.get("db_id"):
            match = db.query(LiveMatch).filter(LiveMatch.id == cached["db_id"]).first()
            if match:
                return match

        if match_id.isdigit():
            match = db.query(LiveMatch).filter(LiveMatch.id == int(match_id)).first()
        else:
            match = db.query(LiveMatch).filter(LiveMatch.slug == match_id).first()

        if not match:
            raise NotFoundError("Match")
        return match

    @staticmethod
    def get_match(db: Session, match_id: str) -> dict:
        cached = LiveCache.get_match(match_id)
        if cached:
            return cached

        match = LiveService._resolve_match(db, match_id)
        data = LiveService.serialize_match(match)
        LiveCache.set_match(match.id, data)
        LiveCache.set_match(match.slug, data)
        return data

    @staticmethod
    def get_events(db: Session, match_id: str) -> list[dict]:
        cached = LiveCache.get_events(match_id)
        if cached is not None:
            return cached

        match = LiveService._resolve_match(db, match_id)
        events = (
            db.query(LiveEvent)
            .filter(LiveEvent.match_id == match.id)
            .order_by(LiveEvent.occurred_at.desc().nullslast(), LiveEvent.id.desc())
            .limit(50)
            .all()
        )
        serialized = [
            {
                "id": e.id,
                "type": e.event_type.value,
                "raw": e.raw_text,
                "minute": e.minute_or_over,
                "time": e.minute_or_over,
                "occurred_at": e.occurred_at.isoformat() if e.occurred_at else None,
            }
            for e in events
        ]
        LiveCache.set_events(match_id, serialized)
        return serialized

    @staticmethod
    def get_commentary(db: Session, match_id: str) -> list[dict]:
        cached = LiveCache.get_commentary(match_id)
        if cached is not None:
            return cached

        match = LiveService._resolve_match(db, match_id)
        items = (
            db.query(LiveCommentary)
            .filter(LiveCommentary.match_id == match.id)
            .order_by(LiveCommentary.created_at.desc())
            .limit(50)
            .all()
        )
        serialized = [
            {
                "id": c.id,
                "text": c.ai_text,
                "ai_text": c.ai_text,
                "minute": c.minute_or_over,
                "time": c.minute_or_over,
                "type": "commentary",
                "is_breaking": c.is_breaking,
            }
            for c in items
        ]
        LiveCache.set_commentary(match_id, serialized)
        return serialized

    @staticmethod
    def get_stats(db: Session, match_id: str) -> dict:
        match = LiveService._resolve_match(db, match_id)
        stat = db.query(MatchStat).filter(MatchStat.match_id == match.id).first()
        if not stat:
            return {"match_id": match.id, "stats": {}}
        try:
            return {"match_id": match.id, "stats": json.loads(stat.stats_json)}
        except json.JSONDecodeError:
            return {"match_id": match.id, "stats": {}}

    @staticmethod
    def generate_commentary_preview(event: dict, sport: str = "Football") -> str:
        from app.models.live import LiveEventType

        try:
            event_type = LiveEventType(event.get("type", "default"))
        except ValueError:
            event_type = LiveEventType.DEFAULT
        raw = event.get("raw") or event.get("text", "")
        return LiveAIService.generate_commentary(event_type, raw, sport)
