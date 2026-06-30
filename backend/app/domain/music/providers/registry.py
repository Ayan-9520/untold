"""Music generation provider registry."""

from __future__ import annotations

from app.domain.music.providers.base import MusicProvider
from app.domain.music.types import MusicGenerateRequest, MusicGenerateResult


class MusicProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, MusicProvider] = {}

    def register(self, provider: MusicProvider) -> None:
        self._providers[provider.id] = provider

    def list_providers(self) -> list[dict]:
        return [{"id": p.id, "label": p.label, "available": p.is_available()} for p in self._providers.values()]

    def resolve(self, preferred: str | None = None) -> MusicProvider:
        from app.ai.adapters.legacy_registry import resolve_capability

        return resolve_capability("music", preferred)

    def generate(self, request: MusicGenerateRequest, provider_id: str | None = None) -> MusicGenerateResult:
        from app.ai.runtime.invoke import invoke_provider_method

        return invoke_provider_method(
            "music",
            "generate",
            request,
            provider_id,
            prompt_for_cost=request.prompt,
        )

    def preview(self, request: MusicGenerateRequest, provider_id: str | None = None) -> MusicGenerateResult:
        from app.ai.runtime.invoke import invoke_provider_method

        return invoke_provider_method(
            "music",
            "preview",
            request,
            provider_id,
            prompt_for_cost=request.prompt,
        )


_registry: MusicProviderRegistry | None = None


def get_music_registry() -> MusicProviderRegistry:
    global _registry
    if _registry is None:
        from app.ai.adapters.legacy_registry import sync_legacy_registry

        _registry = MusicProviderRegistry()
        sync_legacy_registry(_registry, "music")
    return _registry
