"""Redis cache for live scores, events, and commentary."""

import json
import logging
from typing import Any

from app.core.redis import get_redis

logger = logging.getLogger("untold")

LIVE_CHANNEL = "untold:live"
SCORES_TTL = 30
LIST_TTL = 45
EVENTS_TTL = 30
COMMENTARY_TTL = 60


class LiveCache:
    @staticmethod
    def _key_scores(match_id: int | str) -> str:
        return f"live:scores:{match_id}"

    @staticmethod
    def _key_matches(sport: str | None = None) -> str:
        return f"live:matches:{sport or 'all'}"

    @staticmethod
    def _key_events(match_id: int | str) -> str:
        return f"live:events:{match_id}"

    @staticmethod
    def _key_commentary(match_id: int | str) -> str:
        return f"live:commentary:{match_id}"

    @staticmethod
    def get_matches(sport: str | None = None) -> list[dict] | None:
        client = get_redis()
        if not client:
            return None
        raw = client.get(LiveCache._key_matches(sport))
        return json.loads(raw) if raw else None

    @staticmethod
    def set_matches(matches: list[dict], sport: str | None = None) -> None:
        client = get_redis()
        if not client:
            return
        client.setex(LiveCache._key_matches(sport), LIST_TTL, json.dumps(matches))

    @staticmethod
    def get_match(match_id: int | str) -> dict | None:
        client = get_redis()
        if not client:
            return None
        raw = client.get(LiveCache._key_scores(match_id))
        return json.loads(raw) if raw else None

    @staticmethod
    def set_match(match_id: int | str, data: dict) -> None:
        client = get_redis()
        if not client:
            return
        client.setex(LiveCache._key_scores(match_id), SCORES_TTL, json.dumps(data))

    @staticmethod
    def get_events(match_id: int | str) -> list[dict] | None:
        client = get_redis()
        if not client:
            return None
        raw = client.get(LiveCache._key_events(match_id))
        return json.loads(raw) if raw else None

    @staticmethod
    def set_events(match_id: int | str, events: list[dict]) -> None:
        client = get_redis()
        if not client:
            return
        client.setex(LiveCache._key_events(match_id), EVENTS_TTL, json.dumps(events))

    @staticmethod
    def get_commentary(match_id: int | str) -> list[dict] | None:
        client = get_redis()
        if not client:
            return None
        raw = client.get(LiveCache._key_commentary(match_id))
        return json.loads(raw) if raw else None

    @staticmethod
    def set_commentary(match_id: int | str, items: list[dict]) -> None:
        client = get_redis()
        if not client:
            return
        client.setex(LiveCache._key_commentary(match_id), COMMENTARY_TTL, json.dumps(items))

    @staticmethod
    def invalidate_match(match_id: int | str) -> None:
        client = get_redis()
        if not client:
            return
        for key in (
            LiveCache._key_scores(match_id),
            LiveCache._key_events(match_id),
            LiveCache._key_commentary(match_id),
        ):
            client.delete(key)
        client.delete(LiveCache._key_matches(None))
        for sport in ("Cricket", "Football", "Tennis", "Formula 1"):
            client.delete(LiveCache._key_matches(sport))

    @staticmethod
    def publish_update(payload: dict[str, Any]) -> None:
        """Publish real-time update to WebSocket subscribers via Redis pub/sub."""
        client = get_redis()
        if not client:
            return
        try:
            client.publish(LIVE_CHANNEL, json.dumps(payload))
        except Exception as exc:
            logger.warning("Failed to publish live update: %s", exc)
