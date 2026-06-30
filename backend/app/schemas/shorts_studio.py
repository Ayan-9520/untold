"""AI Shorts Studio schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.studio.enums import AIGenerationModule, AIGenerationStatus
from app.schemas.common import ORMBase


class ShortsPlatformInfo(BaseModel):
    id: str
    label: str


class ShortsProviderInfo(BaseModel):
    id: str
    label: str
    available: bool


class ShortsStudioOverviewResponse(BaseModel):
    platforms: list[ShortsPlatformInfo]
    providers: list[ShortsProviderInfo]
    queue_counts: dict[str, int]


class ShortsGenerateCreate(BaseModel):
    source_video_url: str = Field(min_length=1, max_length=2000)
    topic: str = Field(default="", max_length=500)
    platforms: list[str] | None = None
    auto_highlights: bool = True
    captions: bool = True
    auto_zoom: bool = True
    hook_optimization: bool = True
    clip_duration_seconds: int = Field(default=30, ge=15, le=60)
    project_id: int | None = None
    provider: str | None = Field(default=None, max_length=64)
    parameters: dict | None = None


class ShortsQueuePublishCreate(BaseModel):
    platforms: list[str] | None = None


class ShortsJobResponse(ORMBase):
    id: int
    project_id: int | None
    module: AIGenerationModule
    prompt: str
    topic: str
    source_video_url: str | None
    parameters: dict | None
    platforms: list[str]
    auto_highlights: bool
    captions: bool
    auto_zoom: bool
    hook_optimization: bool
    provider: str
    status: AIGenerationStatus
    output_text: str | None
    output_meta: dict | None
    progress: int = 0
    stage: str | None = None
    highlights: list[dict] = []
    clips: list[dict] = []
    thumbnail_url: str | None = None
    hashtags: list[str] = []
    hook: str | None = None
    publish_queue: list[dict] = []
    result_url: str | None
    error: str | None
    retry_count: int
    created_by_id: int | None
    author_name: str | None = None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None


class ShortsQueueResponse(BaseModel):
    queued: list[ShortsJobResponse]
    running: list[ShortsJobResponse]
    counts: dict[str, int]


class ShortsHistoryResponse(BaseModel):
    items: list[ShortsJobResponse]
    total: int


class ShortsPublishQueueResponse(BaseModel):
    publish_jobs: list[dict]
    count: int


class ShortsSaveAssetResponse(BaseModel):
    asset_id: int
    url: str | None
    folder: str
