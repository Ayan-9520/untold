"""AI Publishing Agent schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class PublishingAgentPlatformInfo(BaseModel):
    id: str
    label: str


class PublishingAgentOverviewResponse(BaseModel):
    platforms: list[PublishingAgentPlatformInfo]
    webhook_events: list[str]
    total_runs: int
    active_runs: int
    failed_jobs: int
    published_jobs: int
    webhook_count: int
    analytics_by_platform: dict[str, int]
    queue_counts: dict[str, int]


class PublishingAgentCreate(BaseModel):
    project_id: int
    platforms: list[str] = Field(min_length=1)
    scheduled_at: datetime | None = None
    requires_approval: bool = True
    seo_title: str | None = Field(default=None, max_length=500)
    seo_description: str | None = None
    seo_keywords: list[str] | None = None
    thumbnail_url: str | None = Field(default=None, max_length=1000)


class PublishingAgentRetryRequest(BaseModel):
    job_ids: list[int] | None = None


class PublishingAgentApprovalRequest(BaseModel):
    notes: str | None = Field(default=None, max_length=2000)


class PublishingAgentRunResponse(BaseModel):
    id: int
    project_id: int
    project_title: str | None = None
    platforms: list[str]
    scheduled_at: datetime | None
    status: str
    requires_approval: bool
    approval_status: str
    progress: int
    jobs: list[dict] = []
    webhook_deliveries: list[dict] = []
    error_message: str | None
    created_by_id: int | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime | None


class PublishingAgentQueueResponse(BaseModel):
    runs: list[PublishingAgentRunResponse]
    jobs: list[dict]


class PublishingAgentHistoryResponse(BaseModel):
    items: list[PublishingAgentRunResponse]
    total: int


class PublishingAgentAnalyticsResponse(BaseModel):
    days: int
    by_platform: dict[str, dict[str, int]]
    recent_events: list[dict]


class WebhookCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    url: str = Field(min_length=8, max_length=2000)
    events: list[str] = Field(default_factory=list)
    secret: str | None = Field(default=None, max_length=255)
    is_active: bool = True
    project_id: int | None = None


class WebhookUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    url: str | None = Field(default=None, max_length=2000)
    events: list[str] | None = None
    secret: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    project_id: int | None = None


class WebhookResponse(BaseModel):
    id: int
    name: str
    url: str
    events: list[str]
    is_active: bool
    project_id: int | None
    last_triggered_at: datetime | None
    created_at: datetime | None
