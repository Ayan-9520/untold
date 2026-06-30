"""Shorts provider registry."""

from __future__ import annotations

from app.core.config import get_settings
from app.domain.shorts.providers.base import ShortsProvider
from app.domain.shorts.providers.demo import DemoShortsProvider
from app.domain.shorts.providers.stub_bridge import StubShortsProvider
from app.domain.shorts.types import ShortsGenerateRequest, ShortsGenerateResult


class ShortsProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, ShortsProvider] = {}

    def register(self, provider: ShortsProvider) -> None:
        self._providers[provider.id] = provider

    def list_providers(self) -> list[dict]:
        return [{"id": p.id, "label": p.label, "available": p.is_available()} for p in self._providers.values()]

    def resolve(self, preferred: str | None = None) -> ShortsProvider:
        settings = get_settings()
        order: list[str] = []
        if preferred:
            order.append(preferred)
        order.append(getattr(settings, "shorts_default_provider", "demo"))
        order.extend(["shorts_stub", "demo"])
        seen: set[str] = set()
        for pid in order:
            if pid in seen:
                continue
            seen.add(pid)
            p = self._providers.get(pid)
            if p and p.is_available():
                return p
        demo = self._providers.get("demo")
        if demo:
            return demo
        raise RuntimeError("No shorts provider available")

    def generate(self, request: ShortsGenerateRequest, provider_id: str | None = None) -> ShortsGenerateResult:
        provider = self.resolve(provider_id)
        result = provider.generate(request)
        result.provider = provider.id
        return result


_registry: ShortsProviderRegistry | None = None


def get_shorts_registry() -> ShortsProviderRegistry:
    global _registry
    if _registry is None:
        _registry = ShortsProviderRegistry()
        _registry.register(DemoShortsProvider())
        _registry.register(StubShortsProvider())
    return _registry
