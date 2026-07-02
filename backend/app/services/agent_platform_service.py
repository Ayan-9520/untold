"""Enterprise agent platform — registry, SDK docs, third-party registration."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ConflictError
from app.domain.agents.marketplace_catalog import MARKETPLACE_AGENTS
from app.domain.agents.registry import AGENT_PERMISSIONS, BACKEND_AGENT_REGISTRY, register_agent_class
from app.models import User
from app.models.studio_platform import MarketplaceAgent, MarketplaceAgentVersion
from app.services.agent_marketplace_service import AgentMarketplaceService
from app.services.studio_platform_service import StudioPlatformService


class AgentPlatformService:
    @staticmethod
    def registry(db: Session, user: User) -> dict:
        StudioPlatformService.require_permission(db, user, None, "studio.access")
        AgentMarketplaceService.ensure_catalog(db)
        agents = db.query(MarketplaceAgent).filter(MarketplaceAgent.status == "published").all()
        return {
            "catalog_agents": len(agents),
            "system_agents": len(MARKETPLACE_AGENTS),
            "registered_handlers": list(BACKEND_AGENT_REGISTRY.keys()),
            "permissions": AGENT_PERMISSIONS,
            "agents": [
                {
                    "slug": a.slug,
                    "name": a.name,
                    "category": a.category,
                    "has_handler": a.slug in BACKEND_AGENT_REGISTRY,
                }
                for a in agents
            ],
        }

    @staticmethod
    def sdk_docs() -> dict:
        return {
            "title": "UNTOLD Agent SDK",
            "version": "1.0",
            "backend": {
                "base_class": "app.agents.sdk.base.BaseAgent",
                "context": "AgentContext",
                "methods": ["on_install", "on_enable", "on_disable", "on_run", "on_message"],
                "register": "POST /api/v1/studio/platform/agent-platform/register",
            },
            "frontend": {
                "package": "@untold/agent-sdk",
                "entry": "src/agent-sdk/index.js",
                "hooks": ["useAgentRuntime", "useAgentMemory"],
            },
            "permissions": AGENT_PERMISSIONS,
            "events": ["agent.run.started", "agent.run.completed", "agent.message.received"],
        }

    @staticmethod
    def register_agent(
        db: Session,
        user: User,
        *,
        slug: str,
        name: str,
        description: str,
        category: str = "custom",
        config_schema: dict | None = None,
        available_permissions: list[str] | None = None,
    ) -> dict:
        StudioPlatformService.require_permission(db, user, None, "admin.manage")
        if db.query(MarketplaceAgent).filter(MarketplaceAgent.slug == slug).first():
            raise ConflictError(f"Agent slug '{slug}' already exists")
        perms = available_permissions or ["ai.generate", "memory.read", "memory.write"]
        agent = MarketplaceAgent(
            slug=slug,
            name=name.strip(),
            description=description.strip(),
            icon="🤖",
            category=category,
            is_system=False,
            status="published",
            default_config={},
            available_permissions=perms,
        )
        db.add(agent)
        db.flush()
        version = MarketplaceAgentVersion(
            agent_id=agent.id,
            version=1,
            default_config={},
            config_schema=config_schema or {},
            changelog="Initial registration",
            release_notes=description[:500],
        )
        db.add(version)
        db.flush()
        agent.current_version_id = version.id
        db.commit()
        return {"slug": agent.slug, "id": agent.id, "version": 1}

    @staticmethod
    def register_handler_class(agent_cls: type) -> None:
        if not getattr(agent_cls, "slug", None):
            raise BadRequestError("Agent class must define slug")
        register_agent_class(agent_cls)
