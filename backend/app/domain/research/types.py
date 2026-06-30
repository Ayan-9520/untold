"""Research AI agent — vendor-neutral request/result types."""

from dataclasses import dataclass, field
from typing import Any


RESEARCH_ACTIONS = (
    "full_research",
    "summary",
    "timeline",
    "statistics",
    "public_facts",
    "follow_up",
    "fact_check",
)


@dataclass
class ResearchAgentRequest:
    action: str
    topic: str
    prompt: str
    context: dict[str, Any] = field(default_factory=dict)
    project_id: int | None = None
    research_id: int | None = None


@dataclass
class ResearchAgentResult:
    summary: str = ""
    suggestions: list[str] = field(default_factory=list)
    follow_up_questions: list[str] = field(default_factory=list)
    statistics: list[dict[str, Any]] = field(default_factory=list)
    public_facts: list[dict[str, Any]] = field(default_factory=list)
    timeline_events: list[dict[str, Any]] = field(default_factory=list)
    fact_check_hints: list[dict[str, Any]] = field(default_factory=list)
    provider: str = "demo"
    meta: dict[str, Any] = field(default_factory=dict)
