"""Short-form video generation types."""

from dataclasses import dataclass, field
from typing import Any


SHORTS_PLATFORMS = (
    "instagram_reels",
    "youtube_shorts",
    "tiktok",
    "facebook_reels",
)

PLATFORM_LABELS = {
    "instagram_reels": "Instagram Reels",
    "youtube_shorts": "YouTube Shorts",
    "tiktok": "TikTok",
    "facebook_reels": "Facebook Reels",
}

PUBLISH_PLATFORM_MAP = {
    "instagram_reels": "instagram",
    "youtube_shorts": "youtube",
    "tiktok": "instagram",
    "facebook_reels": "facebook",
}


@dataclass
class ShortsGenerateRequest:
    source_video_url: str
    topic: str = ""
    platforms: list[str] = field(default_factory=lambda: list(SHORTS_PLATFORMS))
    auto_highlights: bool = True
    captions: bool = True
    auto_zoom: bool = True
    hook_optimization: bool = True
    clip_duration_seconds: int = 30
    aspect_ratio: str = "9:16"
    project_id: int | None = None
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class ShortsGenerateResult:
    output_text: str = ""
    result_url: str | None = None
    r2_key: str | None = None
    mime_type: str = "text/html"
    provider: str = "demo"
    highlights: list[dict] = field(default_factory=list)
    clips: list[dict] = field(default_factory=list)
    thumbnail_url: str | None = None
    hashtags: list[str] = field(default_factory=list)
    hook: str = ""
    captions_vtt: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)
