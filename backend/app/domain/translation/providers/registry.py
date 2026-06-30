"""Translation provider registry."""

from __future__ import annotations

from app.domain.translation.providers.base import TranslationProvider
from app.domain.translation.types import TranslationRequest, TranslationResult


class TranslationProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, TranslationProvider] = {}

    def register(self, provider: TranslationProvider) -> None:
        self._providers[provider.id] = provider

    def list_providers(self) -> list[dict]:
        return [{"id": p.id, "label": p.label, "available": p.is_available()} for p in self._providers.values()]

    def resolve(self, preferred: str | None = None) -> TranslationProvider:
        from app.ai.adapters.legacy_registry import resolve_capability

        return resolve_capability("translation", preferred)

    def translate(self, request: TranslationRequest, provider_id: str | None = None) -> TranslationResult:
        from app.ai.runtime.invoke import invoke_provider_method

        return invoke_provider_method(
            "translation",
            "translate",
            request,
            provider_id,
            prompt_for_cost=request.text,
        )


_registry: TranslationProviderRegistry | None = None


def get_translation_registry() -> TranslationProviderRegistry:
    global _registry
    if _registry is None:
        from app.ai.adapters.legacy_registry import sync_legacy_registry

        _registry = TranslationProviderRegistry()
        sync_legacy_registry(_registry, "translation")
    return _registry
