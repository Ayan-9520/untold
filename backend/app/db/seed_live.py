"""Seed live matches, events, commentary, fixtures."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.live import (
    Fixture,
    LiveCommentary,
    LiveEvent,
    LiveEventType,
    LiveMatch,
    LiveNotification,
    LiveProvider,
    LiveSport,
    MatchStat,
    MatchStatus,
)
from app.services.live_ai_service import LiveAIService

THUMBNAILS = {
    LiveSport.CRICKET: "https://images.unsplash.com/photo-1531415074968-076ba3e9f2e4?w=1200&q=80",
    LiveSport.FOOTBALL: "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=1200&q=80",
    LiveSport.TENNIS: "https://images.unsplash.com/photo-1554068865-24cecd4e24b8?w=1200&q=80",
    LiveSport.FORMULA_1: "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=1200&q=80",
}

SEED_MATCHES = [
    {
        "slug": "live-ind-aus",
        "event_name": "India vs Australia — 3rd ODI",
        "sport": LiveSport.CRICKET,
        "team_home": "India",
        "team_away": "Australia",
        "score_home": "287/4",
        "score_away": "245",
        "score_display": "287/4 vs 245",
        "timer": "42.3 overs",
        "featured": True,
        "location": "Wankhede, Mumbai",
        "league": "India Tour of Australia",
        "events": [
            ("42.3", LiveEventType.WICKET, "Kohli departs for 89 — caught at long-on"),
            ("38.1", LiveEventType.DEFAULT, "Kohli and Hardik rebuild after early scare"),
            ("32.0", LiveEventType.BOUNDARY, "Rohit crashes a boundary through covers"),
        ],
    },
    {
        "slug": "live-el-clasico",
        "event_name": "Real Madrid vs Barcelona",
        "sport": LiveSport.FOOTBALL,
        "team_home": "Real Madrid",
        "team_away": "Barcelona",
        "score_home": "2",
        "score_away": "1",
        "score_display": "2 - 1",
        "timer": "78'",
        "location": "Santiago Bernabéu",
        "league": "La Liga",
        "events": [
            ("78'", LiveEventType.GOAL, "Bellingham scores in the 78th minute"),
            ("65'", LiveEventType.CARD, "Yellow card for Barcelona midfielder"),
        ],
    },
    {
        "slug": "live-wimbledon",
        "event_name": "Alcaraz vs Sinner — Wimbledon SF",
        "sport": LiveSport.TENNIS,
        "team_home": "Alcaraz",
        "team_away": "Sinner",
        "score_home": "2",
        "score_away": "1",
        "score_display": "6-4, 3-6, 4-3",
        "timer": "Set 3",
        "league": "Wimbledon",
        "events": [
            ("Set 3", LiveEventType.POINT, "Break point saved — Alcaraz holds serve"),
        ],
    },
    {
        "slug": "live-monaco-gp",
        "event_name": "Monaco Grand Prix",
        "sport": LiveSport.FORMULA_1,
        "team_home": "Verstappen",
        "team_away": "Leclerc",
        "score_home": "P1",
        "score_away": "P2",
        "score_display": "Lap 58/78",
        "timer": "Lap 58",
        "league": "Formula 1",
        "events": [
            ("Lap 58", LiveEventType.LAP, "Verstappen sets fastest lap of the race"),
        ],
    },
]


def seed_live_data(db: Session) -> None:
    if db.query(LiveMatch).first():
        return

    now = datetime.now(timezone.utc)

    for data in SEED_MATCHES:
        match = LiveMatch(
            slug=data["slug"],
            external_id=data["slug"],
            provider=LiveProvider.MANUAL,
            event_name=data["event_name"],
            sport=data["sport"],
            team_home=data["team_home"],
            team_away=data["team_away"],
            score_home=data["score_home"],
            score_away=data["score_away"],
            score_display=data["score_display"],
            status=MatchStatus.LIVE,
            timer=data["timer"],
            thumbnail_url=THUMBNAILS[data["sport"]],
            location=data.get("location"),
            league=data.get("league"),
            is_featured=data.get("featured", False),
            started_at=now - timedelta(hours=2),
            last_synced_at=now,
        )
        db.add(match)
        db.flush()

        db.add(
            MatchStat(
                match_id=match.id,
                stats_json='{"possession": "52-48", "shots": "14-11"}' if data["sport"] == LiveSport.FOOTBALL else '{"run_rate": "6.2"}',
            )
        )

        for minute, event_type, raw in data.get("events", []):
            event = LiveEvent(
                match_id=match.id,
                event_type=event_type,
                minute_or_over=minute,
                raw_text=raw,
                occurred_at=now,
            )
            db.add(event)
            db.flush()

            ai_text = LiveAIService.generate_commentary(event_type, raw, match.sport.value)
            title, body = LiveAIService.generate_notification(event_type, raw, match.event_name)
            db.add(
                LiveCommentary(
                    match_id=match.id,
                    event_id=event.id,
                    minute_or_over=minute,
                    ai_text=ai_text,
                    notification_text=title,
                    is_breaking=event_type in (LiveEventType.GOAL, LiveEventType.WICKET, LiveEventType.SIX),
                )
            )
            db.add(
                LiveNotification(
                    match_id=match.id,
                    event_id=event.id,
                    title=title,
                    body=body,
                    channel="in_app",
                )
            )

        db.add(
            Fixture(
                external_id=f"fix-{data['slug']}",
                provider=LiveProvider.MANUAL,
                sport=data["sport"],
                event_name=data["event_name"],
                team_home=data["team_home"],
                team_away=data["team_away"],
                scheduled_at=now - timedelta(hours=3),
                venue=data.get("location"),
                status=MatchStatus.LIVE,
                match_id=match.id,
            )
        )

    db.commit()
