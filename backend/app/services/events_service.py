"""Sports events — backed by live_matches and related videos."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import Video, VideoType
from app.models.live import LiveMatch, MatchStatus
from app.services.live_service import LiveService, THUMBNAILS


class EventsService:
    @staticmethod
    def _normalize_status(status: str) -> str:
        if status in ("live", "halftime"):
            return "live"
        if status in ("upcoming", "postponed"):
            return "upcoming"
        if status == "completed":
            return "completed"
        return status

    @staticmethod
    def serialize_match(match: LiveMatch) -> dict:
        teams = [match.team_home]
        if match.team_away:
            teams.append(match.team_away)
        sport = match.sport.value if hasattr(match.sport, "value") else str(match.sport)
        status = match.status.value if hasattr(match.status, "value") else str(match.status)
        return {
            "id": match.slug,
            "eventName": match.event_name,
            "sport": sport,
            "date": match.started_at.date().isoformat() if match.started_at else None,
            "endDate": match.ended_at.date().isoformat() if match.ended_at else None,
            "status": EventsService._normalize_status(status),
            "teamsOrPlayers": teams,
            "thumbnail": match.thumbnail_url or THUMBNAILS.get(match.sport, ""),
            "description": match.league or match.location or match.event_name,
            "location": match.location or "",
            "featured": match.is_featured,
            "liveMatchId": match.slug,
            "score": {
                "display": match.score_display or f"{match.score_home or 0} - {match.score_away or 0}",
            },
        }

    @staticmethod
    def list_events(db: Session, *, sport: str | None = None, search: str | None = None) -> list[dict]:
        query = db.query(LiveMatch).order_by(
            LiveMatch.is_featured.desc(),
            LiveMatch.started_at.desc().nullslast(),
            LiveMatch.id.desc(),
        )
        if sport and sport not in ("All", ""):
            try:
                from app.models.live import LiveSport
                query = query.filter(LiveMatch.sport == LiveSport(sport))
            except ValueError:
                query = query.filter(LiveMatch.sport == sport)
        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                LiveMatch.event_name.ilike(term)
                | LiveMatch.team_home.ilike(term)
                | LiveMatch.team_away.ilike(term)
                | LiveMatch.league.ilike(term)
            )
        return [EventsService.serialize_match(m) for m in query.limit(100).all()]

    @staticmethod
    def get_featured(db: Session) -> dict | None:
        match = (
            db.query(LiveMatch)
            .filter(LiveMatch.is_featured.is_(True))
            .order_by(LiveMatch.updated_at.desc())
            .first()
        )
        if not match:
            match = (
                db.query(LiveMatch)
                .filter(LiveMatch.status.in_([MatchStatus.LIVE, MatchStatus.HALFTIME]))
                .order_by(LiveMatch.updated_at.desc())
                .first()
            )
        return EventsService.serialize_match(match) if match else None

    @staticmethod
    def get_event(db: Session, event_id: str) -> dict | None:
        if event_id.isdigit():
            match = db.query(LiveMatch).filter(LiveMatch.id == int(event_id)).first()
        else:
            match = db.query(LiveMatch).filter(LiveMatch.slug == event_id).first()
        return EventsService.serialize_match(match) if match else None

    @staticmethod
    def list_shorts(db: Session, limit: int = 12) -> list[dict]:
        rows = (
            db.query(Video)
            .filter(Video.is_active.is_(True), Video.video_type == VideoType.SHORT)
            .order_by(Video.views_count.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": v.id,
                "title": v.title,
                "duration": v.duration,
                "views": f"{max(1, (v.views_count or 0) // 1000)}K",
                "image": v.image_url,
                "videoUrl": v.video_url,
            }
            for v in rows
        ]

    @staticmethod
    def list_stories(db: Session, limit: int = 8) -> list[dict]:
        rows = (
            db.query(Video)
            .filter(Video.is_active.is_(True))
            .order_by(Video.is_featured.desc(), Video.views_count.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": v.id,
                "title": v.title,
                "image": v.image_url,
                "category": v.category.name if v.category else None,
            }
            for v in rows
        ]

    @staticmethod
    def overview(db: Session, *, sport: str | None = None, search: str | None = None) -> dict:
        items = EventsService.list_events(db, sport=sport, search=search)
        featured = EventsService.get_featured(db)
        if featured and all(i["id"] != featured["id"] for i in items):
            items = [featured, *items]
        return {
            "items": items,
            "featured": featured,
            "shorts": EventsService.list_shorts(db),
            "stories": EventsService.list_stories(db),
            "total": len(items),
        }
