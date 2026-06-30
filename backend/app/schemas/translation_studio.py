"""AI Translation Studio schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.domain.studio.enums import AIGenerationModule, AIGenerationStatus
from app.schemas.common import ORMBase


class TranslationLanguageInfo(BaseModel):
    code: str
    label: str


class TranslationContentTypeInfo(BaseModel):
    id: str
    label: str


class TranslationProviderInfo(BaseModel):
    id: str
    label: str
    available: bool


class TranslationStudioOverviewResponse(BaseModel):
    languages: list[TranslationLanguageInfo]
    content_types: list[TranslationContentTypeInfo]
    providers: list[TranslationProviderInfo]
    queue_counts: dict[str, int]
    translation_memory_count: int


class TranslationGenerateCreate(BaseModel):
    source_text: str = Field(min_length=1, max_length=50000)
    content_type: str = Field(default="script", max_length=64)
    source_lang: str = Field(default="en", max_length=16)
    target_lang: str = Field(default="es", max_length=16)
    auto_sync: bool = True
    generate_srt: bool = True
    generate_vtt: bool = True
    project_id: int | None = None
    provider: str | None = Field(default=None, max_length=64)
    parameters: dict | None = None


class TranslationApprovalRequest(BaseModel):
    project_id: int | None = None
    notes: str | None = Field(default=None, max_length=2000)


class TranslationSubtitlesResponse(BaseModel):
    srt: str | None = None
    vtt: str | None = None
    srt_url: str | None = None
    vtt_url: str | None = None


class TranslationVersionResponse(BaseModel):
    id: int
    generation_id: int
    version: int
    label: str | None
    result_url: str | None
    output_meta: dict[str, Any] | None
    created_at: datetime | None


class TranslationMemoryEntry(BaseModel):
    id: int
    source_lang: str
    target_lang: str
    content_type: str
    source_text: str
    translated_text: str
    usage_count: int
    updated_at: datetime | None
    created_at: datetime | None


class TranslationMemoryResponse(BaseModel):
    items: list[TranslationMemoryEntry]
    total: int


class TranslationJobResponse(ORMBase):
    id: int
    project_id: int | None
    module: AIGenerationModule
    prompt: str
    source_text: str
    parameters: dict | None
    content_type: str
    source_lang: str
    target_lang: str
    auto_sync: bool
    generate_srt: bool
    generate_vtt: bool
    provider: str
    status: AIGenerationStatus
    output_text: str | None
    translated_text: str | None
    output_meta: dict | None
    progress: int = 0
    stage: str | None = None
    tm_hit: bool = False
    srt_url: str | None = None
    vtt_url: str | None = None
    srt_content: str | None = None
    vtt_content: str | None = None
    version_id: int | None = None
    approval_status: str = "none"
    result_url: str | None
    error: str | None
    retry_count: int
    created_by_id: int | None
    author_name: str | None = None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None


class TranslationQueueResponse(BaseModel):
    queued: list[TranslationJobResponse]
    running: list[TranslationJobResponse]
    counts: dict[str, int]


class TranslationHistoryResponse(BaseModel):
    items: list[TranslationJobResponse]
    total: int
