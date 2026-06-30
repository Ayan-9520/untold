"""Cloud image generation providers."""

from __future__ import annotations

import logging

from app.domain.image.providers.image_client import (
    aspect_to_size,
    generate_fal,
    generate_flux_bfl,
    generate_google_imagen,
    generate_ideogram,
    generate_openai_images,
    generate_replicate,
    generate_stability,
    upload_image_bytes,
)
from app.core.config import get_settings
from app.domain.image.providers.base import ImageProvider
from app.domain.image.providers.demo import DemoImageProvider
from app.domain.image.types import ImageGenerateRequest, ImageGenerateResult

logger = logging.getLogger("untold.ai.image")

_IDEOGRAM_ASPECT = {
    "16:9": "ASPECT_16_9",
    "9:16": "ASPECT_9_16",
    "1:1": "ASPECT_1_1",
    "4:3": "ASPECT_4_3",
    "3:4": "ASPECT_3_4",
}


class _BaseCloudImageProvider(ImageProvider):
    def _result(
        self,
        request: ImageGenerateRequest,
        data: bytes,
        mime: str = "image/png",
        ext: str = "png",
        **meta,
    ) -> ImageGenerateResult:
        uploaded = upload_image_bytes(data, mime, project_id=request.project_id, ext=ext)
        return ImageGenerateResult(
            output_text=f"{self.label}: {request.prompt[:200]}",
            result_url=uploaded["url"],
            r2_key=uploaded["key"],
            mime_type=mime,
            size_bytes=uploaded["size_bytes"],
            provider=self.id,
            meta={"image_type": request.image_type, "action": request.action, **meta},
        )

    def _fallback(self, request: ImageGenerateRequest, error: str) -> ImageGenerateResult:
        logger.warning("%s failed (%s), using demo fallback", self.id, error)
        result = DemoImageProvider().generate(request)
        result.meta = dict(result.meta or {})
        result.meta["fallback"] = True
        result.meta["error"] = error
        result.meta["requested_provider"] = self.id
        return result


class OpenAIImagesProvider(_BaseCloudImageProvider):
    id = "openai_images"
    label = "OpenAI Images"

    def is_available(self) -> bool:
        return bool(get_settings().openai_api_key)

    def generate(self, request: ImageGenerateRequest) -> ImageGenerateResult:
        s = get_settings()
        try:
            data = generate_openai_images(
                api_key=s.openai_api_key or "",
                model=s.openai_image_model,
                prompt=request.prompt,
                aspect_ratio=request.aspect_ratio,
            )
            return self._result(request, data, model=s.openai_image_model)
        except Exception as exc:
            return self._fallback(request, str(exc))


class GoogleImagenProvider(_BaseCloudImageProvider):
    id = "google_imagen"
    label = "Google Imagen"

    def is_available(self) -> bool:
        s = get_settings()
        return bool(s.gemini_api_key or s.google_imagen_api_key)

    def generate(self, request: ImageGenerateRequest) -> ImageGenerateResult:
        s = get_settings()
        api_key = s.google_imagen_api_key or s.gemini_api_key or ""
        try:
            data = generate_google_imagen(
                api_key=api_key,
                model=s.google_imagen_model,
                prompt=request.prompt,
                aspect_ratio=request.aspect_ratio,
            )
            return self._result(request, data, model=s.google_imagen_model)
        except Exception as exc:
            return self._fallback(request, str(exc))


class StabilityAIProvider(_BaseCloudImageProvider):
    id = "stability"
    label = "Stability AI"

    def is_available(self) -> bool:
        return bool(get_settings().stability_api_key)

    def generate(self, request: ImageGenerateRequest) -> ImageGenerateResult:
        s = get_settings()
        w, h = aspect_to_size(request.aspect_ratio, request.width, request.height)
        try:
            data = generate_stability(
                api_key=s.stability_api_key or "",
                prompt=request.prompt,
                width=w,
                height=h,
            )
            return self._result(request, data, model=s.stability_model)
        except Exception as exc:
            return self._fallback(request, str(exc))


class IdeogramProvider(_BaseCloudImageProvider):
    id = "ideogram"
    label = "Ideogram"

    def is_available(self) -> bool:
        return bool(get_settings().ideogram_api_key)

    def generate(self, request: ImageGenerateRequest) -> ImageGenerateResult:
        s = get_settings()
        aspect = _IDEOGRAM_ASPECT.get(request.aspect_ratio, "ASPECT_16_9")
        try:
            data = generate_ideogram(
                api_key=s.ideogram_api_key or "",
                prompt=request.prompt,
                aspect_ratio=aspect,
            )
            return self._result(request, data)
        except Exception as exc:
            return self._fallback(request, str(exc))


class FluxProvider(_BaseCloudImageProvider):
    id = "flux"
    label = "Flux"

    def is_available(self) -> bool:
        return bool(get_settings().flux_api_key)

    def generate(self, request: ImageGenerateRequest) -> ImageGenerateResult:
        s = get_settings()
        w, h = aspect_to_size(request.aspect_ratio, request.width, request.height)
        try:
            data = generate_flux_bfl(
                api_key=s.flux_api_key or "",
                model=s.flux_model,
                prompt=request.prompt,
                width=w,
                height=h,
            )
            return self._result(request, data, model=s.flux_model)
        except Exception as exc:
            return self._fallback(request, str(exc))


class ReplicateImageProvider(_BaseCloudImageProvider):
    id = "replicate"
    label = "Replicate"

    def is_available(self) -> bool:
        return bool(get_settings().replicate_api_token)

    def generate(self, request: ImageGenerateRequest) -> ImageGenerateResult:
        s = get_settings()
        w, h = aspect_to_size(request.aspect_ratio, request.width, request.height)
        try:
            data = generate_replicate(
                api_token=s.replicate_api_token or "",
                model=s.replicate_image_model,
                input_payload={
                    "prompt": request.prompt,
                    "width": w,
                    "height": h,
                    "aspect_ratio": request.aspect_ratio,
                },
            )
            return self._result(request, data, model=s.replicate_image_model)
        except Exception as exc:
            return self._fallback(request, str(exc))


class FalImageProvider(_BaseCloudImageProvider):
    id = "fal"
    label = "Fal.ai"

    def is_available(self) -> bool:
        return bool(get_settings().fal_api_key)

    def generate(self, request: ImageGenerateRequest) -> ImageGenerateResult:
        s = get_settings()
        w, h = aspect_to_size(request.aspect_ratio, request.width, request.height)
        try:
            data = generate_fal(
                api_key=s.fal_api_key or "",
                model=s.fal_image_model,
                input_payload={
                    "prompt": request.prompt,
                    "image_size": {"width": w, "height": h},
                    "num_images": 1,
                },
            )
            return self._result(request, data, model=s.fal_image_model)
        except Exception as exc:
            return self._fallback(request, str(exc))


CLOUD_IMAGE_PROVIDER_CLASSES: list[type[_BaseCloudImageProvider]] = [
    OpenAIImagesProvider,
    GoogleImagenProvider,
    StabilityAIProvider,
    IdeogramProvider,
    FluxProvider,
    ReplicateImageProvider,
    FalImageProvider,
]


def get_cloud_image_providers() -> list[ImageProvider]:
    return [cls() for cls in CLOUD_IMAGE_PROVIDER_CLASSES]
