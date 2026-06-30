"""Studio platform Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.domain.studio.enums import (
    AIGenerationModule,
    AIGenerationStatus,
    ApprovalStatus,
    PROJECT_STAGES,
    PublishPlatform,
    ScriptStyle,
    StudioRole,
    TaskPriority,
    TaskStatus,
)
from app.schemas.common import ORMBase


class ProjectMemberResponse(ORMBase):
    user_id: int
    full_name: str
    email: str
    role: StudioRole


class ProjectResponse(ORMBase):
    id: int
    slug: str
    title: str
    description: str | None
    category: str | None
    language: str
    tags: list[str] | None
    stage: str
    status: str
    publishing_status: str
    assignee: str
    owner_id: int | None
    sources_count: int
    version: int
    video_id: int | None
    seo_title: str | None
    seo_description: str | None
    seo_keywords: list[str] | None
    created_at: datetime
    updated_at: datetime | None
    due_date: datetime | None = None
    members: list[ProjectMemberResponse] = []
    comment_count: int = 0
    attachment_count: int = 0


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    slug: str | None = None
    description: str | None = None
    category: str | None = None
    language: str = "en"
    tags: list[str] = Field(default_factory=list)
    stage: str = "research"
    assignee: str | None = None
    due_date: datetime | None = None

    @field_validator("stage")
    @classmethod
    def validate_stage(cls, v: str) -> str:
        if v not in PROJECT_STAGES:
            raise ValueError(f"stage must be one of: {', '.join(PROJECT_STAGES)}")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        return [t.strip() for t in v if t.strip()][:20]


class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    category: str | None = None
    language: str | None = None
    tags: list[str] | None = None
    stage: str | None = None
    status: str | None = None
    assignee: str | None = None
    due_date: datetime | None = None
    seo_title: str | None = None
    seo_description: str | None = None
    seo_keywords: list[str] | None = None

    @field_validator("stage")
    @classmethod
    def validate_stage(cls, v: str | None) -> str | None:
        if v is not None and v not in PROJECT_STAGES:
            raise ValueError(f"stage must be one of: {', '.join(PROJECT_STAGES)}")
        return v


class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
    total: int
    offset: int = 0
    limit: int = 50
    has_more: bool = False


class ResearchSourceResponse(ORMBase):
    id: int
    title: str
    url: str | None
    source_type: str
    credibility_score: float | None
    notes: str | None
    created_at: datetime


class ResearchNoteResponse(ORMBase):
    id: int
    author_id: int
    content: str
    created_at: datetime


class ResearchSessionResponse(ORMBase):
    id: int
    project_id: int
    topic: str
    status: str
    ai_summary: str | None
    timeline: dict | None
    approved_at: datetime | None
    sources: list[ResearchSourceResponse] = []
    notes: list[ResearchNoteResponse] = []


class ResearchCreate(BaseModel):
    topic: str = Field(min_length=1, max_length=500)


class ResearchSourceCreate(BaseModel):
    title: str
    url: str | None = None
    source_type: str = "article"
    credibility_score: float | None = None
    notes: str | None = None


class ResearchNoteCreate(BaseModel):
    content: str = Field(min_length=1)


class ScriptVersionResponse(ORMBase):
    id: int
    version: int
    content: str
    style: ScriptStyle
    created_by_id: int
    created_at: datetime


class ScriptResponse(ORMBase):
    id: int
    project_id: int
    title: str
    status: str
    current_version_id: int | None
    versions: list[ScriptVersionResponse] = []


class ScriptCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)


class ScriptVersionCreate(BaseModel):
    content: str
    style: ScriptStyle = ScriptStyle.DOCUMENTARY


class StoryboardSceneResponse(ORMBase):
    id: int
    scene_number: int
    duration_seconds: int
    narration: str | None
    camera_angle: str | None
    camera_movement: str | None
    visual_prompt: str | None
    environment: str | None
    lighting: str | None
    reference_image_url: str | None
    status: str


class StoryboardSceneCreate(BaseModel):
    scene_number: int
    duration_seconds: int = 0
    narration: str | None = None
    camera_angle: str | None = None
    camera_movement: str | None = None
    visual_prompt: str | None = None
    environment: str | None = None
    lighting: str | None = None


class AIGenerationCreate(BaseModel):
    module: AIGenerationModule
    prompt: str = Field(min_length=1)
    parameters: dict | None = None
    project_id: int | None = None


class AIGenerationResponse(ORMBase):
    id: int
    project_id: int | None
    module: AIGenerationModule
    prompt: str
    parameters: dict | None
    status: AIGenerationStatus
    result_url: str | None
    error: str | None
    created_at: datetime
    completed_at: datetime | None


class TaskResponse(ORMBase):
    id: int
    project_id: int | None
    title: str
    description: str | None
    assignee_id: int | None
    due_date: datetime | None
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    project_id: int | None = None
    assignee_id: int | None = None
    due_date: datetime | None = None
    priority: TaskPriority = TaskPriority.MEDIUM


class ApprovalResponse(ORMBase):
    id: int
    project_id: int
    entity_type: str
    entity_id: int
    status: ApprovalStatus
    notes: str | None
    created_at: datetime


class NotificationResponse(ORMBase):
    id: int
    notification_type: str
    title: str
    body: str | None
    is_read: bool
    data: dict | None
    created_at: datetime


class PublishJobCreate(BaseModel):
    platform: PublishPlatform
    scheduled_at: datetime | None = None
    requires_approval: bool = True
    meta: dict | None = None


class PublishJobResponse(ORMBase):
    id: int
    project_id: int
    platform: PublishPlatform
    scheduled_at: datetime | None
    status: str
    published_at: datetime | None
    requires_approval: bool
    created_at: datetime


class ActivityLogResponse(ORMBase):
    id: int
    project_id: int | None
    user_id: int
    action: str
    entity_type: str | None
    entity_id: int | None
    meta: dict | None
    created_at: datetime


class DashboardOverview(BaseModel):
    active_projects: int
    pending_reviews: int
    todays_tasks: int
    ai_jobs_running: int
    published_videos: int
    storage_bytes: int
    publishing_queue: int = 0
    ai_jobs_queued: int = 0
    revenue_mrr: float = 0
    total_views: int = 0


class PipelineStageCount(BaseModel):
    stage: str
    count: int


class MonthlyMetric(BaseModel):
    month: str
    revenue: float
    views: int
    productions: int


class StatusCount(BaseModel):
    label: str
    count: int


class DashboardResponse(BaseModel):
    overview: DashboardOverview
    production_pipeline: list[PipelineStageCount]
    monthly_analytics: list[MonthlyMetric]
    project_status: list[StatusCount]
    recent_projects: list[ProjectResponse]
    recent_activity: list[ActivityLogResponse]
    upcoming_deadlines: list[TaskResponse]
    notifications: list[NotificationResponse]
    pending_approvals: list[ApprovalResponse] = []
    todays_tasks: list[TaskResponse] = []


class ProjectMemberAssign(BaseModel):
    user_id: int
    role: StudioRole = StudioRole.VIEWER


class ProjectMemberUpdate(BaseModel):
    role: StudioRole


class ProjectCommentResponse(ORMBase):
    id: int
    project_id: int
    user_id: int
    author_name: str
    content: str
    created_at: datetime
    updated_at: datetime | None


class ProjectCommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class ProjectAttachmentResponse(ORMBase):
    id: int
    project_id: int | None
    filename: str
    url: str | None
    asset_type: str
    size_bytes: int
    mime_type: str | None
    created_at: datetime


class ProjectAttachmentCreate(BaseModel):
    filename: str = Field(min_length=1, max_length=500)
    url: str | None = None
    asset_type: str = "document"
    size_bytes: int = 0
    mime_type: str | None = None


class TimelineEntryResponse(ORMBase):
    id: int
    action: str
    entity_type: str | None
    entity_id: int | None
    user_name: str
    created_at: datetime


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    assignee_id: int | None = None
    due_date: datetime | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None


class CalendarEventResponse(ORMBase):
    id: int
    project_id: int | None
    project_title: str | None = None
    title: str
    start_at: datetime
    end_at: datetime | None
    event_type: str
    created_at: datetime


class CalendarEventCreate(BaseModel):
    project_id: int | None = None
    title: str = Field(min_length=1, max_length=500)
    start_at: datetime
    end_at: datetime | None = None
    event_type: str = "deadline"


class CalendarFeedResponse(BaseModel):
    projects: list[ProjectResponse]
    events: list[CalendarEventResponse]
    tasks: list[TaskResponse]
