"""Voice / TTS providers — facade to voice studio registry."""

from __future__ import annotations

from app.ai.providers.base import VoiceProvider as BaseVoiceProvider
from app.domain.voice.types import VoiceGenerateRequest


class VoiceRegistryAdapter(BaseVoiceProvider):
    id = "voice_registry"
    label = "Voice Studio Registry"

    def is_available(self) -> bool:
        from app.domain.voice.providers.registry import get_voice_registry

        return bool(get_voice_registry().list_providers())

    def generate(self, request: VoiceGenerateRequest, provider_id: str | None = None):
        from app.domain.voice.providers.registry import get_voice_registry

        return get_voice_registry().generate(request, provider_id)

    def preview(self, request: VoiceGenerateRequest, provider_id: str | None = None):
        from app.domain.voice.providers.registry import get_voice_registry

        return get_voice_registry().preview(request, provider_id)


def list_voice_providers() -> list[dict]:
    from app.domain.voice.providers.registry import get_voice_registry

    return get_voice_registry().list_providers()


def generate_voice(request: VoiceGenerateRequest, provider_id: str | None = None):
    from app.domain.voice.providers.registry import get_voice_registry

    return get_voice_registry().generate(request, provider_id)
