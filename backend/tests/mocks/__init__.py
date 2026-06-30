"""Shared test mocks."""

from tests.mocks.redis import FakeRedis, patch_redis_ping

__all__ = ["FakeRedis", "patch_redis_ping"]
