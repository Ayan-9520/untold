"""Workflow condition evaluation — field checks and simple expressions."""

from __future__ import annotations

import re

from app.domain.workflow.context import WorkflowContext

_FIELD_MAP_KEYS = (
    "research",
    "script",
    "storyboard",
    "image",
    "video",
    "voice",
    "music",
    "seo",
    "translation",
    "publish",
)


def _field_value(ctx: WorkflowContext, field: str) -> bool:
    field = field.strip().lower()
    mapping = {
        "research": bool(ctx.research_text),
        "script": bool(ctx.script_text),
        "storyboard": bool(ctx.storyboard_scenes),
        "image": bool(ctx.image_url),
        "video": bool(ctx.video_url),
        "voice": bool(ctx.voice_url),
        "music": bool(ctx.music_url),
        "seo": bool(ctx.seo_variants),
        "translation": bool(ctx.translation_text),
        "publish": bool(ctx.publish_run_id),
    }
    return mapping.get(field, False)


def evaluate_condition(expression: str | None, ctx: WorkflowContext) -> bool:
    """Evaluate workflow condition expressions.

    Supported forms:
    - field name: ``research``, ``script``, ``video``, …
    - negation: ``!research``, ``not script``
    - equality: ``topic=foo`` (substring match on topic)
    - boolean literals: ``true``, ``false``
    - compound: ``research && script``, ``image || video``
    """
    if not expression or not expression.strip():
        return True

    expr = expression.strip().lower()

    if expr in ("true", "1", "yes"):
        return True
    if expr in ("false", "0", "no"):
        return False

    if expr.startswith("!") or expr.startswith("not "):
        inner = expr.lstrip("!").removeprefix("not ").strip()
        return not evaluate_condition(inner, ctx)

    if "&&" in expr:
        return all(evaluate_condition(part.strip(), ctx) for part in expr.split("&&"))
    if "||" in expr:
        return any(evaluate_condition(part.strip(), ctx) for part in expr.split("||"))

    eq_match = re.match(r"^topic\s*=\s*(.+)$", expr)
    if eq_match:
        needle = eq_match.group(1).strip().strip("'\"")
        return needle.lower() in (ctx.topic or "").lower()

    if expr in _FIELD_MAP_KEYS:
        return _field_value(ctx, expr)

    return _field_value(ctx, expr)
