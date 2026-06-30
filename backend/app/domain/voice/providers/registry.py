"""Voice generation provider registry."""

from __future__ import annotations

from app.domain.voice.providers.base import VoiceProvider
from app.domain.voice.types import VoiceGenerateRequest, VoiceGenerateResult


class VoiceProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, VoiceProvider] = {}

    def register(self, provider: VoiceProvider) -> None:
        self._providers[provider.id] = provider

    def list_providers(self) -> list[dict]:
        return [{"id": p.id, "label": p.label, "available": p.is_available()} for p in self._providers.values()]

    def resolve(self, preferred: str | None = None) -> VoiceProvider:
        from app.ai.adapters.legacy_registry import resolve_capability

        return resolve_capability("voice", preferred)

    def generate(self, request: VoiceGenerateRequest, provider_id: str | None = None) -> VoiceGenerateResult:
        from app.ai.runtime.invoke import invoke_provider_method

        return invoke_provider_method(
            "voice",
            "generate",
            request,
            provider_id,
            prompt_for_cost=request.text,
        )

    def preview(self, request: VoiceGenerateRequest, provider_id: str | None = None) -> VoiceGenerateResult:
        from app.ai.runtime.invoke import invoke_provider_method

        return invoke_provider_method(
            "voice",
            "preview",
            request,
            provider_id,
            prompt_for_cost=request.text,
        )


_registry: VoiceProviderRegistry | None = None


def get_voice_registry() -> VoiceProviderRegistry:
    global _registry
    if _registry is None:
        from app.ai.adapters.legacy_registry import sync_legacy_registry

        _registry = VoiceProviderRegistry()
        sync_legacy_registry(_registry, "voice")
    return _registry
