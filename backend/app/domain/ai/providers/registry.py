"""Provider registry — register and resolve AI backends without hardcoding vendors."""

from __future__ import annotations

import logging

from app.domain.ai.providers.base import AIProvider
from app.domain.ai.types import AIJobRequest, AIJobResult

logger = logging.getLogger("untold.ai.registry")


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, AIProvider] = {}

    def register(self, provider: AIProvider) -> None:
        self._providers[provider.id] = provider
        logger.debug("Registered AI provider: %s", provider.id)

    def get(self, provider_id: str) -> AIProvider | None:
        return self._providers.get(provider_id)

    def list_providers(self) -> list[dict]:
        return [
            {
                "id": p.id,
                "label": p.label,
                "available": p.is_available(),
                "modules": sorted(p.supports_modules) if p.supports_modules else ["*"],
            }
            for p in self._providers.values()
        ]

    def resolve(self, module: str, preferred: str | None = None) -> AIProvider:
        from app.ai.adapters.legacy_registry import resolve_capability

        return resolve_capability("llm", preferred, module=module)

    def generate(self, request: AIJobRequest, provider_id: str | None = None) -> AIJobResult:
        from app.ai.runtime.invoke import invoke_llm

        return invoke_llm(request, provider_id)


_registry: ProviderRegistry | None = None


def get_provider_registry() -> ProviderRegistry:
    global _registry
    if _registry is None:
        from app.ai.adapters.legacy_registry import sync_legacy_registry

        _registry = ProviderRegistry()
        sync_legacy_registry(_registry, "llm")
    return _registry
