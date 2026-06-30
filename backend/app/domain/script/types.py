"""Script AI writer — vendor-neutral request/result types."""

from dataclasses import dataclass, field
from typing import Any


SCRIPT_ACTIONS = (
    "generate",
    "rewrite",
    "expand",
    "shorten",
    "grammar",
    "tone",
    "style_netflix",
    "style_bbc",
    "style_espn",
    "style_documentary",
    "style_interview",
    "style_podcast",
    "translate",
    "chapter",
    "scene",
    "hook",
    "cta",
)

STYLE_ACTIONS = {
    "style_netflix": "netflix",
    "style_bbc": "bbc",
    "style_espn": "espn",
    "style_documentary": "documentary",
}


@dataclass
class ScriptAgentRequest:
    action: str
    title: str
    prompt: str | None
    content: str
    selection: str | None = None
    style: str = "documentary"
    target_language: str = "es"
    tone: str | None = None
    context: dict[str, Any] = field(default_factory=dict)
    project_id: int | None = None
    script_id: int | None = None


@dataclass
class ScriptAgentResult:
    result: str = ""
    suggested_style: str | None = None
    provider: str = "demo"
    meta: dict[str, Any] = field(default_factory=dict)
