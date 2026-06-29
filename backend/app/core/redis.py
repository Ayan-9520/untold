"""Redis client — cache layer for live scores, sessions, and rate limiting."""

import logging

from app.core.config import get_settings

logger = logging.getLogger("untold")
_settings = get_settings()
_client = None


def get_redis():
    """Lazy Redis connection. Returns None if redis package or server unavailable."""
    global _client
    if _client is not None:
        return _client
    try:
        import redis

        _client = redis.from_url(
            _settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
        )
        _client.ping()
        logger.info("Redis connected")
        return _client
    except Exception as exc:
        logger.warning("Redis unavailable: %s", exc)
        return None


def ping_redis() -> bool:
    """Check Redis connectivity without caching a failed client."""
    try:
        import redis

        client = redis.from_url(
            _settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
        )
        client.ping()
        return True
    except Exception:
        return False
