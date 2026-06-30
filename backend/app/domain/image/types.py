"""Image generation — vendor-neutral types."""

from dataclasses import dataclass, field
from typing import Any


IMAGE_TYPES = (
    "poster",
    "thumbnail",
    "concept_art",
    "environment",
    "illustration",
    "sports",
    "background",
)

IMAGE_ACTIONS = ("generate", "upscale", "variation")


@dataclass
class ImageGenerateRequest:
    prompt: str
    image_type: str = "illustration"
    action: str = "generate"
    aspect_ratio: str = "16:9"
    width: int = 1024
    height: int = 576
    seed: int | None = None
    source_url: str | None = None
    source_prompt: str | None = None
    project_id: int | None = None
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class ImageGenerateResult:
    output_text: str = ""
    result_url: str | None = None
    r2_key: str | None = None
    mime_type: str = "image/svg+xml"
    size_bytes: int = 0
    provider: str = "demo"
    meta: dict[str, Any] = field(default_factory=dict)
