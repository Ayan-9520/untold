"""AI Voice Studio Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.studio.enums import AIGenerationModule, AIGenerationStatus
from app.schemas.common import ORMBase


class LanguageInfo(BaseModel):
    id: str
    label: str


class EmotionInfo(BaseModel):
    id: str
    label: str


class VoiceInfo(BaseModel):
    id: str
    label: str


class VoiceProviderInfo(BaseModel):
    id: str
    label: str
    available: bool


class VoiceStudioOverviewResponse(BaseModel):
    languages: list[LanguageInfo]
    emotions: list[EmotionInfo]
    voices_by_language: dict[str, list[VoiceInfo]]
    providers: list[VoiceProviderInfo]
    queue_counts: dict[str, int]


class VoiceGenerateCreate(BaseModel):
    text: str = Field(min_length=1, max_length=20_000)
    language: str = Field(default="en", max_length=16)
    emotion: str = Field(default="neutral", max_length=64)
    pitch: float = Field(default=1.0, ge=0.5, le=2.0)
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    voice_id: str = Field(default="en-documentary", max_length=64)
    translate_to: str | None = Field(default=None, max_length=16)
    sync_subtitles: bool = True
    project_id: int | None = None
    provider: str | None = Field(default=None, max_length=64)
    parameters: dict | None = None


class VoicePreviewCreate(BaseModel):
    text: str = Field(min_length=1, max_length=500)
    language: str = Field(default="en", max_length=16)
    emotion: str = Field(default="neutral", max_length=64)
    pitch: float = Field(default=1.0, ge=0.5, le=2.0)
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    voice_id: str = Field(default="en-documentary", max_length=64)
    sync_subtitles: bool = False
    project_id: int | None = None
    provider: str | None = Field(default=None, max_length=64)
    translate_to: str | None = None


class VoiceTranslateCreate(BaseModel):
    text: str = Field(min_length=1, max_length=20_000)
    language: str = Field(default="en", max_length=16)
    translate_to: str = Field(max_length=16)


class VoicePreviewResponse(BaseModel):
    audio_url: str | None
    duration_seconds: float
    provider: str
    mime_type: str


class VoiceTranslateResponse(BaseModel):
    source_language: str
    target_language: str
    original_text: str
    translated_text: str


class VoiceJobResponse(ORMBase):
    id: int
    project_id: int | None
    module: AIGenerationModule
    text: str
    prompt: str
    parameters: dict | None
    language: str
    emotion: str
    pitch: float
    speed: float
    voice_id: str
    translate_to: str | None
    sync_subtitles: bool
    provider: str
    status: AIGenerationStatus
    output_text: str | None
    output_meta: dict | None
    progress: int = 0
    stage: str | None = None
    duration_seconds: float | None = None
    subtitles_url: str | None = None
    translated_text: str | None = None
    result_url: str | None
    error: str | None
    retry_count: int
    created_by_id: int | None
    author_name: str | None = None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None


class VoiceQueueResponse(BaseModel):
    queued: list[VoiceJobResponse]
    running: list[VoiceJobResponse]
    counts: dict[str, int]


class VoiceHistoryResponse(BaseModel):
    items: list[VoiceJobResponse]
    total: int


class VoiceSubtitlesResponse(BaseModel):
    srt: str | None
    vtt: str | None
    subtitles_url: str | None


class VoiceVersionResponse(ORMBase):
    id: int
    generation_id: int
    version: int
    label: str | None
    result_url: str | None
    created_at: datetime


class VoiceSaveAssetResponse(BaseModel):
    asset_id: int
    url: str | None
    folder: str
