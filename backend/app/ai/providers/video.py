"""Video generation providers — facade to video studio registry."""

from __future__ import annotations

from app.ai.providers.base import VideoProvider as BaseVideoProvider
from app.domain.video.types import VideoGenerateRequest


class VideoRegistryAdapter(BaseVideoProvider):
    id = "video_registry"
    label = "Video Studio Registry"

    def is_available(self) -> bool:
        from app.domain.video.providers.registry import get_video_registry

        return bool(get_video_registry().list_providers())

    def generate(self, request: VideoGenerateRequest, provider_id: str | None = None):
        from app.domain.video.providers.registry import get_video_registry

        return get_video_registry().generate(request, provider_id)


def list_video_providers() -> list[dict]:
    from app.domain.video.providers.registry import get_video_registry

    return get_video_registry().list_providers()


def generate_video(request: VideoGenerateRequest, provider_id: str | None = None):
    from app.domain.video.providers.registry import get_video_registry

    return get_video_registry().generate(request, provider_id)
