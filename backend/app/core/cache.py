"""Redis JSON cache helpers for hot read paths."""

from __future__ import annotations

import json
import logging
from typing import Any

from app.core.redis import get_redis

logger = logging.getLogger("untold.cache")

DEFAULT_TTL = 60


def cache_key(*parts: str) -> str:
    return "untold:cache:" + ":".join(str(p) for p in parts if p is not None)


def cache_get(key: str) -> Any | None:
    client = get_redis()
    if not client:
        return None
    try:
        raw = client.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as exc:
        logger.debug("cache_get failed %s: %s", key, exc)
        return None


def cache_set(key: str, value: Any, ttl: int = DEFAULT_TTL) -> bool:
    client = get_redis()
    if not client:
        return False
    try:
        client.setex(key, ttl, json.dumps(value, default=str))
        return True
    except Exception as exc:
        logger.debug("cache_set failed %s: %s", key, exc)
        return False


def cache_delete(*keys: str) -> None:
    client = get_redis()
    if not client or not keys:
        return
    try:
        client.delete(*keys)
    except Exception as exc:
        logger.debug("cache_delete failed: %s", exc)


def cache_delete_prefix(prefix: str) -> None:
    client = get_redis()
    if not client:
        return
    try:
        for key in client.scan_iter(match=f"{prefix}*"):
            client.delete(key)
    except Exception as exc:
        logger.debug("cache_delete_prefix failed: %s", exc)
