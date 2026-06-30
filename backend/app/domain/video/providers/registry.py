"""Video generation provider registry."""

from __future__ import annotations

from app.domain.video.providers.base import VideoProvider
from app.domain.video.types import VideoGenerateRequest, VideoGenerateResult


class VideoProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, VideoProvider] = {}

    def register(self, provider: VideoProvider) -> None:
        self._providers[provider.id] = provider

    def list_providers(self) -> list[dict]:
        return [{"id": p.id, "label": p.label, "available": p.is_available()} for p in self._providers.values()]

    def resolve(self, preferred: str | None = None) -> VideoProvider:
        from app.ai.adapters.legacy_registry import resolve_capability

        return resolve_capability("video", preferred)

    def generate(self, request: VideoGenerateRequest, provider_id: str | None = None) -> VideoGenerateResult:
        from app.ai.runtime.invoke import invoke_provider_method

        return invoke_provider_method(
            "video",
            "generate",
            request,
            provider_id,
            prompt_for_cost=request.prompt,
        )


_registry: VideoProviderRegistry | None = None


def get_video_registry() -> VideoProviderRegistry:
    global _registry
    if _registry is None:
        from app.ai.adapters.legacy_registry import sync_legacy_registry

        _registry = VideoProviderRegistry()
        sync_legacy_registry(_registry, "video")
    return _registry
