"""Video generation — vendor-neutral types."""

from dataclasses import dataclass, field
from typing import Any


VIDEO_TYPES = (
    "b_roll",
    "drone",
    "animation",
    "sports_intro",
    "cinematic",
    "motion_graphics",
    "slow_motion",
)


@dataclass
class VideoGenerateRequest:
    prompt: str
    video_type: str = "b_roll"
    duration_seconds: int = 8
    aspect_ratio: str = "16:9"
    fps: int = 24
    width: int = 1280
    height: int = 720
    project_id: int | None = None
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class VideoGenerateResult:
    output_text: str = ""
    result_url: str | None = None
    preview_url: str | None = None
    r2_key: str | None = None
    mime_type: str = "text/html"
    duration_seconds: int = 8
    provider: str = "demo"
    meta: dict[str, Any] = field(default_factory=dict)
