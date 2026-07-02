"""Agent registry — backend agent handlers and permission catalog."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.agents.sdk.base import BaseAgent

# Slug -> BaseAgent subclass (populated by samples and third-party register)
BACKEND_AGENT_REGISTRY: dict[str, type["BaseAgent"]] = {}


def register_agent_class(agent_cls: type["BaseAgent"]) -> type["BaseAgent"]:
    if agent_cls.slug:
        BACKEND_AGENT_REGISTRY[agent_cls.slug] = agent_cls
    return agent_cls


AGENT_PERMISSIONS: dict[str, str] = {
    "ai.generate": "Run AI generations",
    "project.read": "Read project data",
    "project.write": "Modify project data",
    "publish.dispatch": "Dispatch publishing jobs",
    "news.fetch": "Fetch news sources",
    "storage.read": "Read storage assets",
    "storage.write": "Write storage assets",
    "memory.read": "Read agent memory",
    "memory.write": "Write agent memory",
    "communicate.send": "Send messages to other agents",
    "communicate.receive": "Receive agent messages",
    "schedule.manage": "Manage agent schedules",
    "analytics.read": "View agent analytics",
}


def permission_allowed(granted: list[str], required: str) -> bool:
    if required in granted:
        return True
    # Wildcard admin permission on agents
    return "ai.generate" in granted and required.startswith("memory.")


def _load_sample_agents() -> None:
    from app.agents.samples import BACKEND_AGENT_SAMPLE_REGISTRY

    for cls in BACKEND_AGENT_SAMPLE_REGISTRY.values():
        register_agent_class(cls)


_load_sample_agents()
