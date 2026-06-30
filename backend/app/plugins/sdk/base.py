"""Backend Plugin SDK — base classes for third-party plugin authors."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session


@dataclass
class PluginContext:
    """Runtime context passed to plugin handlers."""

    db: Session
    user_id: int
    installation_id: int
    plugin_slug: str
    settings: dict[str, Any] = field(default_factory=dict)
    granted_permissions: list[str] = field(default_factory=list)

    def has_permission(self, permission: str) -> bool:
        return permission in self.granted_permissions

    def get_setting(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)


class BasePlugin(ABC):
    """Base class for backend plugins. Subclass and implement lifecycle + handlers."""

    slug: str = ""

    def on_install(self, ctx: PluginContext) -> None:
        """Called when the plugin is installed."""

    def on_enable(self, ctx: PluginContext) -> None:
        """Called when the plugin is enabled."""

    def on_disable(self, ctx: PluginContext) -> None:
        """Called when the plugin is disabled."""

    def on_uninstall(self, ctx: PluginContext) -> None:
        """Called before uninstall."""

    def on_event(self, ctx: PluginContext, event_name: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        """Handle subscribed studio events. Return optional result dict."""
        return None

    def on_hook(self, ctx: PluginContext, hook_name: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        """Handle registered hook points. Return mutations to apply."""
        handler = getattr(self, f"hook_{hook_name.replace('.', '_')}", None)
        if callable(handler):
            return handler(ctx, payload)
        return None
