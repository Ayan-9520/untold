from datetime import datetime

from pydantic import BaseModel, Field


class ProductionResponse(BaseModel):
    id: int
    slug: str
    title: str
    stage: str
    status: str
    assignee: str
    sources_count: int
    version: int
    notes: str | None = None
    video_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ProductionListResponse(BaseModel):
    items: list[ProductionResponse]
    total: int


class ProductionUpdate(BaseModel):
    stage: str | None = None
    status: str | None = None
    assignee: str | None = None
    sources_count: int | None = Field(None, ge=0)
    version: int | None = Field(None, ge=1)
    notes: str | None = None


class AgentSummaryResponse(BaseModel):
    id: str
    role: str
    description: str
    status: str
    tasks: int
    completed_today: int


class AgentDashboardResponse(BaseModel):
    agents: list[AgentSummaryResponse]
    active_count: int
    total_queued: int
    completed_today: int
    avg_pipeline_days: float


class AssetCategorySummary(BaseModel):
    label: str
    icon: str
    count: int


class AssetLibraryResponse(BaseModel):
    categories: list[AssetCategorySummary]
    total_items: int
    video_count: int
