"""Background music generation — vendor-neutral types."""

from dataclasses import dataclass, field
from typing import Any


MUSIC_CATEGORIES = (
    "sports",
    "drama",
    "epic",
    "corporate",
    "technology",
    "suspense",
    "documentary",
)

_CATEGORY_DEFAULTS: dict[str, dict[str, Any]] = {
    "sports": {"bpm": 128, "key": "E minor", "mood": "driving"},
    "drama": {"bpm": 72, "key": "D minor", "mood": "emotional"},
    "epic": {"bpm": 96, "key": "C minor", "mood": "cinematic"},
    "corporate": {"bpm": 100, "key": "G major", "mood": "uplifting"},
    "technology": {"bpm": 110, "key": "A minor", "mood": "modern"},
    "suspense": {"bpm": 80, "key": "F minor", "mood": "tense"},
    "documentary": {"bpm": 68, "key": "D major", "mood": "reflective"},
}


@dataclass
class MusicGenerateRequest:
    prompt: str
    category: str = "documentary"
    duration_seconds: int = 60
    loop: bool = True
    fade_in_seconds: float = 2.0
    fade_out_seconds: float = 3.0
    project_id: int | None = None
    meta: dict[str, Any] = field(default_factory=dict)

    def category_defaults(self) -> dict[str, Any]:
        return _CATEGORY_DEFAULTS.get(self.category, _CATEGORY_DEFAULTS["documentary"])


@dataclass
class MusicGenerateResult:
    output_text: str = ""
    result_url: str | None = None
    r2_key: str | None = None
    mime_type: str = "audio/wav"
    duration_seconds: float = 60.0
    provider: str = "demo"
    meta: dict[str, Any] = field(default_factory=dict)
