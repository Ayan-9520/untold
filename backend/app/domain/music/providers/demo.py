"""Demo music provider — original background WAV scores."""

from __future__ import annotations

import uuid

from app.domain.music.providers.base import MusicProvider
from app.domain.music.types import MUSIC_CATEGORIES, MusicGenerateRequest, MusicGenerateResult
from app.domain.music.wav_builder import build_music_wav
from app.domain.storage.registry import upload_bytes

_CATEGORY_LABELS = {
    "sports": "Sports",
    "drama": "Drama",
    "epic": "Epic",
    "corporate": "Corporate",
    "technology": "Technology",
    "suspense": "Suspense",
    "documentary": "Documentary",
}


class DemoMusicProvider(MusicProvider):
    id = "demo"
    label = "Demo Music Generator (WAV)"

    def is_available(self) -> bool:
        return True

    def generate(self, request: MusicGenerateRequest) -> MusicGenerateResult:
        category = request.category if request.category in MUSIC_CATEGORIES else "documentary"
        defaults = request.category_defaults()
        duration = max(10, min(request.duration_seconds, 180))
        wav = build_music_wav(
            duration,
            category=category,
            loop=request.loop,
            fade_in=request.fade_in_seconds,
            fade_out=request.fade_out_seconds,
            bpm=int(defaults.get("bpm", 72)),
        )

        folder = request.project_id or "studio"
        key = f"ai-music/{folder}/{uuid.uuid4().hex}.wav"
        uploaded = upload_bytes(key, wav, "audio/wav")
        label = _CATEGORY_LABELS.get(category, category.title())

        brief = (
            f"{label} background score · {defaults.get('bpm')} BPM · {defaults.get('key')} · "
            f"{duration}s · loop={'on' if request.loop else 'off'}"
        )

        return MusicGenerateResult(
            output_text=f"{brief}\n\nMood brief: {request.prompt[:400]}",
            result_url=uploaded.url,
            r2_key=uploaded.key,
            mime_type="audio/wav",
            duration_seconds=float(duration),
            provider=self.id,
            meta={
                "category": category,
                "duration_seconds": duration,
                "loop": request.loop,
                "fade_in_seconds": request.fade_in_seconds,
                "fade_out_seconds": request.fade_out_seconds,
                "bpm": defaults.get("bpm"),
                "key": defaults.get("key"),
                "mood": defaults.get("mood"),
                "size_bytes": len(wav),
                "simulated": True,
            },
        )
