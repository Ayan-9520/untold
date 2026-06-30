"""Redis mocks for unit tests."""

from __future__ import annotations

from unittest.mock import patch


class FakeRedis:
    """Minimal in-memory Redis stand-in."""

    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    def ping(self) -> bool:
        return True

    def get(self, key: str) -> str | None:
        return self._store.get(key)

    def set(self, key: str, value: str, ex: int | None = None) -> bool:
        self._store[key] = value
        return True

    def delete(self, key: str) -> int:
        return 1 if self._store.pop(key, None) is not None else 0


def patch_redis_ping(return_value: bool = True):
    return patch("app.core.redis.ping_redis", return_value=return_value)
