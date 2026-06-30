"""Content safety — block copyrighted / protected character generation requests."""

from __future__ import annotations

import re

# Non-exhaustive guardrail list — rejects obvious protected-IP requests.
_BLOCKED_PATTERNS = [
    r"\bscreenshot\s+from\b",
    r"\bmovie\s+frame\b",
    r"\bfilm\s+still\b",
    r"\bexact\s+replica\b",
    r"\bdisney\b",
    r"\bmarvel\b",
    r"\bdc\s+comics\b",
    r"\bstar\s+wars\b",
    r"\bharry\s+potter\b",
    r"\bmickey\s+mouse\b",
    r"\bminions\b",
    r"\bpixar\b",
    r"\bstudio\s+ghibli\b",
    r"\bspider[\s-]?man\b",
    r"\bbatman\b",
    r"\bsuperman\b",
    r"\biron\s+man\b",
    r"\bcaptain\s+america\b",
    r"\bwonder\s+woman\b",
    r"\bforbidden\s+character\b",
]


def validate_image_prompt(prompt: str) -> str | None:
    """Return error message if prompt violates policy, else None."""
    text = (prompt or "").lower()
    for pattern in _BLOCKED_PATTERNS:
        if re.search(pattern, text, re.I):
            return (
                "Prompt rejected: UNTOLD Image Studio does not generate copyrighted movie frames, "
                "studio character replicas, or protected IP. Use original sports/documentary concepts."
            )
    return None
