"""AI Video Studio Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.studio.enums import AIGenerationModule, AIGenerationStatus
from app.schemas.common import ORMBase


class VideoTypeInfo(BaseModel):
    id: str
    label: str


class VideoProviderInfo(BaseModel):
    id: str
    label: str
    available: bool


class VideoStudioOverviewResponse(BaseModel):
    video_types: list[VideoTypeInfo]
    providers: list[VideoProviderInfo]
    queue_counts: dict[str, int]


class VideoGenerateCreate(BaseModel):
    prompt: str = Field(min_length=1, max_length=10_000)
    video_type: str = Field(default="b_roll", max_length=64)
    duration_seconds: int = Field(default=8, ge=4, le=30)
    aspect_ratio: str = Field(default="16:9", max_length=16)
    fps: int = Field(default=24, ge=12, le=60)
    project_id: int | None = None
    provider: str | None = Field(default=None, max_length=64)
    parameters: dict | None = None


class VideoJobResponse(ORMBase):
    id: int
    project_id: int | None
    module: AIGenerationModule
    prompt: str
    parameters: dict | None
    video_type: str
    duration_seconds: int
    aspect_ratio: str
    provider: str
    status: AIGenerationStatus
    output_text: str | None
    output_meta: dict | None
    progress: int = 0
    stage: str | None = None
    preview_url: str | None = None
    mime_type: str | None = None
    result_url: str | None
    error: str | None
    retry_count: int
    created_by_id: int | None
    author_name: str | None = None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None


class VideoQueueResponse(BaseModel):
    queued: list[VideoJobResponse]
    running: list[VideoJobResponse]
    counts: dict[str, int]


class VideoHistoryResponse(BaseModel):
    items: list[VideoJobResponse]
    total: int


class VideoVersionResponse(ORMBase):
    id: int
    generation_id: int
    version: int
    label: str | None
    result_url: str | None
    created_at: datetime


class VideoSaveAssetResponse(BaseModel):
    asset_id: int
    url: str | None
    folder: str
