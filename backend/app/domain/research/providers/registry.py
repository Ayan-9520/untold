"""Research agent provider registry."""

from __future__ import annotations

import logging

from app.core.config import get_settings
from app.domain.research.providers.base import ResearchProvider
from app.domain.research.providers.demo import DemoResearchProvider
from app.domain.research.providers.llm_bridge import LLMResearchProvider
from app.domain.research.providers.search_stub import SearchStubProvider
from app.domain.research.types import ResearchAgentRequest, ResearchAgentResult

logger = logging.getLogger("untold.research.registry")


class ResearchProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, ResearchProvider] = {}

    def register(self, provider: ResearchProvider) -> None:
        self._providers[provider.id] = provider

    def list_providers(self) -> list[dict]:
        return [{"id": p.id, "label": p.label, "available": p.is_available()} for p in self._providers.values()]

    def resolve(self, preferred: str | None = None) -> ResearchProvider:
        settings = get_settings()
        order = []
        if preferred:
            order.append(preferred)
        order.append(getattr(settings, "research_default_provider", "demo"))
        order.extend(["llm", "search_stub", "demo"])

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
        raise RuntimeError("No research provider available")

    def research(self, request: ResearchAgentRequest, provider_id: str | None = None) -> ResearchAgentResult:
        provider = self.resolve(provider_id)
        result = provider.research(request)
        result.provider = provider.id
        return result


_registry: ResearchProviderRegistry | None = None


def get_research_registry() -> ResearchProviderRegistry:
    global _registry
    if _registry is None:
        _registry = ResearchProviderRegistry()
        _registry.register(DemoResearchProvider())
        _registry.register(LLMResearchProvider())
        _registry.register(SearchStubProvider())
    return _registry
