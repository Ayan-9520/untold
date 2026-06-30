"""Cloud video generation providers."""

from __future__ import annotations

import logging

from app.core.config import get_settings
from app.domain.video.providers.base import VideoProvider
from app.domain.video.providers.demo import DemoVideoProvider
from app.domain.video.providers.video_client import (
    aspect_to_dimensions,
    generate_google_veo,
    generate_hailuo,
    generate_kling,
    generate_luma,
    generate_pika,
    generate_replicate_video,
    generate_runway,
    upload_video_bytes,
)
from app.domain.video.types import VideoGenerateRequest, VideoGenerateResult

logger = logging.getLogger("untold.video")


class _BaseCloudVideoProvider(VideoProvider):
    def _result(
        self,
        request: VideoGenerateRequest,
        data: bytes,
        *,
        mime: str = "video/mp4",
        preview_url: str | None = None,
        **meta,
    ) -> VideoGenerateResult:
        uploaded = upload_video_bytes(data, project_id=request.project_id, mime_type=mime)
        return VideoGenerateResult(
            output_text=f"{self.label}: {request.prompt[:200]}",
            result_url=uploaded["url"],
            preview_url=preview_url,
            r2_key=uploaded["key"],
            mime_type=mime,
            duration_seconds=request.duration_seconds,
            provider=self.id,
            meta={
                "video_type": request.video_type,
                "aspect_ratio": request.aspect_ratio,
                "format": "mp4",
                **meta,
            },
        )

    def _fallback(self, request: VideoGenerateRequest, error: str) -> VideoGenerateResult:
        logger.warning("%s failed (%s), using demo fallback", self.id, error)
        result = DemoVideoProvider().generate(request)
        result.meta = dict(result.meta or {})
        result.meta["fallback"] = True
        result.meta["error"] = error
        result.meta["requested_provider"] = self.id
        return result


class RunwayProvider(_BaseCloudVideoProvider):
    id = "runway"
    label = "Runway"

    def is_available(self) -> bool:
        return bool(get_settings().runway_api_key)

    def generate(self, request: VideoGenerateRequest) -> VideoGenerateResult:
        s = get_settings()
        try:
            data = generate_runway(
                api_key=s.runway_api_key or "",
                model=s.runway_model,
                prompt=request.prompt,
                duration=request.duration_seconds,
                aspect_ratio=request.aspect_ratio,
            )
            return self._result(request, data, model=s.runway_model)
        except Exception as exc:
            return self._fallback(request, str(exc))


class GoogleVeoProvider(_BaseCloudVideoProvider):
    id = "google_veo"
    label = "Google Veo"

    def is_available(self) -> bool:
        s = get_settings()
        return bool(s.google_veo_api_key or s.gemini_api_key)

    def generate(self, request: VideoGenerateRequest) -> VideoGenerateResult:
        s = get_settings()
        api_key = s.google_veo_api_key or s.gemini_api_key or ""
        try:
            data = generate_google_veo(
                api_key=api_key,
                model=s.google_veo_model,
                prompt=request.prompt,
                aspect_ratio=request.aspect_ratio,
            )
            return self._result(request, data, model=s.google_veo_model)
        except Exception as exc:
            return self._fallback(request, str(exc))


class LumaProvider(_BaseCloudVideoProvider):
    id = "luma"
    label = "Luma"

    def is_available(self) -> bool:
        return bool(get_settings().luma_api_key)

    def generate(self, request: VideoGenerateRequest) -> VideoGenerateResult:
        s = get_settings()
        try:
            data = generate_luma(
                api_key=s.luma_api_key or "",
                prompt=request.prompt,
                aspect_ratio=request.aspect_ratio,
            )
            return self._result(request, data)
        except Exception as exc:
            return self._fallback(request, str(exc))


class PikaProvider(_BaseCloudVideoProvider):
    id = "pika"
    label = "Pika"

    def is_available(self) -> bool:
        return bool(get_settings().pika_api_key)

    def generate(self, request: VideoGenerateRequest) -> VideoGenerateResult:
        s = get_settings()
        try:
            data = generate_pika(
                api_key=s.pika_api_key or "",
                prompt=request.prompt,
                aspect_ratio=request.aspect_ratio,
            )
            return self._result(request, data)
        except Exception as exc:
            return self._fallback(request, str(exc))


class KlingProvider(_BaseCloudVideoProvider):
    id = "kling"
    label = "Kling"

    def is_available(self) -> bool:
        return bool(get_settings().kling_api_key)

    def generate(self, request: VideoGenerateRequest) -> VideoGenerateResult:
        s = get_settings()
        try:
            data = generate_kling(
                api_key=s.kling_api_key or "",
                api_secret=s.kling_api_secret,
                prompt=request.prompt,
                duration=request.duration_seconds,
                aspect_ratio=request.aspect_ratio,
            )
            return self._result(request, data)
        except Exception as exc:
            return self._fallback(request, str(exc))


class HailuoProvider(_BaseCloudVideoProvider):
    id = "hailuo"
    label = "Hailuo"

    def is_available(self) -> bool:
        s = get_settings()
        return bool(s.hailuo_api_key and s.hailuo_group_id)

    def generate(self, request: VideoGenerateRequest) -> VideoGenerateResult:
        s = get_settings()
        try:
            data = generate_hailuo(
                api_key=s.hailuo_api_key or "",
                group_id=s.hailuo_group_id or "",
                prompt=request.prompt,
            )
            return self._result(request, data)
        except Exception as exc:
            return self._fallback(request, str(exc))


class ReplicateVideoProvider(_BaseCloudVideoProvider):
    id = "replicate"
    label = "Replicate"

    def is_available(self) -> bool:
        return bool(get_settings().replicate_api_token)

    def generate(self, request: VideoGenerateRequest) -> VideoGenerateResult:
        s = get_settings()
        w, h = aspect_to_dimensions(request.aspect_ratio, request.width, request.height)
        try:
            data = generate_replicate_video(
                api_token=s.replicate_api_token or "",
                model=s.replicate_video_model,
                input_payload={
                    "prompt": request.prompt,
                    "duration": request.duration_seconds,
                    "aspect_ratio": request.aspect_ratio,
                    "width": w,
                    "height": h,
                },
            )
            return self._result(request, data, model=s.replicate_video_model)
        except Exception as exc:
            return self._fallback(request, str(exc))


CLOUD_VIDEO_PROVIDER_CLASSES: list[type[_BaseCloudVideoProvider]] = [
    RunwayProvider,
    GoogleVeoProvider,
    LumaProvider,
    PikaProvider,
    KlingProvider,
    HailuoProvider,
    ReplicateVideoProvider,
]


def get_cloud_video_providers() -> list[VideoProvider]:
    return [cls() for cls in CLOUD_VIDEO_PROVIDER_CLASSES]
