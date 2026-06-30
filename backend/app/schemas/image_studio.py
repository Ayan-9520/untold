"""AI Image Studio Pydantic schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.domain.studio.enums import AIGenerationModule, AIGenerationStatus
from app.domain.security.sanitization import reject_script_markup
from app.schemas.common import ORMBase


class ImageTypeInfo(BaseModel):
    id: str
    label: str


class ImageProviderInfo(BaseModel):
    id: str
    label: str
    available: bool


class ImageStudioOverviewResponse(BaseModel):
    image_types: list[ImageTypeInfo]
    providers: list[ImageProviderInfo]
    queue_counts: dict[str, int]


class ImageGenerateCreate(BaseModel):
    prompt: str = Field(min_length=1, max_length=10_000)
    image_type: str = Field(default="illustration", max_length=64)
    action: Literal["generate", "upscale", "variation"] = "generate"
    aspect_ratio: str = Field(default="16:9", max_length=16)
    project_id: int | None = None
    provider: str | None = Field(default=None, max_length=64)
    parent_generation_id: int | None = None
    parameters: dict | None = None

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, value: str) -> str:
        return reject_script_markup(value, field="prompt")


class ImageJobResponse(ORMBase):
    id: int
    project_id: int | None
    module: AIGenerationModule
    prompt: str
    parameters: dict | None
    image_type: str
    action: str
    provider: str
    status: AIGenerationStatus
    output_text: str | None
    output_meta: dict | None
    result_url: str | None
    error: str | None
    is_favorite: bool
    parent_generation_id: int | None
    retry_count: int
    created_by_id: int | None
    author_name: str | None = None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None


class ImageQueueResponse(BaseModel):
    queued: list[ImageJobResponse]
    running: list[ImageJobResponse]
    counts: dict[str, int]


class ImageHistoryResponse(BaseModel):
    items: list[ImageJobResponse]
    total: int


class ImageCollectionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    project_id: int | None = None


class ImageCollectionResponse(ORMBase):
    id: int
    name: str
    description: str | None
    project_id: int | None
    item_count: int
    created_at: datetime


class ImageVersionResponse(ORMBase):
    id: int
    generation_id: int
    version: int
    label: str | None
    result_url: str | None
    created_at: datetime


class ImageVariationRequest(BaseModel):
    prompt: str | None = Field(default=None, max_length=10_000)


class ImageSaveAssetResponse(BaseModel):
    asset_id: int
    url: str | None
    folder: str
