"""Storyboard AI provider registry."""

from __future__ import annotations

from app.core.config import get_settings
from app.domain.storyboard.providers.base import StoryboardProvider
from app.domain.storyboard.providers.demo import DemoStoryboardProvider
from app.domain.storyboard.providers.llm_bridge import LLMStoryboardProvider
from app.domain.storyboard.types import StoryboardAgentRequest, StoryboardAgentResult


class StoryboardProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, StoryboardProvider] = {}

    def register(self, provider: StoryboardProvider) -> None:
        self._providers[provider.id] = provider

    def list_providers(self) -> list[dict]:
        return [{"id": p.id, "label": p.label, "available": p.is_available()} for p in self._providers.values()]

    def resolve(self, preferred: str | None = None) -> StoryboardProvider:
        settings = get_settings()
        order: list[str] = []
        if preferred:
            order.append(preferred)
        order.append(getattr(settings, "storyboard_default_provider", "demo"))
        order.extend(["llm", "demo"])

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
        raise RuntimeError("No storyboard provider available")

    def generate(self, request: StoryboardAgentRequest, provider_id: str | None = None) -> StoryboardAgentResult:
        provider = self.resolve(provider_id)
        result = provider.generate(request)
        result.provider = provider.id
        return result


_registry: StoryboardProviderRegistry | None = None


def get_storyboard_registry() -> StoryboardProviderRegistry:
    global _registry
    if _registry is None:
        _registry = StoryboardProviderRegistry()
        _registry.register(DemoStoryboardProvider())
        _registry.register(LLMStoryboardProvider())
    return _registry
