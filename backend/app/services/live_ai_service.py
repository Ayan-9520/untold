"""AI Live Agent — commentary, notifications, event summaries."""

import json
import logging

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.live import LiveEvent, LiveEventType, LiveMatch, LiveNotification
from app.services.live_cache import LiveCache

logger = logging.getLogger("untold")
settings = get_settings()

AI_TEMPLATES = {
    LiveEventType.GOAL: "GOAL! {text} — the stadium erupts!",
    LiveEventType.WICKET: "WICKET! {text} — a huge moment in this contest.",
    LiveEventType.BOUNDARY: "FOUR! {text} — racing to the rope!",
    LiveEventType.SIX: "SIX! {text} — into the crowd!",
    LiveEventType.POINT: "MATCH POINT! {text}",
    LiveEventType.LAP: "FASTEST LAP! {text}",
    LiveEventType.INCIDENT: "INCIDENT: {text}",
    LiveEventType.CARD: "CARD SHOWN! {text}",
    LiveEventType.SUBSTITUTION: "SUBSTITUTION: {text}",
    LiveEventType.DEFAULT: "{text}",
}

NOTIFICATION_TEMPLATES = {
    LiveEventType.GOAL: "⚽ GOAL — {short}",
    LiveEventType.WICKET: "🏏 WICKET — {short}",
    LiveEventType.BOUNDARY: "🏏 FOUR — {short}",
    LiveEventType.SIX: "🏏 SIX — {short}",
    LiveEventType.DEFAULT: "🔴 LIVE — {short}",
}


class LiveAIService:
    @staticmethod
    def generate_commentary(event_type: LiveEventType, raw_text: str, sport: str) -> str:
        if settings.openai_api_key:
            try:
                return LiveAIService._openai_commentary(event_type, raw_text, sport)
            except Exception as exc:
                logger.warning("OpenAI live commentary failed: %s", exc)

        template = AI_TEMPLATES.get(event_type, AI_TEMPLATES[LiveEventType.DEFAULT])
        return template.format(text=raw_text)

    @staticmethod
    def _openai_commentary(event_type: LiveEventType, raw_text: str, sport: str) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are UNTOLD Live AI commentator. Write one exciting sentence of live commentary. "
                        "No hashtags. Max 120 characters."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Sport: {sport}\nEvent: {event_type.value}\nRaw: {raw_text}",
                },
            ],
            max_tokens=80,
            temperature=0.8,
        )
        return (response.choices[0].message.content or raw_text).strip()

    @staticmethod
    def generate_notification(event_type: LiveEventType, raw_text: str, match_name: str) -> tuple[str, str]:
        short = raw_text[:80]
        title_tpl = NOTIFICATION_TEMPLATES.get(event_type, NOTIFICATION_TEMPLATES[LiveEventType.DEFAULT])
        title = title_tpl.format(short=short)
        body = f"{match_name}: {raw_text}"
        return title, body

    @staticmethod
    def generate_event_summary(events: list[LiveEvent], sport: str) -> str:
        if not events:
            return "No events yet in this match."
        lines = [f"- {e.event_type.value}: {e.raw_text}" for e in events[-5:]]
        summary = "\n".join(lines)

        if settings.openai_api_key:
            try:
                from openai import OpenAI

                client = OpenAI(api_key=settings.openai_api_key)
                response = client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[
                        {"role": "system", "content": "Summarize match events in 2 sentences for UNTOLD fans."},
                        {"role": "user", "content": f"Sport: {sport}\nEvents:\n{summary}"},
                    ],
                    max_tokens=120,
                )
                return (response.choices[0].message.content or summary).strip()
            except Exception:
                pass

        return f"Latest in {sport}: " + "; ".join(e.raw_text[:60] for e in events[-3:])

    @staticmethod
    def process_event(
        db: Session,
        match: LiveMatch,
        event: LiveEvent,
        broadcast: bool = True,
    ) -> dict:
        from app.models.live import LiveCommentary

        ai_text = LiveAIService.generate_commentary(event.event_type, event.raw_text, match.sport.value)
        notif_title, notif_body = LiveAIService.generate_notification(
            event.event_type, event.raw_text, match.event_name
        )

        commentary = LiveCommentary(
            match_id=match.id,
            event_id=event.id,
            minute_or_over=event.minute_or_over,
            ai_text=ai_text,
            notification_text=notif_title,
            is_breaking=event.event_type in (
                LiveEventType.GOAL,
                LiveEventType.WICKET,
                LiveEventType.SIX,
            ),
        )
        db.add(commentary)

        notification = LiveNotification(
            match_id=match.id,
            event_id=event.id,
            title=notif_title,
            body=notif_body,
            channel="in_app",
        )
        db.add(notification)
        db.commit()
        db.refresh(commentary)

        payload = {
            "type": "live_event",
            "match_id": match.slug,
            "db_id": match.id,
            "event": {
                "id": event.id,
                "type": event.event_type.value,
                "raw": event.raw_text,
                "minute": event.minute_or_over,
            },
            "commentary": {
                "id": commentary.id,
                "text": ai_text,
                "is_breaking": commentary.is_breaking,
            },
            "notification": {"title": notif_title, "body": notif_body},
            "score": {
                "display": match.score_display,
                "home": match.score_home,
                "away": match.score_away,
            },
        }

        if broadcast:
            LiveCache.invalidate_match(match.id)
            LiveCache.invalidate_match(match.slug)
            LiveCache.publish_update(payload)

        return payload
