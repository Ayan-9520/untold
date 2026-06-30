"""SEO provider registry."""

from __future__ import annotations

from app.core.config import get_settings
from app.domain.seo.providers.base import SEOProvider
from app.domain.seo.providers.demo import DemoSEOProvider
from app.domain.seo.providers.stub_bridge import StubSEOProvider
from app.domain.seo.types import SEOGenerateRequest, SEOGenerateResult


class SEOProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, SEOProvider] = {}

    def register(self, provider: SEOProvider) -> None:
        self._providers[provider.id] = provider

    def list_providers(self) -> list[dict]:
        return [{"id": p.id, "label": p.label, "available": p.is_available()} for p in self._providers.values()]

    def resolve(self, preferred: str | None = None) -> SEOProvider:
        settings = get_settings()
        order: list[str] = []
        if preferred:
            order.append(preferred)
        order.append(getattr(settings, "seo_default_provider", "demo"))
        order.extend(["seo_stub", "demo"])
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
        raise RuntimeError("No SEO provider available")

    def generate(self, request: SEOGenerateRequest, provider_id: str | None = None) -> SEOGenerateResult:
        provider = self.resolve(provider_id)
        result = provider.generate(request)
        result.provider = provider.id
        return result


_registry: SEOProviderRegistry | None = None


def get_seo_registry() -> SEOProviderRegistry:
    global _registry
    if _registry is None:
        _registry = SEOProviderRegistry()
        _registry.register(DemoSEOProvider())
        _registry.register(StubSEOProvider())
    return _registry
