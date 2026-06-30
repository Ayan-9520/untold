"""Translation studio — vendor-neutral types."""

from dataclasses import dataclass, field
from typing import Any


TRANSLATION_LANGUAGES = (
    ("en", "English"),
    ("hi", "Hindi"),
    ("ar", "Arabic"),
    ("es", "Spanish"),
    ("fr", "French"),
    ("ja", "Japanese"),
    ("de", "German"),
    ("pt", "Portuguese"),
    ("zh", "Chinese"),
    ("ru", "Russian"),
)

CONTENT_TYPES = (
    "script",
    "voice",
    "subtitles",
    "metadata",
    "description",
    "title",
)

CONTENT_TYPE_LABELS = {
    "script": "Script",
    "voice": "Voice / Narration",
    "subtitles": "Subtitles",
    "metadata": "Metadata",
    "description": "Description",
    "title": "Title",
}


@dataclass
class TranslationRequest:
    source_text: str
    content_type: str = "script"
    source_lang: str = "en"
    target_lang: str = "es"
    auto_sync: bool = True
    generate_srt: bool = True
    generate_vtt: bool = True
    project_id: int | None = None
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class TranslationResult:
    output_text: str = ""
    translated_text: str = ""
    result_url: str | None = None
    r2_key: str | None = None
    srt_content: str | None = None
    vtt_content: str | None = None
    srt_url: str | None = None
    vtt_url: str | None = None
    provider: str = "demo"
    tm_hit: bool = False
    meta: dict[str, Any] = field(default_factory=dict)
