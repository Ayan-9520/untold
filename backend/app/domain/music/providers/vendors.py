"""Cloud music generation providers."""

from __future__ import annotations

import logging

from app.core.config import get_settings
from app.domain.music.providers.base import MusicProvider
from app.domain.music.providers.demo import DemoMusicProvider
from app.domain.music.providers.music_client import (
    generate_elevenlabs_music,
    generate_fal_music,
    generate_replicate_music,
    generate_stable_audio,
    generate_suno,
    generate_udio,
    upload_music_bytes,
)
from app.domain.music.types import MUSIC_CATEGORIES, MusicGenerateRequest, MusicGenerateResult

logger = logging.getLogger("untold.music")


class _BaseCloudMusicProvider(MusicProvider):
    def _finish(
        self,
        request: MusicGenerateRequest,
        audio_bytes: bytes,
        mime_type: str,
        **meta,
    ) -> MusicGenerateResult:
        uploaded = upload_music_bytes(audio_bytes, mime_type, project_id=request.project_id)
        defaults = request.category_defaults()
        duration = float(request.duration_seconds)
        label = request.category.title()
        brief = (
            f"{label} background score · {defaults.get('bpm')} BPM · {defaults.get('key')} · "
            f"{int(duration)}s · loop={'on' if request.loop else 'off'}"
        )
        return MusicGenerateResult(
            output_text=f"{brief}\n\nMood brief: {request.prompt[:400]}",
            result_url=uploaded["url"],
            r2_key=uploaded["key"],
            mime_type=mime_type,
            duration_seconds=duration,
            provider=self.id,
            meta={
                "category": request.category,
                "duration_seconds": duration,
                "loop": request.loop,
                "fade_in_seconds": request.fade_in_seconds,
                "fade_out_seconds": request.fade_out_seconds,
                "bpm": defaults.get("bpm"),
                "key": defaults.get("key"),
                "mood": defaults.get("mood"),
                "size_bytes": uploaded["size_bytes"],
                **meta,
            },
        )

    def _fallback(self, request: MusicGenerateRequest, error: str) -> MusicGenerateResult:
        logger.warning("%s failed (%s), using demo fallback", self.id, error)
        result = DemoMusicProvider().generate(request)
        result.meta = dict(result.meta or {})
        result.meta["fallback"] = True
        result.meta["error"] = error
        result.meta["requested_provider"] = self.id
        return result

    def _category(self, request: MusicGenerateRequest) -> str:
        return request.category if request.category in MUSIC_CATEGORIES else "documentary"


class SunoProvider(_BaseCloudMusicProvider):
    id = "suno"
    label = "Suno"

    def is_available(self) -> bool:
        return bool(get_settings().suno_api_key)

    def generate(self, request: MusicGenerateRequest) -> MusicGenerateResult:
        s = get_settings()
        try:
            audio, mime = generate_suno(
                api_key=s.suno_api_key or "",
                base_url=s.suno_api_base_url,
                prompt=request.prompt,
                duration=request.duration_seconds,
                category=self._category(request),
            )
            return self._finish(request, audio, mime)
        except Exception as exc:
            return self._fallback(request, str(exc))


class UdioProvider(_BaseCloudMusicProvider):
    id = "udio"
    label = "Udio"

    def is_available(self) -> bool:
        return bool(get_settings().udio_api_key)

    def generate(self, request: MusicGenerateRequest) -> MusicGenerateResult:
        s = get_settings()
        try:
            audio, mime = generate_udio(
                api_key=s.udio_api_key or "",
                base_url=s.udio_api_base_url,
                prompt=request.prompt,
                duration=request.duration_seconds,
                category=self._category(request),
            )
            return self._finish(request, audio, mime)
        except Exception as exc:
            return self._fallback(request, str(exc))


class StableAudioProvider(_BaseCloudMusicProvider):
    id = "stable_audio"
    label = "Stable Audio"

    def is_available(self) -> bool:
        s = get_settings()
        return bool(s.stable_audio_api_key or s.stability_api_key)

    def generate(self, request: MusicGenerateRequest) -> MusicGenerateResult:
        s = get_settings()
        api_key = s.stable_audio_api_key or s.stability_api_key or ""
        try:
            audio, mime = generate_stable_audio(
                api_key=api_key,
                prompt=request.prompt,
                duration=request.duration_seconds,
                category=self._category(request),
            )
            return self._finish(request, audio, mime, engine="stable-audio-2")
        except Exception as exc:
            return self._fallback(request, str(exc))


class ElevenLabsMusicProvider(_BaseCloudMusicProvider):
    id = "elevenlabs_music"
    label = "ElevenLabs Music"

    def is_available(self) -> bool:
        return bool(get_settings().elevenlabs_api_key)

    def generate(self, request: MusicGenerateRequest) -> MusicGenerateResult:
        s = get_settings()
        try:
            audio, mime = generate_elevenlabs_music(
                api_key=s.elevenlabs_api_key or "",
                prompt=request.prompt,
                duration=request.duration_seconds,
                category=self._category(request),
            )
            return self._finish(request, audio, mime, engine="sound-generation")
        except Exception as exc:
            return self._fallback(request, str(exc))


class ReplicateMusicProvider(_BaseCloudMusicProvider):
    id = "replicate"
    label = "Replicate"

    def is_available(self) -> bool:
        return bool(get_settings().replicate_api_token)

    def generate(self, request: MusicGenerateRequest) -> MusicGenerateResult:
        s = get_settings()
        try:
            audio, mime = generate_replicate_music(
                api_token=s.replicate_api_token or "",
                model=s.replicate_music_model,
                prompt=request.prompt,
                duration=request.duration_seconds,
                category=self._category(request),
            )
            return self._finish(request, audio, mime, model=s.replicate_music_model)
        except Exception as exc:
            return self._fallback(request, str(exc))


class FalMusicProvider(_BaseCloudMusicProvider):
    id = "fal"
    label = "Fal.ai"

    def is_available(self) -> bool:
        return bool(get_settings().fal_api_key)

    def generate(self, request: MusicGenerateRequest) -> MusicGenerateResult:
        s = get_settings()
        try:
            audio, mime = generate_fal_music(
                api_key=s.fal_api_key or "",
                model=s.fal_music_model,
                prompt=request.prompt,
                duration=request.duration_seconds,
                category=self._category(request),
            )
            return self._finish(request, audio, mime, model=s.fal_music_model)
        except Exception as exc:
            return self._fallback(request, str(exc))


CLOUD_MUSIC_PROVIDER_CLASSES: list[type[_BaseCloudMusicProvider]] = [
    SunoProvider,
    UdioProvider,
    StableAudioProvider,
    ElevenLabsMusicProvider,
    ReplicateMusicProvider,
    FalMusicProvider,
]


def get_cloud_music_providers() -> list[MusicProvider]:
    return [cls() for cls in CLOUD_MUSIC_PROVIDER_CLASSES]
