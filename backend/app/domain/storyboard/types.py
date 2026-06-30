"""Storyboard AI generator — vendor-neutral types."""

from dataclasses import dataclass, field
from typing import Any


STORYBOARD_ACTIONS = ("generate_from_script", "regenerate_scene")


@dataclass
class StoryboardAgentRequest:
    action: str
    project_title: str
    script_content: str
    prompt: str | None = None
    existing_scenes: list[dict] = field(default_factory=list)
    default_duration_seconds: int = 15
    context: dict[str, Any] = field(default_factory=dict)
    project_id: int | None = None


@dataclass
class StoryboardAgentResult:
    scenes: list[dict] = field(default_factory=list)
    summary: str = ""
    provider: str = "demo"
    meta: dict[str, Any] = field(default_factory=dict)
