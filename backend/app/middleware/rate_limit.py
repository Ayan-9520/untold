"""Redis-backed rate limiting via slowapi."""

import logging

from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.core.config import Settings, get_settings

logger = logging.getLogger("untold")
_settings = get_settings()


def _client_ip(request: Request) -> str:
    """Prefer X-Forwarded-For when behind Railway / reverse proxy."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return get_remote_address(request)


limiter = Limiter(
    key_func=_client_ip,
    storage_uri=_settings.redis_url,
    default_limits=[_settings.rate_limit_default],
    headers_enabled=True,
)


def check_redis_available(settings: Settings | None = None) -> bool:
    """Ping Redis — used at startup and in health checks."""
    cfg = settings or get_settings()
    try:
        import redis

        client = redis.from_url(cfg.redis_url, decode_responses=True, socket_connect_timeout=2)
        client.ping()
        return True
    except Exception as exc:
        logger.debug("Redis ping failed: %s", exc)
        return False


def setup_rate_limiting(app: FastAPI, settings: Settings | None = None) -> bool:
    """Attach Redis-backed rate limiting middleware. Returns True if enabled."""
    cfg = settings or get_settings()
    if not cfg.rate_limit_enabled:
        logger.info("Rate limiting disabled")
        return False

    if not check_redis_available(cfg):
        if cfg.is_production:
            raise RuntimeError("Redis is required for rate limiting in production")
        logger.warning("Redis unavailable — rate limiting disabled")
        return False

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    logger.info("Rate limiting enabled (%s)", cfg.rate_limit_default)
    return True
