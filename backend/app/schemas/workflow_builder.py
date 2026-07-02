"""Workflow builder API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class WorkflowGraphSchema(BaseModel):
    nodes: list[dict[str, Any]] = Field(default_factory=list)
    edges: list[dict[str, Any]] = Field(default_factory=list)
    viewport: dict[str, Any] = Field(default_factory=dict)


class WorkflowDefinitionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    project_id: int | None = None
    graph: WorkflowGraphSchema | None = None
    is_template: bool = False


class WorkflowDefinitionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: str | None = None
    project_id: int | None = None


class WorkflowVersionCreate(BaseModel):
    graph: WorkflowGraphSchema
    changelog: str | None = None


class WorkflowExecuteRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=500)
    project_id: int | None = None
    version_id: int | None = None
    trigger_type: str = "manual"
    auto_run: bool = True
    requires_approval: bool = False
    scheduled_at: datetime | None = None
    providers: dict[str, str | None] = Field(default_factory=dict)
    publish_platforms: list[str] = Field(default_factory=lambda: ["originals", "youtube"])
    translation_language: str | None = None
    prompts: dict[str, str] | None = None


class WorkflowTriggerCreate(BaseModel):
    trigger_type: str = Field(pattern="^(manual|api|webhook|cron|email|event)$")
    name: str = Field(min_length=1, max_length=200)
    version_id: int | None = None
    enabled: bool = True
    cron_expression: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)


class WorkflowTriggerUpdate(BaseModel):
    name: str | None = None
    enabled: bool | None = None
    version_id: int | None = None
    cron_expression: str | None = None
    config: dict[str, Any] | None = None


class WorkflowVersionResponse(BaseModel):
    id: int
    definition_id: int
    version: int
    graph: dict[str, Any]
    changelog: str | None
    created_at: datetime | None

    model_config = {"from_attributes": True}


class WorkflowDefinitionResponse(BaseModel):
    id: int
    name: str
    description: str | None
    project_id: int | None
    is_template: bool
    is_system: bool
    status: str
    current_version_id: int | None
    created_at: datetime | None
    updated_at: datetime | None
    current_version: WorkflowVersionResponse | None = None

    model_config = {"from_attributes": True}


class WorkflowTriggerResponse(BaseModel):
    id: int
    definition_id: int
    version_id: int | None
    trigger_type: str
    name: str
    enabled: bool
    config: dict[str, Any]
    webhook_secret: str | None = None
    webhook_url: str | None = None
    api_key: str | None = None
    api_key_prefix: str | None = None
    email_token: str | None = None
    email_url: str | None = None
    cron_expression: str | None
    next_run_at: datetime | None
    last_run_at: datetime | None
    created_at: datetime | None

    model_config = {"from_attributes": True}


class WorkflowExecutionLogResponse(BaseModel):
    id: int
    run_id: int
    node_id: str | None
    level: str
    stage: str | None
    message: str
    meta: dict[str, Any]
    created_at: datetime | None

    model_config = {"from_attributes": True}


class WorkflowExecutionLogsPage(BaseModel):
    items: list[WorkflowExecutionLogResponse]
    total: int


class WorkflowNodeCatalogResponse(BaseModel):
    nodes: list[dict[str, Any]]


class WorkflowDashboardResponse(BaseModel):
    total_definitions: int
    total_templates: int
    runs_today: int
    runs_active: int
    runs_completed: int
    runs_failed: int
    recent_runs: list[dict[str, Any]]
