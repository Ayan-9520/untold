"""Collaboration helpers — mentions, etag, room keys."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

MENTION_PATTERN = re.compile(r"@\[(\d+)\]")

PRESENCE_COLORS = ("#d4af37", "#60a5fa", "#34d399", "#f472b6", "#a78bfa", "#fb923c", "#38bdf8")


def parse_mentions(content: str) -> list[int]:
    return [int(m) for m in MENTION_PATTERN.findall(content or "")]


def compute_etag(content: dict[str, Any], version: int) -> str:
    raw = json.dumps({"v": version, "c": content}, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def room_key(project_id: int, resource_type: str = "project", resource_id: int | None = None) -> str:
    rid = resource_id if resource_id is not None else 0
    return f"project:{project_id}:{resource_type}:{rid}"


def presence_color(user_id: int) -> str:
    return PRESENCE_COLORS[user_id % len(PRESENCE_COLORS)]
