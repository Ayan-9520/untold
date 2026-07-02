"""Per-API-key rate limiting via Redis."""

from __future__ import annotations

import logging

from fastapi import HTTPException, status

from app.core.config import get_settings
from app.domain.gateway.scopes import RATE_LIMIT_TIERS
from app.models.studio_platform import StudioApiKey

logger = logging.getLogger("untold.gateway.ratelimit")


def check_rate_limit(
    *,
    api_key: StudioApiKey | None,
    auth_type: str,
    identifier: str,
    environment: str = "production",
) -> None:
    """Raise 429 if rate limit exceeded. JWT uses IP-based default tier."""
    settings = get_settings()
    if not settings.rate_limit_enabled:
        return

    tier_name = api_key.rate_limit_tier if api_key else "standard"
    if environment == "sandbox":
        tier_name = "standard"
    tier = RATE_LIMIT_TIERS.get(tier_name, RATE_LIMIT_TIERS["standard"])
    limit = tier["limit"]
    key = f"gateway:rl:{api_key.id if api_key else identifier}:{tier_name}"

    try:
        import redis
        from limits import parse
        from limits.storage import RedisStorage
        from limits.strategies import MovingWindowRateLimiter

        storage = RedisStorage(settings.redis_url)
        limiter = MovingWindowRateLimiter(storage)
        rate = parse(limit)
        if not limiter.hit(rate, key):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded ({tier_name}: {limit})",
                headers={"Retry-After": "60", "X-RateLimit-Tier": tier_name},
            )
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("Rate limit check failed: %s", exc)
        if settings.is_production:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Rate limiting unavailable",
            ) from exc
        return
