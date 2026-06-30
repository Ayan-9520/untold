"""Shorts API stub."""

from app.domain.shorts.providers.base import ShortsProvider
from app.domain.shorts.providers.demo import DemoShortsProvider
from app.domain.shorts.types import ShortsGenerateRequest, ShortsGenerateResult


class StubShortsProvider(ShortsProvider):
    id = "shorts_stub"
    label = "Cloud Shorts API (configure keys)"

    def is_available(self) -> bool:
        return False

    def generate(self, request: ShortsGenerateRequest) -> ShortsGenerateResult:
        return DemoShortsProvider().generate(request)
