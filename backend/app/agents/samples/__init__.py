"""Sample backend agents — reference implementations for the Agent SDK."""

from __future__ import annotations

import logging
from typing import Any

from app.agents.sdk.base import AgentContext, BaseAgent

logger = logging.getLogger(__name__)


class PublishingAgentHandler(BaseAgent):
    """Handles scheduled/manual runs for the publishing marketplace agent."""

    slug = "publishing"

    def on_run(self, ctx: AgentContext, payload: dict[str, Any]) -> dict[str, Any]:
        from app.services.agent_memory_service import AgentMemoryService

        platforms = payload.get("platforms") or ctx.get_config("default_platforms") or ["originals"]
        if ctx.has_permission("memory.write") and payload.get("topic"):
            AgentMemoryService.upsert_memory(
                ctx.db,
                _ctx_user(ctx),
                ctx.installation_id,
                memory_key="last_publish_topic",
                content=str(payload["topic"])[:2000],
                project_id=ctx.project_id,
            )
        logger.info("PublishingAgentHandler run platforms=%s installation=%s", platforms, ctx.installation_id)
        return {"status": "ok", "platforms": platforms, "simulated": True}


class ResearchMemoryAgent(BaseAgent):
    """Stores research context in agent memory on manual/scheduled runs."""

    slug = "research"

    def on_run(self, ctx: AgentContext, payload: dict[str, Any]) -> dict[str, Any]:
        from app.services.agent_memory_service import AgentMemoryService

        topic = payload.get("topic") or payload.get("query") or ""
        if topic and ctx.has_permission("memory.write"):
            AgentMemoryService.upsert_memory(
                ctx.db,
                _ctx_user(ctx),
                ctx.installation_id,
                memory_key="last_research_topic",
                content=str(topic)[:2000],
                project_id=ctx.project_id,
            )
        recalled = AgentMemoryService.recall(ctx.db, ctx.installation_id, "last_research_topic", ctx.project_id)
        return {"status": "ok", "topic": topic, "recalled": recalled}


def _ctx_user(ctx: AgentContext):
    from app.models import User

    user = ctx.db.query(User).filter(User.id == ctx.user_id).first()
    if not user:
        raise ValueError("User not found")
    return user


BACKEND_AGENT_SAMPLE_REGISTRY: dict[str, type[BaseAgent]] = {
    "publishing": PublishingAgentHandler,
    "research": ResearchMemoryAgent,
}
