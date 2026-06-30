"""Demo highlight detection from long-form video metadata."""

from __future__ import annotations

import hashlib
import re


def detect_highlights(topic: str, source_url: str, count: int = 3) -> list[dict]:
    seed = hashlib.md5(f"{source_url}:{topic}".encode()).hexdigest()
    base = int(seed[:8], 16)
    words = re.findall(r"\w+", topic) or ["untold", "moment", "legacy"]
    highlights: list[dict] = []
    for i in range(count):
        start = (base % 120) + i * 45
        duration = 28 + (i * 2)
        label_word = words[i % len(words)].title()
        highlights.append({
            "id": i + 1,
            "label": f"Highlight — {label_word}",
            "start_seconds": start,
            "end_seconds": start + duration,
            "score": round(0.72 + (i * 0.08), 2),
            "reason": "Peak engagement signal (demo detector)",
        })
    return highlights
