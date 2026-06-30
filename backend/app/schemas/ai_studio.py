"""AI Studio Pydantic schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.domain.studio.enums import AIGenerationModule, AIGenerationStatus
from app.domain.security.sanitization import reject_script_markup
from app.schemas.common import ORMBase

AI_MODULE_IDS = (
    "research",
    "script",
    "image",
    "video",
    "voice",
    "music",
    "thumbnail",
    "seo",
    "translation",
)


class AIProviderResponse(BaseModel):
    id: str
    label: str
    available: bool
    modules: list[str]


class AIModuleInfo(BaseModel):
    id: str
    label: str
    description: str
    output_type: Literal["text", "media"] = "text"


class AIGenerationJobResponse(ORMBase):
    id: int
    project_id: int | None
    project_title: str | None = None
    module: AIGenerationModule
    prompt: str
    parameters: dict | None
    provider: str
    status: AIGenerationStatus
    output_text: str | None
    output_meta: dict | None
    result_url: str | None
    error: str | None
    retry_count: int
    model: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int | None = None
    cost_usd: float | None = None
    failure_count: int = 0
    retries: int = 0
    approval_status: str = "none"
    prompt_version: str | None = None
    temperature: float | None = None
    created_by_id: int | None
    author_name: str | None = None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None


class AIGenerationCreate(BaseModel):
    module: AIGenerationModule
    prompt: str = Field(min_length=1, max_length=50_000)
    parameters: dict | None = None
    project_id: int | None = None
    provider: str | None = Field(default=None, max_length=64)

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, value: str) -> str:
        return reject_script_markup(value, field="prompt")


class AIQueueResponse(BaseModel):
    queued: list[AIGenerationJobResponse]
    running: list[AIGenerationJobResponse]
    counts: dict[str, int]


class AIHistoryResponse(BaseModel):
    items: list[AIGenerationJobResponse]
    total: int


class AITelemetryTotals(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0
    failures: int = 0
    retries: int = 0


class AITelemetryResponse(BaseModel):
    items: list[AIGenerationJobResponse]
    total: int
    totals: AITelemetryTotals


class AIPromptResponse(ORMBase):
    id: int
    title: str
    module: str
    prompt_template: str
    description: str | None
    parameters: dict | None
    tags: list[str]
    is_public: bool
    created_by_id: int | None
    author_name: str | None = None
    created_at: datetime
    updated_at: datetime | None


class AIPromptCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    module: str = Field(min_length=1, max_length=64)
    prompt_template: str = Field(min_length=1, max_length=50_000)
    description: str | None = Field(default=None, max_length=2000)
    parameters: dict | None = None
    tags: list[str] = Field(default_factory=list)
    is_public: bool = True


class AIPromptUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=300)
    prompt_template: str | None = Field(default=None, max_length=50_000)
    description: str | None = None
    parameters: dict | None = None
    tags: list[str] | None = None
    is_public: bool | None = None


class AIStudioOverviewResponse(BaseModel):
    modules: list[AIModuleInfo]
    providers: list[AIProviderResponse]
    queue_counts: dict[str, int]
