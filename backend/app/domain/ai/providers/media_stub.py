"""Media stub provider — placeholder for image/video backends (Replicate, Runway, etc.)."""

from app.domain.ai.providers.base import AIProvider
from app.domain.ai.types import AIJobRequest, AIJobResult


class MediaStubProvider(AIProvider):
    id = "media_stub"
    label = "Media Stub"
    supports_modules = frozenset({"image", "video", "thumbnail"})

    def is_available(self) -> bool:
        return True

    def generate(self, request: AIJobRequest) -> AIJobResult:
        return AIJobResult(
            output_text=f"[{request.module.upper()}] Media job queued for: {request.prompt[:500]}",
            result_url=None,
            meta={
                "provider": self.id,
                "media_type": request.module,
                "note": "Plug in a real media provider via ProviderRegistry.register()",
            },
            provider=self.id,
        )
