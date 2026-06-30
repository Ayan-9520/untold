"""Plugin manifest schema validation."""

from __future__ import annotations

from typing import Any

from app.core.exceptions import BadRequestError
from app.domain.plugins.events import STUDIO_EVENTS
from app.domain.plugins.hooks import HOOK_POINTS
from app.domain.plugins.permissions import PLUGIN_PERMISSIONS


def validate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    slug = manifest.get("slug")
    if not slug or not isinstance(slug, str) or len(slug) > 64:
        raise BadRequestError("manifest.slug is required (max 64 chars)")

    name = manifest.get("name")
    if not name:
        raise BadRequestError("manifest.name is required")

    hooks = manifest.get("hooks") or []
    subscribes = manifest.get("subscribes") or manifest.get("events") or []
    permissions = manifest.get("permissions") or manifest.get("available_permissions") or []

    for hook in hooks:
        if hook not in HOOK_POINTS:
            raise BadRequestError(f"Unknown hook: {hook}")

    for event in subscribes:
        if event not in STUDIO_EVENTS:
            raise BadRequestError(f"Unknown event: {event}")

    for perm in permissions:
        if perm not in PLUGIN_PERMISSIONS:
            raise BadRequestError(f"Unknown permission: {perm}")

    return {
        "slug": slug,
        "name": name,
        "description": manifest.get("description") or "",
        "version": int(manifest.get("version") or 1),
        "author": manifest.get("author") or "Community",
        "author_url": manifest.get("author_url"),
        "category": manifest.get("category") or "integration",
        "icon": manifest.get("icon") or "🧩",
        "hooks": list(hooks),
        "subscribes": list(subscribes),
        "permissions": list(permissions),
        "entry_points": manifest.get("entry_points") or {},
        "settings_schema": manifest.get("settings_schema") or {},
        "default_settings": manifest.get("default_settings") or {},
        "frontend_panels": manifest.get("frontend_panels") or [],
    }
