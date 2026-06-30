"""Mutable state passed between workflow agents."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class WorkflowContext:
    topic: str
    project_id: int | None
    providers: dict[str, str | None] = field(default_factory=dict)
    publish_platforms: list[str] = field(default_factory=lambda: ["originals", "youtube"])

    research_text: str = ""
    script_text: str = ""
    storyboard_summary: str = ""
    storyboard_scenes: list[dict] = field(default_factory=list)

    image_text: str = ""
    image_url: str | None = None

    voice_text: str = ""
    voice_url: str | None = None

    video_text: str = ""
    video_url: str | None = None

    music_text: str = ""
    music_url: str | None = None

    seo_text: str = ""
    seo_variants: list[dict] = field(default_factory=list)

    timeline_summary: str = ""
    analytics_summary: str = ""

    publish_run_id: int | None = None
    publish_summary: str = ""

    prompts: dict[str, str] = field(default_factory=dict)
    translation_language: str | None = None
    translation_text: str = ""

    def script_excerpt(self, limit: int = 1200) -> str:
        return (self.script_text or self.research_text or self.topic)[:limit]
