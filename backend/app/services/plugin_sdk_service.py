"""Plugin SDK service — marketplace, lifecycle, event bus API."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.domain.plugins.catalog import DEFAULT_PLUGIN_GRANTED, PLUGIN_CATALOG
from app.domain.plugins.events import STUDIO_EVENTS
from app.domain.plugins.hooks import HOOK_POINTS
from app.domain.plugins.manifest import validate_manifest
from app.domain.plugins.permissions import PLUGIN_PERMISSIONS, validate_permissions
from app.domain.plugins.registry import PluginEventBus
from app.domain.plugins.samples import BACKEND_PLUGIN_REGISTRY
from app.models import User
from app.models.studio_platform import (
    PluginDefinition,
    PluginEventLog,
    PluginInstallation,
    PluginInstallationHistory,
    PluginRating,
    PluginVersion,
)
from app.plugins.sdk import PluginContext
from app.services.studio_platform_service import StudioPlatformService


class PluginSdkService:
    @staticmethod
    def ensure_catalog(db: Session) -> None:
        if db.query(PluginDefinition).filter(PluginDefinition.is_system.is_(True)).count():
            return
        for entry in PLUGIN_CATALOG:
            manifest = validate_manifest(entry["manifest"])
            plugin = PluginDefinition(
                slug=entry["slug"],
                name=entry["name"],
                description=entry["description"],
                icon=entry["icon"],
                category=entry["category"],
                author=entry.get("author", "UNTOLD"),
                author_url=entry.get("author_url"),
                is_system=True,
                status="published",
                manifest=manifest,
                default_settings=entry["default_settings"],
                available_permissions=entry["available_permissions"],
                backend_entry=entry.get("backend_entry"),
                frontend_entry=entry.get("frontend_entry"),
            )
            db.add(plugin)
            db.flush()
            version = PluginVersion(
                plugin_id=plugin.id,
                version=1,
                version_label="1.0.0",
                manifest=manifest,
                settings_schema=manifest.get("settings_schema") or {},
                default_settings=entry["default_settings"],
                changelog="Initial release",
                release_notes=f"{entry['name']} v1 — UNTOLD Plugin SDK sample.",
            )
            db.add(version)
            db.flush()
            plugin.current_version_id = version.id
            plugin.documentation_url = entry.get("author_url") or f"/studio/plugins/docs#{entry['slug']}"
        db.commit()

    @staticmethod
    def _version_dict(v: PluginVersion) -> dict:
        return {
            "id": v.id,
            "plugin_id": v.plugin_id,
            "version": v.version,
            "version_label": getattr(v, "version_label", None) or f"1.{max(v.version - 1, 0)}.0",
            "manifest": v.manifest or {},
            "settings_schema": v.settings_schema or {},
            "default_settings": v.default_settings or {},
            "changelog": v.changelog,
            "release_notes": v.release_notes,
            "created_at": v.created_at,
        }

    @staticmethod
    def _get_plugin_by_slug(db: Session, slug: str) -> PluginDefinition:
        plugin = db.query(PluginDefinition).filter(PluginDefinition.slug == slug).first()
        if not plugin:
            raise NotFoundError(f"Plugin not found: {slug}")
        return plugin

    @staticmethod
    def _installation_dict(db: Session, inst: PluginInstallation) -> dict:
        plugin = inst.plugin or db.query(PluginDefinition).filter(PluginDefinition.id == inst.plugin_id).first()
        installed_ver = inst.installed_version or (
            db.query(PluginVersion).filter(PluginVersion.id == inst.installed_version_id).first()
        )
        latest_ver = (
            db.query(func.max(PluginVersion.version)).filter(PluginVersion.plugin_id == inst.plugin_id).scalar() or 1
        )
        installed_version_num = installed_ver.version if installed_ver else 1
        return {
            "id": inst.id,
            "user_id": inst.user_id,
            "plugin_id": inst.plugin_id,
            "plugin_slug": plugin.slug if plugin else "",
            "plugin_name": plugin.name if plugin else "",
            "plugin_icon": plugin.icon if plugin else "🧩",
            "installed_version_id": inst.installed_version_id,
            "installed_version": installed_version_num,
            "installed_version_label": installed_ver.version_label if installed_ver else "1.0.0",
            "latest_version": latest_ver,
            "enabled": inst.enabled,
            "settings": inst.settings or {},
            "granted_permissions": inst.granted_permissions or [],
            "available_permissions": plugin.available_permissions if plugin else [],
            "manifest": (installed_ver.manifest if installed_ver else plugin.manifest) or {},
            "settings_schema": (installed_ver.settings_schema if installed_ver else {}) or {},
            "frontend_entry": plugin.frontend_entry if plugin else None,
            "status": inst.status,
            "update_available": installed_version_num < latest_ver,
            "installed_at": inst.installed_at,
            "updated_at": inst.updated_at,
            "last_enabled_at": inst.last_enabled_at,
        }

    @staticmethod
    def _plugin_dict(db: Session, plugin: PluginDefinition, user_id: int | None) -> dict:
        current = None
        if plugin.current_version_id:
            ver = db.query(PluginVersion).filter(PluginVersion.id == plugin.current_version_id).first()
            if ver:
                current = PluginSdkService._version_dict(ver)

        installation = None
        if user_id:
            installation = (
                db.query(PluginInstallation)
                .filter(PluginInstallation.user_id == user_id, PluginInstallation.plugin_id == plugin.id)
                .first()
            )

        installed_version_num = None
        if installation:
            iv = db.query(PluginVersion).filter(PluginVersion.id == installation.installed_version_id).first()
            installed_version_num = iv.version if iv else 1

        latest_ver = (
            db.query(func.max(PluginVersion.version)).filter(PluginVersion.plugin_id == plugin.id).scalar() or 1
        )

        return {
            "id": plugin.id,
            "slug": plugin.slug,
            "name": plugin.name,
            "description": plugin.description,
            "icon": plugin.icon,
            "category": plugin.category,
            "author": plugin.author,
            "author_url": plugin.author_url,
            "is_system": plugin.is_system,
            "status": plugin.status,
            "current_version_id": plugin.current_version_id,
            "manifest": plugin.manifest or {},
            "default_settings": plugin.default_settings or {},
            "available_permissions": plugin.available_permissions or [],
            "backend_entry": plugin.backend_entry,
            "frontend_entry": plugin.frontend_entry,
            "current_version": current,
            "installed": installation is not None,
            "installation_id": installation.id if installation else None,
            "enabled": installation.enabled if installation else None,
            "update_available": bool(
                installation and installed_version_num is not None and installed_version_num < latest_ver
            ),
            "average_rating": round(float(plugin.average_rating or 0), 2),
            "rating_count": int(plugin.rating_count or 0),
            "install_count": int(plugin.install_count or 0),
            "documentation_url": plugin.documentation_url,
        }

    @staticmethod
    def overview(db: Session, user: User) -> dict:
        PluginSdkService.ensure_catalog(db)
        total = db.query(PluginDefinition).filter(PluginDefinition.status == "published").count()
        installed = db.query(PluginInstallation).filter(PluginInstallation.user_id == user.id).count()
        enabled = (
            db.query(PluginInstallation)
            .filter(PluginInstallation.user_id == user.id, PluginInstallation.enabled.is_(True))
            .count()
        )
        categories = (
            db.query(PluginDefinition.category, func.count(PluginDefinition.id))
            .filter(PluginDefinition.status == "published")
            .group_by(PluginDefinition.category)
            .all()
        )
        recent = (
            db.query(PluginEventLog)
            .filter(PluginEventLog.user_id == user.id)
            .order_by(PluginEventLog.created_at.desc())
            .limit(10)
            .all()
        )
        return {
            "total_plugins": total,
            "installed_count": installed,
            "enabled_count": enabled,
            "categories": [{"category": c, "count": n} for c, n in categories],
            "recent_events": [
                {
                    "id": r.id,
                    "plugin_slug": r.plugin_slug,
                    "event_name": r.event_name,
                    "status": r.status,
                    "created_at": r.created_at,
                }
                for r in recent
            ],
        }

    @staticmethod
    def list_plugins(db: Session, user: User, *, category: str | None = None, search: str | None = None) -> list[dict]:
        PluginSdkService.ensure_catalog(db)
        query = db.query(PluginDefinition).filter(PluginDefinition.status == "published")
        if category:
            query = query.filter(PluginDefinition.category == category)
        if search:
            like = f"%{search.strip()}%"
            query = query.filter(
                (PluginDefinition.name.ilike(like))
                | (PluginDefinition.description.ilike(like))
                | (PluginDefinition.slug.ilike(like))
            )
        plugins = query.order_by(PluginDefinition.install_count.desc(), PluginDefinition.name).all()
        return [PluginSdkService._plugin_dict(db, p, user.id) for p in plugins]

    @staticmethod
    def get_plugin(db: Session, user: User, slug: str) -> dict:
        PluginSdkService.ensure_catalog(db)
        plugin = PluginSdkService._get_plugin_by_slug(db, slug)
        return PluginSdkService._plugin_dict(db, plugin, user.id)

    @staticmethod
    def list_installed(db: Session, user: User) -> list[dict]:
        PluginSdkService.ensure_catalog(db)
        rows = (
            db.query(PluginInstallation)
            .filter(PluginInstallation.user_id == user.id)
            .order_by(PluginInstallation.installed_at.desc())
            .all()
        )
        return [PluginSdkService._installation_dict(db, r) for r in rows]

    @staticmethod
    def install(db: Session, user: User, slug: str, data, *, organization_id: int | None = None) -> dict:
        PluginSdkService.ensure_catalog(db)
        plugin = PluginSdkService._get_plugin_by_slug(db, slug)
        existing = (
            db.query(PluginInstallation)
            .filter(PluginInstallation.user_id == user.id, PluginInstallation.plugin_id == plugin.id)
            .first()
        )
        if existing:
            raise ConflictError("Plugin already installed")

        version = (
            db.query(PluginVersion).filter(PluginVersion.id == plugin.current_version_id).first()
            if plugin.current_version_id
            else None
        )
        if not version:
            raise BadRequestError("Plugin has no published version")

        perms = data.granted_permissions if data.granted_permissions else DEFAULT_PLUGIN_GRANTED
        granted = validate_permissions(perms, plugin.available_permissions or [])

        settings = dict(version.default_settings or plugin.default_settings or {})
        if data.settings:
            settings.update(data.settings)

        inst = PluginInstallation(
            user_id=user.id,
            plugin_id=plugin.id,
            organization_id=organization_id,
            installed_version_id=version.id,
            enabled=True,
            settings=settings,
            granted_permissions=granted,
            status="active",
            last_enabled_at=datetime.now(timezone.utc),
        )
        db.add(inst)
        db.flush()

        handler_cls = BACKEND_PLUGIN_REGISTRY.get(plugin.backend_entry or "")
        if handler_cls:
            handler = handler_cls()
            ctx = PluginContext(
                db=db,
                user_id=user.id,
                installation_id=inst.id,
                plugin_slug=plugin.slug,
                settings=settings,
                granted_permissions=granted,
            )
            handler.on_install(ctx)

        hist = PluginInstallationHistory(
            installation_id=inst.id,
            action="install",
            to_version=version.version,
            settings_snapshot=settings,
            performed_by_id=user.id,
        )
        db.add(hist)
        plugin.install_count = int(plugin.install_count or 0) + 1
        db.commit()
        db.refresh(inst)

        PluginEventBus.emit(
            db,
            "plugin.installed",
            {"plugin_slug": plugin.slug, "installation_id": inst.id},
            user_id=user.id,
        )
        return PluginSdkService._installation_dict(db, inst)

    @staticmethod
    def enable(db: Session, user: User, installation_id: int) -> dict:
        inst = PluginSdkService._get_installation(db, user, installation_id)
        inst.enabled = True
        inst.last_enabled_at = datetime.now(timezone.utc)
        inst.updated_at = datetime.now(timezone.utc)
        plugin = inst.plugin
        handler_cls = BACKEND_PLUGIN_REGISTRY.get((plugin.backend_entry if plugin else "") or "")
        if handler_cls and plugin:
            handler = handler_cls()
            ctx = PluginContext(
                db=db,
                user_id=user.id,
                installation_id=inst.id,
                plugin_slug=plugin.slug,
                settings=inst.settings or {},
                granted_permissions=inst.granted_permissions or [],
            )
            handler.on_enable(ctx)
        db.add(
            PluginInstallationHistory(
                installation_id=inst.id,
                action="enable",
                performed_by_id=user.id,
            )
        )
        db.commit()
        db.refresh(inst)
        return PluginSdkService._installation_dict(db, inst)

    @staticmethod
    def disable(db: Session, user: User, installation_id: int) -> dict:
        inst = PluginSdkService._get_installation(db, user, installation_id)
        inst.enabled = False
        inst.updated_at = datetime.now(timezone.utc)
        plugin = inst.plugin
        handler_cls = BACKEND_PLUGIN_REGISTRY.get((plugin.backend_entry if plugin else "") or "")
        if handler_cls and plugin:
            handler = handler_cls()
            ctx = PluginContext(
                db=db,
                user_id=user.id,
                installation_id=inst.id,
                plugin_slug=plugin.slug,
                settings=inst.settings or {},
                granted_permissions=inst.granted_permissions or [],
            )
            handler.on_disable(ctx)
        db.add(
            PluginInstallationHistory(
                installation_id=inst.id,
                action="disable",
                performed_by_id=user.id,
            )
        )
        db.commit()
        db.refresh(inst)
        return PluginSdkService._installation_dict(db, inst)

    @staticmethod
    def update_settings(db: Session, user: User, installation_id: int, data) -> dict:
        inst = PluginSdkService._get_installation(db, user, installation_id)
        settings = dict(inst.settings or {})
        settings.update(data.settings)
        inst.settings = settings
        inst.updated_at = datetime.now(timezone.utc)
        db.add(
            PluginInstallationHistory(
                installation_id=inst.id,
                action="settings_update",
                settings_snapshot=settings,
                performed_by_id=user.id,
            )
        )
        db.commit()
        db.refresh(inst)
        return PluginSdkService._installation_dict(db, inst)

    @staticmethod
    def update_permissions(db: Session, user: User, installation_id: int, data) -> dict:
        inst = PluginSdkService._get_installation(db, user, installation_id)
        plugin = inst.plugin or db.query(PluginDefinition).filter(PluginDefinition.id == inst.plugin_id).first()
        granted = validate_permissions(data.granted_permissions, plugin.available_permissions if plugin else [])
        if not granted:
            raise BadRequestError("No valid permissions granted")
        inst.granted_permissions = granted
        inst.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(inst)
        return PluginSdkService._installation_dict(db, inst)

    @staticmethod
    def update_version(db: Session, user: User, installation_id: int) -> dict:
        inst = PluginSdkService._get_installation(db, user, installation_id)
        plugin = inst.plugin or db.query(PluginDefinition).filter(PluginDefinition.id == inst.plugin_id).first()
        if not plugin or not plugin.current_version_id:
            raise BadRequestError("No update available")
        current = db.query(PluginVersion).filter(PluginVersion.id == inst.installed_version_id).first()
        latest = db.query(PluginVersion).filter(PluginVersion.id == plugin.current_version_id).first()
        if not latest or (current and current.version >= latest.version):
            raise BadRequestError("Already on latest version")
        old_v = current.version if current else None
        inst.installed_version_id = latest.id
        merged_settings = dict(latest.default_settings or {})
        merged_settings.update(inst.settings or {})
        inst.settings = merged_settings
        inst.status = "active"
        inst.updated_at = datetime.now(timezone.utc)
        handler_cls = BACKEND_PLUGIN_REGISTRY.get((plugin.backend_entry if plugin else "") or "")
        if handler_cls and plugin:
            handler = handler_cls()
            ctx = PluginContext(
                db=db,
                user_id=user.id,
                installation_id=inst.id,
                plugin_slug=plugin.slug,
                settings=inst.settings or {},
                granted_permissions=inst.granted_permissions or [],
            )
            handler.on_update(ctx, old_v or 0, latest.version)
        db.add(
            PluginInstallationHistory(
                installation_id=inst.id,
                action="update",
                from_version=old_v,
                to_version=latest.version,
                performed_by_id=user.id,
            )
        )
        db.commit()
        db.refresh(inst)
        return PluginSdkService._installation_dict(db, inst)

    @staticmethod
    def uninstall(db: Session, user: User, installation_id: int) -> None:
        inst = PluginSdkService._get_installation(db, user, installation_id)
        plugin = inst.plugin
        handler_cls = BACKEND_PLUGIN_REGISTRY.get((plugin.backend_entry if plugin else "") or "")
        if handler_cls and plugin:
            handler = handler_cls()
            ctx = PluginContext(
                db=db,
                user_id=user.id,
                installation_id=inst.id,
                plugin_slug=plugin.slug,
                settings=inst.settings or {},
                granted_permissions=inst.granted_permissions or [],
            )
            handler.on_uninstall(ctx)
        db.delete(inst)
        db.commit()

    @staticmethod
    def installation_history(db: Session, user: User, installation_id: int) -> list[dict]:
        inst = PluginSdkService._get_installation(db, user, installation_id)
        rows = (
            db.query(PluginInstallationHistory)
            .filter(PluginInstallationHistory.installation_id == inst.id)
            .order_by(PluginInstallationHistory.created_at.desc())
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
    def event_log(db: Session, user: User, *, limit: int = 50) -> list[dict]:
        rows = (
            db.query(PluginEventLog)
            .filter(PluginEventLog.user_id == user.id)
            .order_by(PluginEventLog.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": r.id,
                "plugin_slug": r.plugin_slug,
                "event_name": r.event_name,
                "hook_name": r.hook_name,
                "status": r.status,
                "duration_ms": r.duration_ms,
                "created_at": r.created_at,
            }
            for r in rows
        ]

    @staticmethod
    def sdk_docs() -> dict:
        return {
            "title": "UNTOLD Plugin SDK",
            "version": "1.0",
            "backend": {
                "base_class": "app.plugins.sdk.base.BasePlugin",
                "context": "PluginContext",
                "lifecycle": ["on_install", "on_enable", "on_disable", "on_update", "on_uninstall"],
                "handlers": ["on_event", "on_hook"],
                "register": "POST /api/v1/studio/platform/plugins/register",
            },
            "frontend": {
                "package": "src/plugin-sdk",
                "entry": "createPlugin / PluginProvider",
                "hooks": "usePluginHooks(hookName)",
            },
            "events": STUDIO_EVENTS,
            "hooks": HOOK_POINTS,
            "permissions": PLUGIN_PERMISSIONS,
            "manifest_example": PLUGIN_CATALOG[0]["manifest"],
        }

    @staticmethod
    def runtime_manifest(db: Session, user: User) -> list[dict]:
        """Enabled plugins for frontend runtime loader."""
        PluginSdkService.ensure_catalog(db)
        rows = (
            db.query(PluginInstallation)
            .filter(PluginInstallation.user_id == user.id, PluginInstallation.enabled.is_(True))
            .all()
        )
        out = []
        for inst in rows:
            d = PluginSdkService._installation_dict(db, inst)
            out.append(
                {
                    "slug": d["plugin_slug"],
                    "frontend_entry": d["frontend_entry"],
                    "manifest": d["manifest"],
                    "settings": d["settings"],
                    "granted_permissions": d["granted_permissions"],
                }
            )
        return out

    @staticmethod
    def _get_installation(db: Session, user: User, installation_id: int) -> PluginInstallation:
        inst = (
            db.query(PluginInstallation)
            .filter(PluginInstallation.id == installation_id, PluginInstallation.user_id == user.id)
            .first()
        )
        if not inst:
            raise NotFoundError("Plugin installation not found")
        return inst

    @staticmethod
    def is_plugin_enabled(db: Session, user_id: int, slug: str) -> bool:
        plugin = db.query(PluginDefinition).filter(PluginDefinition.slug == slug).first()
        if not plugin:
            return False
        inst = (
            db.query(PluginInstallation)
            .filter(PluginInstallation.user_id == user_id, PluginInstallation.plugin_id == plugin.id)
            .first()
        )
        return bool(inst and inst.enabled)

    @staticmethod
    def publish_plugin(db: Session, user: User, slug: str, *, changelog: str, release_notes: str | None = None) -> dict:
        StudioPlatformService.require_permission(db, user, None, "admin.manage")
        plugin = PluginSdkService._get_plugin_by_slug(db, slug)
        max_v = db.query(func.max(PluginVersion.version)).filter(PluginVersion.plugin_id == plugin.id).scalar() or 0
        current = (
            db.query(PluginVersion).filter(PluginVersion.id == plugin.current_version_id).first()
            if plugin.current_version_id
            else None
        )
        manifest = current.manifest if current else plugin.manifest
        version = PluginVersion(
            plugin_id=plugin.id,
            version=max_v + 1,
            version_label=f"1.{max_v}.0",
            manifest=manifest,
            settings_schema=current.settings_schema if current else {},
            default_settings=current.default_settings if current else plugin.default_settings,
            changelog=changelog,
            release_notes=release_notes,
        )
        db.add(version)
        db.flush()
        plugin.current_version_id = version.id
        plugin.updated_at = datetime.now(timezone.utc)
        for inst in db.query(PluginInstallation).filter(PluginInstallation.plugin_id == plugin.id).all():
            old = db.query(PluginVersion).filter(PluginVersion.id == inst.installed_version_id).first()
            if old and old.version < version.version:
                inst.status = "update_available"
        db.commit()
        return PluginSdkService._version_dict(version)

    @staticmethod
    def register_plugin(db: Session, user: User, manifest: dict) -> dict:
        """Third-party developers submit a new plugin to the marketplace."""
        StudioPlatformService.require_permission(db, user, None, "admin.manage")
        validated = validate_manifest(manifest)
        slug = validated["slug"]
        if db.query(PluginDefinition).filter(PluginDefinition.slug == slug).first():
            raise ConflictError(f"Plugin slug already exists: {slug}")

        plugin = PluginDefinition(
            slug=slug,
            name=validated["name"],
            description=validated["description"],
            icon=validated["icon"],
            category=validated["category"],
            author=validated["author"],
            author_url=validated.get("author_url"),
            is_system=False,
            status="published",
            manifest=validated,
            default_settings=validated["default_settings"],
            available_permissions=validated["permissions"],
            backend_entry=validated.get("entry_points", {}).get("backend"),
            frontend_entry=validated.get("entry_points", {}).get("frontend"),
        )
        db.add(plugin)
        db.flush()
        version = PluginVersion(
            plugin_id=plugin.id,
            version=1,
            version_label="1.0.0",
            manifest=validated,
            settings_schema=validated.get("settings_schema") or {},
            default_settings=validated["default_settings"],
            changelog="Initial community release",
        )
        db.add(version)
        db.flush()
        plugin.current_version_id = version.id
        plugin.documentation_url = validated.get("documentation_url") or validated.get("author_url")
        db.commit()
        return PluginSdkService._plugin_dict(db, plugin, user.id)

    @staticmethod
    def list_versions(db: Session, user: User, slug: str) -> list[dict]:
        PluginSdkService.ensure_catalog(db)
        plugin = PluginSdkService._get_plugin_by_slug(db, slug)
        rows = (
            db.query(PluginVersion)
            .filter(PluginVersion.plugin_id == plugin.id)
            .order_by(PluginVersion.version.desc())
            .all()
        )
        return [PluginSdkService._version_dict(v) for v in rows]

    @staticmethod
    def list_ratings(db: Session, user: User, slug: str, *, limit: int = 20) -> list[dict]:
        plugin = PluginSdkService._get_plugin_by_slug(db, slug)
        rows = (
            db.query(PluginRating)
            .filter(PluginRating.plugin_id == plugin.id)
            .order_by(PluginRating.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": r.id,
                "rating": r.rating,
                "review": r.review,
                "user_id": r.user_id,
                "created_at": r.created_at,
            }
            for r in rows
        ]

    @staticmethod
    def rate_plugin(db: Session, user: User, slug: str, *, rating: int, review: str | None = None) -> dict:
        if rating < 1 or rating > 5:
            raise BadRequestError("Rating must be between 1 and 5")
        plugin = PluginSdkService._get_plugin_by_slug(db, slug)
        row = (
            db.query(PluginRating)
            .filter(PluginRating.plugin_id == plugin.id, PluginRating.user_id == user.id)
            .first()
        )
        if row:
            row.rating = rating
            row.review = review
            row.updated_at = datetime.now(timezone.utc)
        else:
            row = PluginRating(plugin_id=plugin.id, user_id=user.id, rating=rating, review=review)
            db.add(row)
        db.flush()
        stats = (
            db.query(func.avg(PluginRating.rating), func.count(PluginRating.id))
            .filter(PluginRating.plugin_id == plugin.id)
            .one()
        )
        plugin.average_rating = float(stats[0] or 0)
        plugin.rating_count = int(stats[1] or 0)
        db.commit()
        return {
            "plugin_slug": slug,
            "rating": rating,
            "average_rating": round(plugin.average_rating, 2),
            "rating_count": plugin.rating_count,
        }
