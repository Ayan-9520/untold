"""Workflow node catalog — types available in the visual builder."""

from __future__ import annotations

AGENT_NODE_TYPES: tuple[str, ...] = (
    "research",
    "script",
    "storyboard",
    "image",
    "video",
    "voice",
    "music",
    "seo",
    "translation",
    "publishing",
    "analytics",
)

CONTROL_NODE_TYPES: tuple[str, ...] = (
    "approval",
    "condition",
    "loop",
    "parallel",
    "delay",
    "notification",
)

ALL_NODE_TYPES: tuple[str, ...] = AGENT_NODE_TYPES + CONTROL_NODE_TYPES

NODE_CATALOG: list[dict] = [
    {"type": "research", "label": "Research", "category": "agent", "icon": "🔍", "default_timeout": 300, "default_retries": 2},
    {"type": "script", "label": "Script", "category": "agent", "icon": "📝", "default_timeout": 300, "default_retries": 2},
    {"type": "storyboard", "label": "Storyboard", "category": "agent", "icon": "🎬", "default_timeout": 240, "default_retries": 2},
    {"type": "image", "label": "Image", "category": "agent", "icon": "🖼️", "default_timeout": 600, "default_retries": 2},
    {"type": "video", "label": "Video", "category": "agent", "icon": "📹", "default_timeout": 900, "default_retries": 2},
    {"type": "voice", "label": "Voice", "category": "agent", "icon": "🎙️", "default_timeout": 600, "default_retries": 2},
    {"type": "music", "label": "Music", "category": "agent", "icon": "🎵", "default_timeout": 600, "default_retries": 2},
    {"type": "seo", "label": "SEO", "category": "agent", "icon": "📊", "default_timeout": 180, "default_retries": 2},
    {"type": "translation", "label": "Translation", "category": "agent", "icon": "🌐", "default_timeout": 300, "default_retries": 2},
    {"type": "approval", "label": "Approval", "category": "control", "icon": "✅", "default_timeout": None, "default_retries": 0},
    {"type": "publishing", "label": "Publishing", "category": "agent", "icon": "🚀", "default_timeout": 300, "default_retries": 2},
    {"type": "analytics", "label": "Analytics", "category": "agent", "icon": "📈", "default_timeout": 60, "default_retries": 1},
    {"type": "condition", "label": "Condition", "category": "control", "icon": "⑂", "default_timeout": 30, "default_retries": 0},
    {"type": "loop", "label": "Loop", "category": "control", "icon": "🔁", "default_timeout": None, "default_retries": 0},
    {"type": "parallel", "label": "Parallel", "category": "control", "icon": "⚡", "default_timeout": None, "default_retries": 0},
    {"type": "delay", "label": "Delay / Schedule", "category": "control", "icon": "⏱️", "default_timeout": None, "default_retries": 0},
    {"type": "notification", "label": "Notification", "category": "control", "icon": "🔔", "default_timeout": 30, "default_retries": 0},
]

AGENT_TO_ENGINE_STEP: dict[str, str] = {
    "research": "research",
    "script": "script",
    "storyboard": "storyboard",
    "image": "image",
    "video": "video",
    "voice": "voice",
    "music": "music",
    "seo": "seo",
    "translation": "translation",
    "publishing": "publisher",
    "analytics": "analytics",
}
