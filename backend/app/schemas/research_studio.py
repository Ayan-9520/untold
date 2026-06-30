"""Research Studio Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class ResearchWorkspaceResponse(ORMBase):
    id: int
    project_id: int
    project_title: str | None = None
    topic: str
    status: str
    workspace_content: str
    content_version: int
    ai_summary: str | None
    statistics: list[dict] = []
    public_facts: list[dict] = []
    follow_up_questions: list[str] = []
    rejection_notes: str | None = None
    last_auto_saved_at: datetime | None
    approved_at: datetime | None
    created_at: datetime
    updated_at: datetime | None


class ResearchWorkspaceAutoSave(BaseModel):
    workspace_content: str = Field(max_length=500_000)
    create_version: bool = False


class ResearchNoteResponse(ORMBase):
    id: int
    author_id: int
    author_name: str | None = None
    title: str | None
    content: str
    is_pinned: bool
    created_at: datetime
    updated_at: datetime | None


class ResearchNoteCreate(BaseModel):
    title: str | None = Field(default=None, max_length=300)
    content: str = Field(min_length=1, max_length=50_000)
    is_pinned: bool = False


class ResearchNoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = Field(default=None, max_length=50_000)
    is_pinned: bool | None = None


class ResearchSourceResponse(ORMBase):
    id: int
    title: str
    url: str | None
    source_type: str
    credibility_score: float | None
    notes: str | None
    excerpt: str | None
    is_bookmarked: bool
    created_at: datetime


class ResearchSourceCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    url: str | None = None
    source_type: str = "article"
    credibility_score: float | None = Field(default=None, ge=0, le=1)
    notes: str | None = None
    excerpt: str | None = None
    is_bookmarked: bool = False


class ResearchSourceUpdate(BaseModel):
    title: str | None = None
    url: str | None = None
    source_type: str | None = None
    credibility_score: float | None = Field(default=None, ge=0, le=1)
    notes: str | None = None
    excerpt: str | None = None
    is_bookmarked: bool | None = None


class ResearchBookmarkResponse(ORMBase):
    id: int
    title: str
    url: str | None
    excerpt: str | None
    color: str
    created_at: datetime


class ResearchBookmarkCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    url: str | None = None
    excerpt: str | None = None
    color: str = "gold"


class ResearchFactCheckResponse(ORMBase):
    id: int
    claim: str
    status: str
    source_id: int | None
    notes: str | None
    checked_by_id: int | None
    created_at: datetime


class ResearchFactCheckCreate(BaseModel):
    claim: str = Field(min_length=1, max_length=5000)
    source_id: int | None = None
    notes: str | None = None


class ResearchFactCheckUpdate(BaseModel):
    status: str | None = Field(default=None, pattern="^(pending|verified|disputed|rejected)$")
    notes: str | None = None
    source_id: int | None = None


class ResearchCommentResponse(ORMBase):
    id: int
    user_id: int
    author_name: str
    content: str
    created_at: datetime


class ResearchCommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class ResearchTimelineEventResponse(ORMBase):
    id: int
    event_date: datetime
    title: str
    description: str | None
    event_type: str
    created_at: datetime


class ResearchTimelineEventCreate(BaseModel):
    event_date: datetime
    title: str = Field(min_length=1, max_length=500)
    description: str | None = None
    event_type: str = "milestone"


class ResearchVersionResponse(ORMBase):
    id: int
    version: int
    workspace_content: str
    created_by_id: int
    author_name: str | None = None
    created_at: datetime


class ResearchAIRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=10_000)
    focus: str | None = Field(default=None, max_length=200)
    action: str = Field(default="full_research", pattern="^(full_research|summary|timeline|statistics|public_facts|follow_up|fact_check)$")
    provider: str | None = None


class ResearchAIResponse(BaseModel):
    summary: str
    suggestions: list[str] = []
    follow_up_questions: list[str] = []
    statistics: list[dict] = []
    public_facts: list[dict] = []
    generation_id: int | None = None
    provider: str | None = None


class ResearchTopicUpdate(BaseModel):
    topic: str = Field(min_length=1, max_length=500)


class ResearchApprovalReject(BaseModel):
    notes: str | None = None


class ResearchAIHistoryItem(BaseModel):
    id: int
    action: str
    prompt: str
    provider: str
    response: dict
    created_at: datetime


class ResearchProviderInfo(BaseModel):
    id: str
    label: str
    available: bool


class ResearchFullResponse(ORMBase):
    workspace: ResearchWorkspaceResponse
    notes: list[ResearchNoteResponse]
    sources: list[ResearchSourceResponse]
    bookmarks: list[ResearchBookmarkResponse]
    fact_checks: list[ResearchFactCheckResponse]
    comments: list[ResearchCommentResponse]
    timeline: list[ResearchTimelineEventResponse]
    versions: list[ResearchVersionResponse]
    ai_history: list[ResearchAIHistoryItem] = []
    providers: list[ResearchProviderInfo] = []
