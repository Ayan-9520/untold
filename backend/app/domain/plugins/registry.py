"""Plugin hook registry and event bus — dispatches to installed plugins."""

from __future__ import annotations

import logging
import time
from typing import Any

from sqlalchemy.orm import Session

from app.domain.plugins.samples import BACKEND_PLUGIN_REGISTRY
from app.models.studio_platform import PluginDefinition, PluginEventLog, PluginInstallation
from app.plugins.sdk import BasePlugin, PluginContext

logger = logging.getLogger(__name__)


class PluginEventBus:
    """Emit studio events and run hook chains for enabled plugin installations."""

    @staticmethod
    def _build_context(db: Session, inst: PluginInstallation) -> PluginContext:
        plugin = inst.plugin or db.query(PluginDefinition).filter(PluginDefinition.id == inst.plugin_id).first()
        return PluginContext(
            db=db,
            user_id=inst.user_id,
            installation_id=inst.id,
            plugin_slug=plugin.slug if plugin else "",
            settings=inst.settings or {},
            granted_permissions=inst.granted_permissions or [],
        )

    @staticmethod
    def _load_handler(plugin: PluginDefinition) -> BasePlugin | None:
        entry = plugin.backend_entry or (plugin.manifest or {}).get("entry_points", {}).get("backend")
        if not entry or entry not in BACKEND_PLUGIN_REGISTRY:
            return None
        return BACKEND_PLUGIN_REGISTRY[entry]()

    @staticmethod
    def _plugin_subscribes(plugin: PluginDefinition, event_name: str) -> bool:
        manifest = plugin.manifest or {}
        subscribes = manifest.get("subscribes") or manifest.get("events") or []
        return event_name in subscribes

    @staticmethod
    def _plugin_has_hook(plugin: PluginDefinition, hook_name: str) -> bool:
        manifest = plugin.manifest or {}
        hooks = manifest.get("hooks") or []
        return hook_name in hooks

    @staticmethod
    def _log_dispatch(
        db: Session,
        *,
        installation_id: int | None,
        plugin_slug: str,
        event_name: str,
        hook_name: str | None,
        status: str,
        payload: dict | None,
        result: dict | None,
        error_message: str | None,
        duration_ms: int,
        user_id: int | None,
    ) -> None:
        row = PluginEventLog(
            installation_id=installation_id,
            plugin_slug=plugin_slug,
            event_name=event_name,
            hook_name=hook_name,
            status=status,
            payload=payload,
            result=result,
            error_message=error_message,
            duration_ms=duration_ms,
            user_id=user_id,
        )
        db.add(row)

    @staticmethod
    def emit(
        db: Session,
        event_name: str,
        payload: dict[str, Any],
        *,
        user_id: int | None = None,
        commit: bool = True,
    ) -> list[dict[str, Any]]:
        """Dispatch event to all enabled installations subscribed to this event."""
        results: list[dict[str, Any]] = []
        query = db.query(PluginInstallation).filter(PluginInstallation.enabled.is_(True))
        if user_id is not None:
            query = query.filter(PluginInstallation.user_id == user_id)

        for inst in query.all():
            plugin = inst.plugin or db.query(PluginDefinition).filter(PluginDefinition.id == inst.plugin_id).first()
            if not plugin or not PluginEventBus._plugin_subscribes(plugin, event_name):
                continue

            handler = PluginEventBus._load_handler(plugin)
            start = time.perf_counter()
            status = "success"
            result: dict | None = None
            error_message: str | None = None
            try:
                if handler:
                    ctx = PluginEventBus._build_context(db, inst)
                    result = handler.on_event(ctx, event_name, payload) or {}
                else:
                    result = {"acknowledged": True, "frontend_only": True}
                results.append({"plugin_slug": plugin.slug, "installation_id": inst.id, "result": result})
            except Exception as exc:
                status = "error"
                error_message = str(exc)
                logger.exception("Plugin event handler failed slug=%s event=%s", plugin.slug, event_name)
                results.append({"plugin_slug": plugin.slug, "installation_id": inst.id, "error": error_message})

            duration_ms = int((time.perf_counter() - start) * 1000)
            PluginEventBus._log_dispatch(
                db,
                installation_id=inst.id,
                plugin_slug=plugin.slug,
                event_name=event_name,
                hook_name=None,
                status=status,
                payload=payload,
                result=result,
                error_message=error_message,
                duration_ms=duration_ms,
                user_id=user_id or inst.user_id,
            )

        if commit:
            db.commit()
        return results

    @staticmethod
    def run_hooks(
        db: Session,
        hook_name: str,
        payload: dict[str, Any],
        *,
        user_id: int | None = None,
        commit: bool = True,
    ) -> dict[str, Any]:
        """Run hook chain; later plugins can mutate accumulated payload."""
        merged = dict(payload)
        query = db.query(PluginInstallation).filter(PluginInstallation.enabled.is_(True))
        if user_id is not None:
            query = query.filter(PluginInstallation.user_id == user_id)

        for inst in query.all():
            plugin = inst.plugin or db.query(PluginDefinition).filter(PluginDefinition.id == inst.plugin_id).first()
            if not plugin or not PluginEventBus._plugin_has_hook(plugin, hook_name):
                continue

            handler = PluginEventBus._load_handler(plugin)
            start = time.perf_counter()
            status = "success"
            result: dict | None = None
            error_message: str | None = None
            try:
                if handler:
                    ctx = PluginEventBus._build_context(db, inst)
                    result = handler.on_hook(ctx, hook_name, merged) or {}
                    merged.update(result)
            except Exception as exc:
                status = "error"
                error_message = str(exc)
                logger.exception("Plugin hook failed slug=%s hook=%s", plugin.slug, hook_name)

            duration_ms = int((time.perf_counter() - start) * 1000)
            PluginEventBus._log_dispatch(
                db,
                installation_id=inst.id,
                plugin_slug=plugin.slug,
                event_name=hook_name,
                hook_name=hook_name,
                status=status,
                payload=payload,
                result=result,
                error_message=error_message,
                duration_ms=duration_ms,
                user_id=user_id or inst.user_id,
            )

        if commit:
            db.commit()
        return merged
