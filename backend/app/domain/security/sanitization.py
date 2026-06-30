"""Input validation and safe output helpers."""

from __future__ import annotations

import html
import re

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_SCRIPT_TAG = re.compile(r"<\s*script\b", re.I)


def sanitize_text(value: str | None, *, max_length: int = 50_000, field: str = "value") -> str:
    """Strip control characters and enforce length limits on user text."""
    text = (value or "").strip()
    text = _CONTROL_CHARS.sub("", text)
    if len(text) > max_length:
        raise ValueError(f"{field} exceeds {max_length} characters")
    return text


def escape_html_output(value: str | None) -> str:
    """Escape HTML for API responses rendered in the browser."""
    return html.escape(value or "", quote=True)


def reject_script_markup(value: str | None, *, field: str = "value") -> str:
    """Reject obvious script injection in prompts and rich text."""
    text = sanitize_text(value, field=field)
    if _SCRIPT_TAG.search(text):
        raise ValueError(f"{field} contains disallowed markup")
    return text
