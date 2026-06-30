"""AI Agent Marketplace API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AgentVersionResponse(BaseModel):
    id: int
    agent_id: int
    version: int
    default_config: dict[str, Any]
    config_schema: dict[str, Any]
    changelog: str | None
    release_notes: str | None
    created_at: datetime | None

    model_config = {"from_attributes": True}


class MarketplaceAgentResponse(BaseModel):
    id: int
    slug: str
    name: str
    description: str
    icon: str
    category: str
    studio_route: str | None
    is_system: bool
    status: str
    current_version_id: int | None
    default_config: dict[str, Any]
    available_permissions: list[str]
    current_version: AgentVersionResponse | None = None
    installed: bool = False
    installation_id: int | None = None
    enabled: bool | None = None
    update_available: bool = False

    model_config = {"from_attributes": True}


class AgentInstallationResponse(BaseModel):
    id: int
    user_id: int
    agent_id: int
    agent_slug: str
    agent_name: str
    agent_icon: str
    installed_version_id: int
    installed_version: int
    latest_version: int
    enabled: bool
    config: dict[str, Any]
    granted_permissions: list[str]
    available_permissions: list[str]
    status: str
    update_available: bool
    studio_route: str | None
    installed_at: datetime | None
    updated_at: datetime | None
    last_enabled_at: datetime | None

    model_config = {"from_attributes": True}


class AgentInstallRequest(BaseModel):
    config: dict[str, Any] | None = None
    granted_permissions: list[str] | None = None


class AgentConfigUpdate(BaseModel):
    config: dict[str, Any]


class AgentPermissionsUpdate(BaseModel):
    granted_permissions: list[str] = Field(min_length=1)


class AgentInstallationHistoryItem(BaseModel):
    id: int
    action: str
    from_version: int | None
    to_version: int | None
    notes: str | None
    created_at: datetime | None

    model_config = {"from_attributes": True}


class MarketplaceOverviewResponse(BaseModel):
    total_agents: int
    installed_count: int
    enabled_count: int
    updates_available: int
    agents: list[MarketplaceAgentResponse]
    installations: list[AgentInstallationResponse]
