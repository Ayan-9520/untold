"""Agent memory — persistent key-value and context per installation."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import User
from app.models.studio_platform import AgentMemoryEntry
from app.services.agent_runtime_service import AgentRuntimeService
from app.services.studio_platform_service import StudioPlatformService


class AgentMemoryService:
    @staticmethod
    def list_memory(
        db: Session,
        user: User,
        installation_id: int,
        *,
        project_id: int | None = None,
        prefix: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        ctx = AgentRuntimeService.build_context(
            db, user.id, AgentMemoryService._slug_for_installation(db, installation_id, user.id)
        )
        AgentRuntimeService.require_permission(ctx, "memory.read")
        q = db.query(AgentMemoryEntry).filter(AgentMemoryEntry.installation_id == installation_id)
        if project_id is not None:
            q = q.filter(AgentMemoryEntry.project_id == project_id)
        if prefix:
            q = q.filter(AgentMemoryEntry.memory_key.startswith(prefix))
        now = datetime.now(timezone.utc)
        rows = q.order_by(AgentMemoryEntry.updated_at.desc()).limit(limit).all()
        return [
            {
                "id": r.id,
                "memory_key": r.memory_key,
                "content": r.content,
                "project_id": r.project_id,
                "meta": r.meta or {},
                "expires_at": r.expires_at,
                "updated_at": r.updated_at,
            }
            for r in rows
            if not r.expires_at or r.expires_at > now
        ]

    @staticmethod
    def upsert_memory(
        db: Session,
        user: User,
        installation_id: int,
        *,
        memory_key: str,
        content: str,
        project_id: int | None = None,
        meta: dict | None = None,
        expires_at: datetime | None = None,
    ) -> dict:
        slug = AgentMemoryService._slug_for_installation(db, installation_id, user.id)
        ctx = AgentRuntimeService.build_context(db, user.id, slug, project_id=project_id)
        AgentRuntimeService.require_permission(ctx, "memory.write")
        row = (
            db.query(AgentMemoryEntry)
            .filter(
                AgentMemoryEntry.installation_id == installation_id,
                AgentMemoryEntry.memory_key == memory_key,
                AgentMemoryEntry.project_id == project_id,
            )
            .first()
        )
        if row:
            row.content = content
            row.meta = {**(row.meta or {}), **(meta or {})}
            row.expires_at = expires_at
        else:
            row = AgentMemoryEntry(
                installation_id=installation_id,
                project_id=project_id,
                memory_key=memory_key,
                content=content,
                meta=meta or {},
                expires_at=expires_at,
            )
            db.add(row)
        db.commit()
        db.refresh(row)
        return {"id": row.id, "memory_key": row.memory_key, "content": row.content}

    @staticmethod
    def delete_memory(db: Session, user: User, installation_id: int, memory_id: int) -> None:
        slug = AgentMemoryService._slug_for_installation(db, installation_id, user.id)
        ctx = AgentRuntimeService.build_context(db, user.id, slug)
        AgentRuntimeService.require_permission(ctx, "memory.write")
        row = (
            db.query(AgentMemoryEntry)
            .filter(AgentMemoryEntry.id == memory_id, AgentMemoryEntry.installation_id == installation_id)
            .first()
        )
        if not row:
            raise NotFoundError("Memory entry")
        db.delete(row)
        db.commit()

    @staticmethod
    def recall(db: Session, installation_id: int, memory_key: str, project_id: int | None = None) -> str | None:
        """Internal recall for agent runtime (no user auth)."""
        row = (
            db.query(AgentMemoryEntry)
            .filter(
                AgentMemoryEntry.installation_id == installation_id,
                AgentMemoryEntry.memory_key == memory_key,
                AgentMemoryEntry.project_id == project_id,
            )
            .first()
        )
        if not row:
            return None
        if row.expires_at and row.expires_at <= datetime.now(timezone.utc):
            return None
        return row.content

    @staticmethod
    def _slug_for_installation(db: Session, installation_id: int, user_id: int) -> str:
        from app.models.studio_platform import AgentInstallation, MarketplaceAgent

        inst = (
            db.query(AgentInstallation)
            .filter(AgentInstallation.id == installation_id, AgentInstallation.user_id == user_id)
            .first()
        )
        if not inst:
            raise NotFoundError("Installation")
        agent = db.query(MarketplaceAgent).filter(MarketplaceAgent.id == inst.agent_id).first()
        if not agent:
            raise NotFoundError("Agent")
        return agent.slug
