"""AI Agent Marketplace service — install, enable, configure, version."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.domain.agents.marketplace_catalog import DEFAULT_GRANTED_PERMISSIONS, MARKETPLACE_AGENTS
from app.models import User
from app.models.studio_platform import (
    AgentInstallation,
    AgentInstallationHistory,
    MarketplaceAgent,
    MarketplaceAgentVersion,
)
from app.schemas.agent_marketplace import AgentConfigUpdate, AgentInstallRequest, AgentPermissionsUpdate
from app.services.studio_platform_service import StudioPlatformService


class AgentMarketplaceService:
    @staticmethod
    def ensure_catalog(db: Session) -> None:
        if db.query(MarketplaceAgent).filter(MarketplaceAgent.is_system.is_(True)).count():
            return
        for entry in MARKETPLACE_AGENTS:
            agent = MarketplaceAgent(
                slug=entry["slug"],
                name=entry["name"],
                description=entry["description"],
                icon=entry["icon"],
                category=entry["category"],
                studio_route=entry.get("studio_route"),
                is_system=True,
                status="published",
                default_config=entry["default_config"],
                available_permissions=entry["available_permissions"],
            )
            db.add(agent)
            db.flush()
            version = MarketplaceAgentVersion(
                agent_id=agent.id,
                version=1,
                default_config=entry["default_config"],
                config_schema=entry.get("config_schema") or {},
                changelog="Initial release",
                release_notes=f"{entry['name']} v1 — production-ready agent for UNTOLD Studio.",
            )
            db.add(version)
            db.flush()
            agent.current_version_id = version.id
        db.commit()

    @staticmethod
    def _version_dict(v: MarketplaceAgentVersion) -> dict:
        return {
            "id": v.id,
            "agent_id": v.agent_id,
            "version": v.version,
            "default_config": v.default_config or {},
            "config_schema": v.config_schema or {},
            "changelog": v.changelog,
            "release_notes": v.release_notes,
            "created_at": v.created_at,
        }

    @staticmethod
    def _installation_dict(db: Session, inst: AgentInstallation) -> dict:
        agent = inst.agent or db.query(MarketplaceAgent).filter(MarketplaceAgent.id == inst.agent_id).first()
        installed_ver = inst.installed_version or (
            db.query(MarketplaceAgentVersion).filter(MarketplaceAgentVersion.id == inst.installed_version_id).first()
        )
        latest_ver = (
            db.query(func.max(MarketplaceAgentVersion.version))
            .filter(MarketplaceAgentVersion.agent_id == inst.agent_id)
            .scalar()
            or 1
        )
        installed_version_num = installed_ver.version if installed_ver else 1
        return {
            "id": inst.id,
            "user_id": inst.user_id,
            "agent_id": inst.agent_id,
            "agent_slug": agent.slug if agent else "",
            "agent_name": agent.name if agent else "",
            "agent_icon": agent.icon if agent else "🤖",
            "installed_version_id": inst.installed_version_id,
            "installed_version": installed_version_num,
            "latest_version": latest_ver,
            "enabled": inst.enabled,
            "config": inst.config or {},
            "granted_permissions": inst.granted_permissions or [],
            "available_permissions": agent.available_permissions if agent else [],
            "status": inst.status,
            "update_available": installed_version_num < latest_ver,
            "studio_route": agent.studio_route if agent else None,
            "installed_at": inst.installed_at,
            "updated_at": inst.updated_at,
            "last_enabled_at": inst.last_enabled_at,
        }

    @staticmethod
    def _agent_dict(db: Session, agent: MarketplaceAgent, user_id: int | None) -> dict:
        current = None
        if agent.current_version_id:
            ver = db.query(MarketplaceAgentVersion).filter(MarketplaceAgentVersion.id == agent.current_version_id).first()
            if ver:
                current = AgentMarketplaceService._version_dict(ver)

        installation = None
        if user_id:
            installation = (
                db.query(AgentInstallation)
                .filter(AgentInstallation.user_id == user_id, AgentInstallation.agent_id == agent.id)
                .first()
            )

        installed_version_num = None
        latest_version_num = current["version"] if current else 1
        if installation:
            ver = db.query(MarketplaceAgentVersion).filter(
                MarketplaceAgentVersion.id == installation.installed_version_id
            ).first()
            installed_version_num = ver.version if ver else 1

        return {
            "id": agent.id,
            "slug": agent.slug,
            "name": agent.name,
            "description": agent.description,
            "icon": agent.icon,
            "category": agent.category,
            "studio_route": agent.studio_route,
            "is_system": agent.is_system,
            "status": agent.status,
            "current_version_id": agent.current_version_id,
            "default_config": agent.default_config or {},
            "available_permissions": agent.available_permissions or [],
            "current_version": current,
            "installed": installation is not None,
            "installation_id": installation.id if installation else None,
            "enabled": installation.enabled if installation else None,
            "update_available": bool(
                installation and installed_version_num is not None and installed_version_num < latest_version_num
            ),
        }

    @staticmethod
    def _log_history(
        db: Session,
        installation: AgentInstallation,
        *,
        action: str,
        user_id: int,
        from_version: int | None = None,
        to_version: int | None = None,
        notes: str | None = None,
    ) -> None:
        db.add(
            AgentInstallationHistory(
                installation_id=installation.id,
                action=action,
                from_version=from_version,
                to_version=to_version,
                config_snapshot=dict(installation.config or {}),
                notes=notes,
                performed_by_id=user_id,
            )
        )

    @staticmethod
    def _validate_permissions(agent: MarketplaceAgent, granted: list[str]) -> None:
        available = set(agent.available_permissions or [])
        invalid = [p for p in granted if p not in available]
        if invalid:
            raise BadRequestError(f"Invalid permissions: {', '.join(invalid)}")

    @staticmethod
    def _get_agent_by_slug(db: Session, slug: str) -> MarketplaceAgent:
        agent = db.query(MarketplaceAgent).filter(MarketplaceAgent.slug == slug).first()
        if not agent:
            raise NotFoundError("Marketplace agent")
        return agent

    @staticmethod
    def _get_installation(db: Session, installation_id: int, user_id: int) -> AgentInstallation:
        inst = (
            db.query(AgentInstallation)
            .options(joinedload(AgentInstallation.agent), joinedload(AgentInstallation.installed_version))
            .filter(AgentInstallation.id == installation_id, AgentInstallation.user_id == user_id)
            .first()
        )
        if not inst:
            raise NotFoundError("Agent installation")
        return inst

    @staticmethod
    def overview(db: Session, user: User) -> dict:
        StudioPlatformService.require_permission(db, user, None, "studio.access")
        AgentMarketplaceService.ensure_catalog(db)

        agents = db.query(MarketplaceAgent).filter(MarketplaceAgent.status == "published").order_by(MarketplaceAgent.name).all()
        installations = (
            db.query(AgentInstallation)
            .options(joinedload(AgentInstallation.agent))
            .filter(AgentInstallation.user_id == user.id)
            .all()
        )
        inst_dicts = [AgentMarketplaceService._installation_dict(db, i) for i in installations]
        return {
            "total_agents": len(agents),
            "installed_count": len(installations),
            "enabled_count": sum(1 for i in installations if i.enabled),
            "updates_available": sum(1 for d in inst_dicts if d["update_available"]),
            "agents": [AgentMarketplaceService._agent_dict(db, a, user.id) for a in agents],
            "installations": inst_dicts,
        }

    @staticmethod
    def list_agents(db: Session, user: User, *, category: str | None = None) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "studio.access")
        AgentMarketplaceService.ensure_catalog(db)
        q = db.query(MarketplaceAgent).filter(MarketplaceAgent.status == "published")
        if category:
            q = q.filter(MarketplaceAgent.category == category)
        return [AgentMarketplaceService._agent_dict(db, a, user.id) for a in q.order_by(MarketplaceAgent.name).all()]

    @staticmethod
    def get_agent(db: Session, user: User, slug: str) -> dict:
        StudioPlatformService.require_permission(db, user, None, "studio.access")
        AgentMarketplaceService.ensure_catalog(db)
        agent = AgentMarketplaceService._get_agent_by_slug(db, slug)
        result = AgentMarketplaceService._agent_dict(db, agent, user.id)
        versions = (
            db.query(MarketplaceAgentVersion)
            .filter(MarketplaceAgentVersion.agent_id == agent.id)
            .order_by(MarketplaceAgentVersion.version.desc())
            .all()
        )
        result["versions"] = [AgentMarketplaceService._version_dict(v) for v in versions]
        return result

    @staticmethod
    def list_installed(db: Session, user: User) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "studio.access")
        rows = (
            db.query(AgentInstallation)
            .options(joinedload(AgentInstallation.agent), joinedload(AgentInstallation.installed_version))
            .filter(AgentInstallation.user_id == user.id)
            .order_by(AgentInstallation.updated_at.desc())
            .all()
        )
        return [AgentMarketplaceService._installation_dict(db, r) for r in rows]

    @staticmethod
    def install(db: Session, user: User, slug: str, data: AgentInstallRequest) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        AgentMarketplaceService.ensure_catalog(db)
        agent = AgentMarketplaceService._get_agent_by_slug(db, slug)

        existing = (
            db.query(AgentInstallation)
            .filter(AgentInstallation.user_id == user.id, AgentInstallation.agent_id == agent.id)
            .first()
        )
        if existing:
            raise ConflictError("Agent already installed")

        version = (
            db.query(MarketplaceAgentVersion)
            .filter(MarketplaceAgentVersion.id == agent.current_version_id)
            .first()
        )
        if not version:
            raise BadRequestError("Agent has no published version")

        granted = data.granted_permissions or DEFAULT_GRANTED_PERMISSIONS.get(slug, ["ai.generate"])
        AgentMarketplaceService._validate_permissions(agent, granted)
        config = {**(version.default_config or {}), **(data.config or {})}

        inst = AgentInstallation(
            user_id=user.id,
            agent_id=agent.id,
            installed_version_id=version.id,
            enabled=True,
            config=config,
            granted_permissions=granted,
            status="active",
            last_enabled_at=datetime.now(timezone.utc),
        )
        db.add(inst)
        db.flush()
        AgentMarketplaceService._log_history(
            db, inst, action="install", user_id=user.id, to_version=version.version, notes=f"Installed {agent.name}"
        )
        StudioPlatformService.log_activity(db, user.id, "agent.installed", None, "marketplace", agent.id)
        db.commit()
        db.refresh(inst)
        return AgentMarketplaceService._installation_dict(db, inst)

    @staticmethod
    def enable(db: Session, user: User, installation_id: int) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        inst = AgentMarketplaceService._get_installation(db, installation_id, user.id)
        if inst.enabled:
            raise ConflictError("Agent is already enabled")
        inst.enabled = True
        inst.status = "active"
        inst.last_enabled_at = datetime.now(timezone.utc)
        AgentMarketplaceService._log_history(db, inst, action="enable", user_id=user.id)
        db.commit()
        return AgentMarketplaceService._installation_dict(db, inst)

    @staticmethod
    def disable(db: Session, user: User, installation_id: int) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        inst = AgentMarketplaceService._get_installation(db, installation_id, user.id)
        if not inst.enabled:
            raise ConflictError("Agent is already disabled")
        inst.enabled = False
        inst.status = "disabled"
        AgentMarketplaceService._log_history(db, inst, action="disable", user_id=user.id)
        db.commit()
        return AgentMarketplaceService._installation_dict(db, inst)

    @staticmethod
    def update_config(db: Session, user: User, installation_id: int, data: AgentConfigUpdate) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        inst = AgentMarketplaceService._get_installation(db, installation_id, user.id)
        inst.config = {**(inst.config or {}), **data.config}
        inst.updated_at = datetime.now(timezone.utc)
        AgentMarketplaceService._log_history(db, inst, action="configure", user_id=user.id, notes="Configuration updated")
        db.commit()
        return AgentMarketplaceService._installation_dict(db, inst)

    @staticmethod
    def update_permissions(db: Session, user: User, installation_id: int, data: AgentPermissionsUpdate) -> dict:
        StudioPlatformService.require_permission(db, user, None, "settings.manage")
        inst = AgentMarketplaceService._get_installation(db, installation_id, user.id)
        agent = inst.agent or db.query(MarketplaceAgent).filter(MarketplaceAgent.id == inst.agent_id).first()
        AgentMarketplaceService._validate_permissions(agent, data.granted_permissions)
        inst.granted_permissions = data.granted_permissions
        inst.updated_at = datetime.now(timezone.utc)
        AgentMarketplaceService._log_history(db, inst, action="permission_change", user_id=user.id)
        db.commit()
        return AgentMarketplaceService._installation_dict(db, inst)

    @staticmethod
    def update_version(db: Session, user: User, installation_id: int) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        inst = AgentMarketplaceService._get_installation(db, installation_id, user.id)
        agent = inst.agent or db.query(MarketplaceAgent).filter(MarketplaceAgent.id == inst.agent_id).first()
        latest = (
            db.query(MarketplaceAgentVersion)
            .filter(MarketplaceAgentVersion.id == agent.current_version_id)
            .first()
        )
        if not latest:
            raise BadRequestError("No latest version available")

        old_ver = (
            db.query(MarketplaceAgentVersion)
            .filter(MarketplaceAgentVersion.id == inst.installed_version_id)
            .first()
        )
        from_v = old_ver.version if old_ver else None
        if from_v == latest.version:
            raise ConflictError("Already on latest version")

        inst.installed_version_id = latest.id
        inst.config = {**(latest.default_config or {}), **(inst.config or {})}
        inst.status = "active"
        inst.updated_at = datetime.now(timezone.utc)
        AgentMarketplaceService._log_history(
            db,
            inst,
            action="update",
            user_id=user.id,
            from_version=from_v,
            to_version=latest.version,
            notes=latest.changelog,
        )
        db.commit()
        return AgentMarketplaceService._installation_dict(db, inst)

    @staticmethod
    def uninstall(db: Session, user: User, installation_id: int) -> None:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        inst = AgentMarketplaceService._get_installation(db, installation_id, user.id)
        db.delete(inst)
        db.commit()

    @staticmethod
    def history(db: Session, user: User, installation_id: int) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "studio.access")
        inst = AgentMarketplaceService._get_installation(db, installation_id, user.id)
        rows = (
            db.query(AgentInstallationHistory)
            .filter(AgentInstallationHistory.installation_id == inst.id)
            .order_by(AgentInstallationHistory.created_at.desc())
            .all()
        )
        return [
            {
                "id": r.id,
                "action": r.action,
                "from_version": r.from_version,
                "to_version": r.to_version,
                "notes": r.notes,
                "created_at": r.created_at,
            }
            for r in rows
        ]

    @staticmethod
    def is_agent_enabled(db: Session, user_id: int, slug: str) -> bool:
        """Check if user has an enabled installation for the given agent slug."""
        agent = db.query(MarketplaceAgent).filter(MarketplaceAgent.slug == slug).first()
        if not agent:
            return True
        inst = (
            db.query(AgentInstallation)
            .filter(AgentInstallation.user_id == user_id, AgentInstallation.agent_id == agent.id)
            .first()
        )
        if not inst:
            return False
        return bool(inst.enabled)

    @staticmethod
    def publish_agent_version(db: Session, user: User, slug: str, *, changelog: str, release_notes: str | None = None) -> dict:
        """Admin: publish a new catalog version for a system agent."""
        StudioPlatformService.require_permission(db, user, None, "admin.manage")
        agent = AgentMarketplaceService._get_agent_by_slug(db, slug)
        max_v = (
            db.query(func.max(MarketplaceAgentVersion.version))
            .filter(MarketplaceAgentVersion.agent_id == agent.id)
            .scalar()
            or 0
        )
        current = (
            db.query(MarketplaceAgentVersion)
            .filter(MarketplaceAgentVersion.id == agent.current_version_id)
            .first()
        )
        version = MarketplaceAgentVersion(
            agent_id=agent.id,
            version=max_v + 1,
            default_config=current.default_config if current else agent.default_config,
            config_schema=current.config_schema if current else {},
            changelog=changelog,
            release_notes=release_notes,
        )
        db.add(version)
        db.flush()
        agent.current_version_id = version.id
        agent.updated_at = datetime.now(timezone.utc)

        installations = db.query(AgentInstallation).filter(AgentInstallation.agent_id == agent.id).all()
        for inst in installations:
            old = db.query(MarketplaceAgentVersion).filter(MarketplaceAgentVersion.id == inst.installed_version_id).first()
            if old and old.version < version.version:
                inst.status = "update_available"

        db.commit()
        return AgentMarketplaceService._version_dict(version)
