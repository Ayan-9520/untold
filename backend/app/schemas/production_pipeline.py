"""Workflow Engine API schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class PipelineStageStatus(BaseModel):
    id: str
    label: str
    status: str = "pending"
    generation_id: int | None = None
    output_preview: str | None = None
    result_url: str | None = None
    publish_run_id: int | None = None
    error: str | None = None


class WorkflowLogEntry(BaseModel):
    ts: str
    level: str
    message: str
    stage: str | None = None


class WorkflowPromptOverrides(BaseModel):
    research: str | None = Field(default=None, max_length=50_000)
    script: str | None = Field(default=None, max_length=50_000)
    thumbnail: str | None = Field(default=None, max_length=50_000)
    seo: str | None = Field(default=None, max_length=50_000)
    translation: str | None = Field(default=None, max_length=50_000)
    voice: str | None = Field(default=None, max_length=50_000)


class WorkflowPromptTemplate(BaseModel):
    key: str
    label: str
    template: str
    placeholders: list[str] = Field(default_factory=list)


class WorkflowPromptsResponse(BaseModel):
    prompts: list[WorkflowPromptTemplate]


class ProductionPipelineCreate(BaseModel):
    topic: str = Field(min_length=3, max_length=500)
    project_id: int | None = None
    requires_approval: bool = False
    auto_run: bool = True
    publish_platforms: list[str] | None = None
    translation_language: str | None = Field(default=None, max_length=8)
    prompts: WorkflowPromptOverrides | None = None
    research_provider: str | None = None
    script_provider: str | None = None
    storyboard_provider: str | None = None
    image_provider: str | None = None
    voice_provider: str | None = None
    video_provider: str | None = None
    music_provider: str | None = None
    translation_provider: str | None = None
    seo_provider: str | None = None
    publisher_provider: str | None = None


class WorkflowApprovalRequest(BaseModel):
    notes: str | None = Field(default=None, max_length=2000)


class ProductionPipelineRunResponse(ORMBase):
    id: int
    project_id: int | None
    topic: str
    status: str
    requires_approval: bool = False
    approval_status: str = "none"
    retry_count: int = 0
    current_stage: str | None
    progress: int
    stages: list[PipelineStageStatus] = Field(default_factory=list)
    output_meta: dict | None = None
    error_message: str | None = None
    created_by_id: int | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime | None = None
    workflow_definition_id: int | None = None
    workflow_version_id: int | None = None
    trigger_type: str | None = None
    graph_snapshot: dict | None = None
    node_executions: dict | None = None
    scheduled_at: datetime | None = None


class WorkflowStatusResponse(BaseModel):
    id: int
    status: str
    approval_status: str
    current_stage: str | None
    progress: int
    retry_count: int
    error_message: str | None = None


class WorkflowHistoryResponse(BaseModel):
    items: list[ProductionPipelineRunResponse]
    total: int


class WorkflowLogsResponse(BaseModel):
    run_id: int
    logs: list[WorkflowLogEntry]


class ProductionPipelineOverviewResponse(BaseModel):
    engine: dict
    steps: list[dict]
    prompts: list[WorkflowPromptTemplate] = Field(default_factory=list)
    recent_runs: list[ProductionPipelineRunResponse]
