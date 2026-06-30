"""Workflow Engine — agent step definitions (Idea → Analytics)."""

from __future__ import annotations

WORKFLOW_AGENTS: list[dict[str, str]] = [
    {"id": "idea", "label": "Idea"},
    {"id": "research", "label": "AI Research"},
    {"id": "script", "label": "AI Script"},
    {"id": "storyboard", "label": "AI Storyboard"},
    {"id": "image", "label": "AI Images"},
    {"id": "video", "label": "AI Video Clips"},
    {"id": "voice", "label": "AI Voice"},
    {"id": "music", "label": "AI Music"},
    {"id": "timeline", "label": "Timeline Editor"},
    {"id": "seo", "label": "AI SEO"},
    {"id": "translation", "label": "AI Translation"},
    {"id": "publisher", "label": "Publishing"},
    {"id": "analytics", "label": "Analytics"},
]

WORKFLOW_AGENT_IDS: tuple[str, ...] = tuple(s["id"] for s in WORKFLOW_AGENTS)


def stage_progress(step_id: str) -> int:
    if step_id not in WORKFLOW_AGENT_IDS:
        return 0
    idx = WORKFLOW_AGENT_IDS.index(step_id)
    return int(((idx + 1) / len(WORKFLOW_AGENT_IDS)) * 100)
