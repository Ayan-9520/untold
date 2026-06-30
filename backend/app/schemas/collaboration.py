"""Enterprise Collaboration API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CollabDocumentSave(BaseModel):
    content: dict[str, Any]
    expected_version: int
    changelog: str | None = None


class CollabConflictResolve(BaseModel):
    resolution: str = Field(pattern="^(accept_server|accept_client|merge)$")
    merged_content: dict[str, Any] | None = None


class CollabCommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=10_000)
    resource_type: str = "project"
    resource_id: int | None = None
    parent_id: int | None = None
    anchor: dict[str, Any] | None = None


class CollabPresenceUpdate(BaseModel):
    resource_type: str = "document"
    resource_id: int | None = None
    status: str = Field(default="viewing", pattern="^(viewing|editing|idle)$")
    cursor: dict[str, Any] | None = None


class CollabSharedFileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=500)
    url: str | None = None
    r2_key: str | None = None
    mime_type: str | None = None
    size_bytes: int | None = None
    permissions: dict[str, bool] | None = None


class CollabRealtimePatch(BaseModel):
    content_delta: dict[str, Any] | None = None
    cursor: dict[str, Any] | None = None


class CollabOverviewResponse(BaseModel):
    project_id: int
    presence: list[dict[str, Any]]
    pending_tasks: int
    pending_approvals: int
    unread_notifications: int
    recent_activity: list[dict[str, Any]]
    documents: list[dict[str, Any]]
