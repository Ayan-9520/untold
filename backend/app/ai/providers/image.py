"""Image generation providers — facade to image studio registry."""

from __future__ import annotations

from app.ai.providers.base import ImageProvider as BaseImageProvider
from app.domain.image.types import ImageGenerateRequest


class ImageRegistryAdapter(BaseImageProvider):
    """Delegates to the image studio domain registry."""

    id = "image_registry"
    label = "Image Studio Registry"

    def is_available(self) -> bool:
        from app.domain.image.providers.registry import get_image_registry

        return bool(get_image_registry().list_providers())

    def generate(self, request: ImageGenerateRequest, provider_id: str | None = None):
        from app.domain.image.providers.registry import get_image_registry

        return get_image_registry().generate(request, provider_id)


def list_image_providers() -> list[dict]:
    from app.domain.image.providers.registry import get_image_registry

    return get_image_registry().list_providers()


def generate_image(request: ImageGenerateRequest, provider_id: str | None = None):
    from app.domain.image.providers.registry import get_image_registry

    return get_image_registry().generate(request, provider_id)
