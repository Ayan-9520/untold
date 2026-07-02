"""Agent runtime — resolve installations, permissions, execution logging."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.agents.sdk.base import AgentContext
from app.core.exceptions import ForbiddenError, NotFoundError
from app.domain.agents.registry import BACKEND_AGENT_REGISTRY, permission_allowed
from app.models.studio_platform import (
    AgentExecutionLog,
    AgentInstallation,
    AgentMessage,
    MarketplaceAgent,
    MarketplaceAgentVersion,
)


class AgentRuntimeService:
    @staticmethod
    def resolve_installation(db: Session, user_id: int, slug: str) -> tuple[AgentInstallation, MarketplaceAgent]:
        agent = db.query(MarketplaceAgent).filter(MarketplaceAgent.slug == slug).first()
        if not agent:
            raise NotFoundError(f"Agent '{slug}'")
        inst = (
            db.query(AgentInstallation)
            .filter(AgentInstallation.user_id == user_id, AgentInstallation.agent_id == agent.id)
            .first()
        )
        if not inst:
            raise ForbiddenError(f"Agent '{slug}' is not installed")
        return inst, agent

    @staticmethod
    def build_context(
        db: Session,
        user_id: int,
        slug: str,
        *,
        project_id: int | None = None,
        organization_id: int | None = None,
    ) -> AgentContext:
        inst, agent = AgentRuntimeService.resolve_installation(db, user_id, slug)
        if not inst.enabled:
            raise ForbiddenError(f"Agent '{slug}' is disabled")

        version = (
            db.query(MarketplaceAgentVersion)
            .filter(MarketplaceAgentVersion.id == inst.installed_version_id)
            .first()
        )
        merged_config = {**(version.default_config if version else {}), **(inst.config or {})}
        return AgentContext(
            db=db,
            user_id=user_id,
            installation_id=inst.id,
            agent_slug=slug,
            organization_id=organization_id or inst.organization_id,
            project_id=project_id,
            config=merged_config,
            granted_permissions=list(inst.granted_permissions or []),
        )

    @staticmethod
    def require_permission(ctx: AgentContext, permission: str) -> None:
        if not permission_allowed(ctx.granted_permissions, permission):
            raise ForbiddenError(f"Agent missing permission: {permission}")

    @staticmethod
    def require_enabled(db: Session, user_id: int | None, slug: str, *, permission: str = "ai.generate") -> AgentContext | None:
        if not user_id or not slug:
            return None
        agent = db.query(MarketplaceAgent).filter(MarketplaceAgent.slug == slug).first()
        if not agent:
            return None
        inst = (
            db.query(AgentInstallation)
            .filter(AgentInstallation.user_id == user_id, AgentInstallation.agent_id == agent.id)
            .first()
        )
        if not inst or not inst.enabled:
            raise ForbiddenError(f"Agent '{slug}' is not installed or disabled")
        ctx = AgentRuntimeService.build_context(db, user_id, slug)
        AgentRuntimeService.require_permission(ctx, permission)
        return ctx

    @staticmethod
    def merged_provider(ctx: AgentContext, step_key: str, default: str | None = None) -> str | None:
        """Resolve provider from agent config for a workflow step."""
        return ctx.config.get(f"{step_key}_provider") or ctx.config.get("provider") or default

    @staticmethod
    def log_execution(
        db: Session,
        *,
        agent_slug: str,
        installation_id: int | None,
        user_id: int | None,
        organization_id: int | None = None,
        project_id: int | None = None,
        run_id: int | None = None,
        generation_id: int | None = None,
        status: str = "success",
        duration_ms: int | None = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost_usd: float = 0,
        message: str | None = None,
        meta: dict | None = None,
    ) -> AgentExecutionLog:
        row = AgentExecutionLog(
            installation_id=installation_id,
            agent_slug=agent_slug,
            user_id=user_id,
            organization_id=organization_id,
            project_id=project_id,
            run_id=run_id,
            generation_id=generation_id,
            status=status,
            duration_ms=duration_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            message=message,
            meta=meta or {},
        )
        db.add(row)
        db.flush()
        return row

    @staticmethod
    def run_registered_agent(ctx: AgentContext, payload: dict[str, Any]) -> dict[str, Any]:
        handler_cls = BACKEND_AGENT_REGISTRY.get(ctx.agent_slug)
        if not handler_cls:
            return {"status": "skipped", "reason": "no registered handler"}
        handler = handler_cls()
        return handler.on_run(ctx, payload) or {}

    @staticmethod
    def send_message(
        db: Session,
        ctx: AgentContext,
        to_slug: str,
        payload: dict[str, Any],
        *,
        message_type: str = "task",
    ) -> AgentMessage:
        AgentRuntimeService.require_permission(ctx, "communicate.send")
        to_agent = db.query(MarketplaceAgent).filter(MarketplaceAgent.slug == to_slug).first()
        if not to_agent:
            raise NotFoundError(f"Target agent '{to_slug}'")
        to_inst = (
            db.query(AgentInstallation)
            .filter(AgentInstallation.user_id == ctx.user_id, AgentInstallation.agent_id == to_agent.id)
            .first()
        )
        msg = AgentMessage(
            from_installation_id=ctx.installation_id,
            to_installation_id=to_inst.id if to_inst else None,
            from_slug=ctx.agent_slug,
            to_slug=to_slug,
            message_type=message_type,
            payload=payload,
            status="pending",
        )
        db.add(msg)
        db.flush()
        return msg

    @staticmethod
    def list_messages(db: Session, installation_id: int, *, status: str | None = None, limit: int = 50) -> list[dict]:
        q = db.query(AgentMessage).filter(AgentMessage.to_installation_id == installation_id)
        if status:
            q = q.filter(AgentMessage.status == status)
        rows = q.order_by(AgentMessage.created_at.desc()).limit(limit).all()
        return [
            {
                "id": r.id,
                "from_slug": r.from_slug,
                "to_slug": r.to_slug,
                "message_type": r.message_type,
                "payload": r.payload,
                "status": r.status,
                "created_at": r.created_at,
            }
            for r in rows
        ]

    @staticmethod
    def mark_message_read(db: Session, message_id: int, installation_id: int) -> None:
        msg = (
            db.query(AgentMessage)
            .filter(AgentMessage.id == message_id, AgentMessage.to_installation_id == installation_id)
            .first()
        )
        if msg:
            msg.status = "read"
            msg.read_at = datetime.now(timezone.utc)

    @staticmethod
    def execution_timer():
        return _ExecutionTimer()


class _ExecutionTimer:
    def __init__(self) -> None:
        self._start = time.perf_counter()

    def elapsed_ms(self) -> int:
        return int((time.perf_counter() - self._start) * 1000)
