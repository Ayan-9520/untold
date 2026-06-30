"""AI SEO Studio schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.domain.studio.enums import AIGenerationModule, AIGenerationStatus
from app.schemas.common import ORMBase


class SEOContentTypeInfo(BaseModel):
    id: str
    label: str


class SEOProviderInfo(BaseModel):
    id: str
    label: str
    available: bool


class SEOStudioOverviewResponse(BaseModel):
    content_types: list[SEOContentTypeInfo]
    providers: list[SEOProviderInfo]
    queue_counts: dict[str, int]


class SEOGenerateCreate(BaseModel):
    topic: str = Field(min_length=1, max_length=2000)
    content_type: str = Field(default="video", max_length=64)
    target_keyword: str = Field(default="", max_length=200)
    variant_count: int = Field(default=3, ge=1, le=5)
    project_id: int | None = None
    provider: str | None = Field(default=None, max_length=64)
    parameters: dict | None = None


class SEOSelectVariantRequest(BaseModel):
    variant_id: int


class SEOApprovalRequest(BaseModel):
    project_id: int | None = None
    notes: str | None = Field(default=None, max_length=2000)


class SEOApplyProjectRequest(BaseModel):
    project_id: int | None = None
    variant_id: int | None = None


class SEOExportResponse(BaseModel):
    generation_id: int
    variant_id: int | None
    pack: dict


class SEOApplyProjectResponse(BaseModel):
    project_id: int
    seo_title: str | None
    seo_description: str | None
    seo_keywords: list[str]


class SEOVariantResponse(BaseModel):
    id: int
    generation_id: int
    variant: int
    label: str | None
    seo_score: int | None
    is_selected: bool
    youtube_title: str
    meta_title: str
    description: str
    keywords: list[str]
    hashtags: list[str]
    tags: list[str]
    open_graph: dict[str, str]
    twitter_cards: dict[str, str]
    schema_org: dict[str, Any]
    suggestions: list[str]


class SEOJobResponse(ORMBase):
    id: int
    project_id: int | None
    module: AIGenerationModule
    prompt: str
    topic: str
    parameters: dict | None
    content_type: str
    target_keyword: str
    variant_count: int
    provider: str
    status: AIGenerationStatus
    output_text: str | None
    output_meta: dict | None
    progress: int = 0
    stage: str | None = None
    variants: list[dict] = []
    selected_variant_id: int | None = None
    seo_score: int | None = None
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


class SEOQueueResponse(BaseModel):
    queued: list[SEOJobResponse]
    running: list[SEOJobResponse]
    counts: dict[str, int]


class SEOHistoryResponse(BaseModel):
    items: list[SEOJobResponse]
    total: int
