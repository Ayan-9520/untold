"""AI Music Studio Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.studio.enums import AIGenerationModule, AIGenerationStatus
from app.schemas.common import ORMBase


class MusicCategoryInfo(BaseModel):
    id: str
    label: str


class MusicProviderInfo(BaseModel):
    id: str
    label: str
    available: bool


class MusicStudioOverviewResponse(BaseModel):
    categories: list[MusicCategoryInfo]
    providers: list[MusicProviderInfo]
    queue_counts: dict[str, int]


class MusicGenerateCreate(BaseModel):
    prompt: str = Field(min_length=1, max_length=10_000)
    category: str = Field(default="documentary", max_length=64)
    duration_seconds: int = Field(default=60, ge=10, le=180)
    loop: bool = True
    fade_in_seconds: float = Field(default=2.0, ge=0, le=10)
    fade_out_seconds: float = Field(default=3.0, ge=0, le=15)
    project_id: int | None = None
    provider: str | None = Field(default=None, max_length=64)
    parameters: dict | None = None


class MusicPreviewCreate(BaseModel):
    prompt: str = Field(min_length=1, max_length=2000)
    category: str = Field(default="documentary", max_length=64)
    duration_seconds: int = Field(default=12, ge=5, le=30)
    loop: bool = True
    fade_in_seconds: float = Field(default=1.0, ge=0, le=10)
    fade_out_seconds: float = Field(default=1.5, ge=0, le=15)
    project_id: int | None = None
    provider: str | None = Field(default=None, max_length=64)


class MusicPreviewResponse(BaseModel):
    audio_url: str | None
    duration_seconds: float
    provider: str
    mime_type: str


class MusicJobResponse(ORMBase):
    id: int
    project_id: int | None
    module: AIGenerationModule
    prompt: str
    parameters: dict | None
    category: str
    duration_seconds: int
    loop: bool
    fade_in_seconds: float
    fade_out_seconds: float
    provider: str
    status: AIGenerationStatus
    output_text: str | None
    output_meta: dict | None
    progress: int = 0
    stage: str | None = None
    bpm: int | None = None
    result_url: str | None
    error: str | None
    is_favorite: bool
    retry_count: int
    created_by_id: int | None
    author_name: str | None = None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None


class MusicQueueResponse(BaseModel):
    queued: list[MusicJobResponse]
    running: list[MusicJobResponse]
    counts: dict[str, int]


class MusicHistoryResponse(BaseModel):
    items: list[MusicJobResponse]
    total: int


class MusicVersionResponse(ORMBase):
    id: int
    generation_id: int
    version: int
    label: str | None
    result_url: str | None
    created_at: datetime


class MusicSaveAssetResponse(BaseModel):
    asset_id: int
    url: str | None
    folder: str
