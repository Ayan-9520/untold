"""Enterprise agent platform API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AgentRegisterRequest(BaseModel):
    slug: str = Field(min_length=2, max_length=64, pattern=r"^[a-z0-9-]+$")
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1)
    category: str = "custom"
    config_schema: dict[str, Any] = Field(default_factory=dict)
    available_permissions: list[str] | None = None


class AgentMemoryUpsert(BaseModel):
    memory_key: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    project_id: int | None = None
    meta: dict[str, Any] | None = None
    expires_at: datetime | None = None


class AgentScheduleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    cron_expression: str = Field(min_length=5, max_length=120)
    payload: dict[str, Any] = Field(default_factory=dict)


class AgentMessageSend(BaseModel):
    to_slug: str = Field(min_length=1, max_length=64)
    message_type: str = "task"
    payload: dict[str, Any] = Field(default_factory=dict)


class AgentRunRequest(BaseModel):
    payload: dict[str, Any] = Field(default_factory=dict)
    project_id: int | None = None
