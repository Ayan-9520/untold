"""Agent SDK — base classes for backend agent authors."""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session


@dataclass
class AgentContext:
    """Runtime context for agent execution."""

    db: Session
    user_id: int
    installation_id: int
    agent_slug: str
    organization_id: int | None = None
    project_id: int | None = None
    config: dict[str, Any] = field(default_factory=dict)
    granted_permissions: list[str] = field(default_factory=list)

    def has_permission(self, permission: str) -> bool:
        return permission in self.granted_permissions

    def get_config(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)


class BaseAgent(ABC):
    """Base class for registered backend agents."""

    slug: str = ""

    def on_install(self, ctx: AgentContext) -> None:
        """Called when agent is installed."""

    def on_enable(self, ctx: AgentContext) -> None:
        """Called when agent is enabled."""

    def on_disable(self, ctx: AgentContext) -> None:
        """Called when agent is disabled."""

    def on_run(self, ctx: AgentContext, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute agent task. Override for custom registered agents."""
        return {"status": "ok"}

    def on_message(self, ctx: AgentContext, message: dict[str, Any]) -> dict[str, Any] | None:
        """Handle inter-agent message."""
        return None
