"""Voice generation — vendor-neutral types."""

from dataclasses import dataclass, field
from typing import Any


VOICE_LANGUAGES = (
    ("en", "English"),
    ("hi", "Hindi"),
    ("ar", "Arabic"),
    ("es", "Spanish"),
    ("fr", "French"),
    ("ja", "Japanese"),
)

VOICE_EMOTIONS = (
    "neutral",
    "warm",
    "dramatic",
    "energetic",
    "calm",
    "authoritative",
)

VOICES_BY_LANGUAGE: dict[str, list[dict[str, str]]] = {
    "en": [
        {"id": "en-documentary", "label": "Documentary (Neutral)"},
        {"id": "en-warm", "label": "Warm Narrator"},
        {"id": "en-energetic", "label": "Sports Energetic"},
    ],
    "hi": [
        {"id": "hi-neutral", "label": "Hindi Neutral"},
        {"id": "hi-warm", "label": "Hindi Warm"},
    ],
    "ar": [
        {"id": "ar-neutral", "label": "Arabic Neutral"},
        {"id": "ar-formal", "label": "Arabic Formal"},
    ],
    "es": [
        {"id": "es-neutral", "label": "Spanish Neutral"},
        {"id": "es-warm", "label": "Spanish Warm"},
    ],
    "fr": [
        {"id": "fr-neutral", "label": "French Neutral"},
        {"id": "fr-elegant", "label": "French Elegant"},
    ],
    "ja": [
        {"id": "ja-neutral", "label": "Japanese Neutral"},
        {"id": "ja-calm", "label": "Japanese Calm"},
    ],
}


@dataclass
class VoiceGenerateRequest:
    text: str
    language: str = "en"
    emotion: str = "neutral"
    pitch: float = 1.0
    speed: float = 1.0
    voice_id: str = "en-documentary"
    translate_to: str | None = None
    sync_subtitles: bool = True
    project_id: int | None = None
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class VoiceGenerateResult:
    output_text: str = ""
    result_url: str | None = None
    r2_key: str | None = None
    mime_type: str = "audio/wav"
    duration_seconds: float = 0.0
    provider: str = "demo"
    subtitles_url: str | None = None
    subtitles_srt: str | None = None
    subtitles_vtt: str | None = None
    translated_text: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)
