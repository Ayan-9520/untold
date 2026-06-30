"""Music generation providers — facade to music studio registry."""

from __future__ import annotations

from app.ai.providers.base import MusicProvider as BaseMusicProvider
from app.domain.music.types import MusicGenerateRequest


class MusicRegistryAdapter(BaseMusicProvider):
    id = "music_registry"
    label = "Music Studio Registry"

    def is_available(self) -> bool:
        from app.domain.music.providers.registry import get_music_registry

        return bool(get_music_registry().list_providers())

    def generate(self, request: MusicGenerateRequest, provider_id: str | None = None):
        from app.domain.music.providers.registry import get_music_registry

        return get_music_registry().generate(request, provider_id)

    def preview(self, request: MusicGenerateRequest, provider_id: str | None = None):
        from app.domain.music.providers.registry import get_music_registry

        return get_music_registry().preview(request, provider_id)


def list_music_providers() -> list[dict]:
    from app.domain.music.providers.registry import get_music_registry

    return get_music_registry().list_providers()


def generate_music(request: MusicGenerateRequest, provider_id: str | None = None):
    from app.domain.music.providers.registry import get_music_registry

    return get_music_registry().generate(request, provider_id)
