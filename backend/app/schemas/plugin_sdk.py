"""Plugin SDK API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PluginVersionResponse(BaseModel):
    id: int
    plugin_id: int
    version: int
    manifest: dict[str, Any]
    settings_schema: dict[str, Any]
    default_settings: dict[str, Any]
    changelog: str | None
    release_notes: str | None
    created_at: datetime | None

    model_config = {"from_attributes": True}


class PluginDefinitionResponse(BaseModel):
    id: int
    slug: str
    name: str
    description: str
    icon: str
    category: str
    author: str
    author_url: str | None
    is_system: bool
    status: str
    current_version_id: int | None
    manifest: dict[str, Any]
    default_settings: dict[str, Any]
    available_permissions: list[str]
    backend_entry: str | None
    frontend_entry: str | None
    current_version: PluginVersionResponse | None = None
    installed: bool = False
    installation_id: int | None = None
    enabled: bool | None = None
    update_available: bool = False

    model_config = {"from_attributes": True}


class PluginInstallationResponse(BaseModel):
    id: int
    user_id: int
    plugin_id: int
    plugin_slug: str
    plugin_name: str
    plugin_icon: str
    installed_version_id: int
    installed_version: int
    latest_version: int
    enabled: bool
    settings: dict[str, Any]
    granted_permissions: list[str]
    available_permissions: list[str]
    manifest: dict[str, Any]
    settings_schema: dict[str, Any]
    frontend_entry: str | None
    status: str
    update_available: bool
    installed_at: datetime | None
    updated_at: datetime | None
    last_enabled_at: datetime | None

    model_config = {"from_attributes": True}


class PluginInstallRequest(BaseModel):
    settings: dict[str, Any] | None = None
    granted_permissions: list[str] | None = None


class PluginSettingsUpdate(BaseModel):
    settings: dict[str, Any]


class PluginPermissionsUpdate(BaseModel):
    granted_permissions: list[str] = Field(min_length=1)


class PluginMarketplaceOverviewResponse(BaseModel):
    total_plugins: int
    installed_count: int
    enabled_count: int
    categories: list[dict[str, Any]]
    recent_events: list[dict[str, Any]]


class PluginSdkDocsResponse(BaseModel):
    events: dict[str, Any]
    hooks: dict[str, Any]
    permissions: dict[str, Any]
    manifest_example: dict[str, Any]


class PluginEventLogItem(BaseModel):
    id: int
    plugin_slug: str
    event_name: str
    hook_name: str | None
    status: str
    duration_ms: int | None
    created_at: datetime | None


class PluginInstallationHistoryItem(BaseModel):
    id: int
    action: str
    from_version: int | None
    to_version: int | None
    notes: str | None
    created_at: datetime | None
