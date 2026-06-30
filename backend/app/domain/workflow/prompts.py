"""Workflow Engine — default prompt templates and rendering."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.workflow.context import WorkflowContext

WORKFLOW_PROMPT_KEYS: tuple[str, ...] = (
    "research",
    "script",
    "thumbnail",
    "seo",
    "translation",
    "voice",
)

WORKFLOW_PROMPT_LABELS: dict[str, str] = {
    "research": "Research Prompt",
    "script": "Script Prompt",
    "thumbnail": "Thumbnail Prompt",
    "seo": "SEO Prompt",
    "translation": "Translation Prompt",
    "voice": "Voice Prompt",
}

WORKFLOW_PROMPT_PLACEHOLDERS: dict[str, list[str]] = {
    "research": ["{topic}"],
    "script": ["{topic}", "{research}"],
    "thumbnail": ["{topic}", "{excerpt}"],
    "seo": ["{topic}", "{excerpt}"],
    "translation": ["{language}", "{excerpt}"],
    "voice": ["{excerpt}"],
}

DEFAULT_WORKFLOW_PROMPTS: dict[str, str] = {
    "research": (
        "Create a documentary research brief for: {topic}\n\n"
        "Include timeline, key figures, controversies, verified statistics, "
        "and five primary sources to verify."
    ),
    "script": (
        "Write a full documentary narration script for: {topic}\n\n"
        "Use this research brief:\n{research}\n\n"
        "Structure: opening hook, three acts, closing reflection. Cinematic tone."
    ),
    "thumbnail": (
        "Cinematic documentary poster for {topic}. "
        "Key beat: {excerpt}. Original composition, dramatic lighting, "
        "YouTube-thumbnail readable contrast."
    ),
    "seo": (
        "Generate SEO metadata for documentary: {topic}\n\n"
        "Include YouTube titles (max 60 chars), meta title, description, tags, and hashtags.\n"
        "Script context:\n{excerpt}"
    ),
    "translation": "Translate to {language}:\n\n{excerpt}",
    "voice": (
        "Narrate the following documentary script with cinematic documentary tone:\n\n{excerpt}"
    ),
}


class _SafeFormatDict(dict):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def merge_prompts(overrides: dict[str, str] | None) -> dict[str, str]:
    merged = dict(DEFAULT_WORKFLOW_PROMPTS)
    if overrides:
        for key, value in overrides.items():
            if key in merged and value and str(value).strip():
                merged[key] = str(value).strip()
    return merged


def prompt_catalog() -> list[dict]:
    return [
        {
            "key": key,
            "label": WORKFLOW_PROMPT_LABELS[key],
            "template": DEFAULT_WORKFLOW_PROMPTS[key],
            "placeholders": WORKFLOW_PROMPT_PLACEHOLDERS[key],
        }
        for key in WORKFLOW_PROMPT_KEYS
    ]


def render_workflow_prompt(
    key: str,
    prompts: dict[str, str],
    ctx: WorkflowContext,
    **extra: str,
) -> str:
    template = prompts.get(key) or DEFAULT_WORKFLOW_PROMPTS[key]
    values = {
        "topic": ctx.topic,
        "research": (ctx.research_text or "")[:6000],
        "script": (ctx.script_text or "")[:6000],
        "excerpt": ctx.script_excerpt(1200),
        "language": extra.get("language") or ctx.translation_language or "es",
    }
    values.update(extra)
    try:
        return template.format_map(_SafeFormatDict(values))
    except (ValueError, KeyError):
        return template
