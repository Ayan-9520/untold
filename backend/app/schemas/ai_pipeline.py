import json
from datetime import datetime

from pydantic import BaseModel, Field


AI_PIPELINE_STEPS = [
    "speech_to_text",
    "script_cleanup",
    "translation",
    "subtitles",
    "dubbing",
    "metadata",
]

STEP_LABELS = {
    "speech_to_text": "Speech-to-Text",
    "script_cleanup": "Script Cleanup",
    "translation": "Translation",
    "subtitles": "Subtitle Generation",
    "dubbing": "AI Dubbing",
    "metadata": "Metadata Localization",
}


class PipelineStepStatus(BaseModel):
    id: str
    label: str
    status: str = "pending"


class LocalizationJobCreate(BaseModel):
    video_id: int | None = None
    video_title: str
    source_language: str = "en"
    target_languages: list[str] = Field(default_factory=lambda: ["hi", "es", "ru", "ar"])
    transcript: str | None = None


class LocalizationJobResponse(BaseModel):
    id: int
    video_id: int | None
    video_title: str
    source_language: str
    target_languages: list[str]
    status: str
    progress: int
    steps: list[PipelineStepStatus]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LocalizationJobListResponse(BaseModel):
    items: list[LocalizationJobResponse]
    total: int


class MembershipStatsResponse(BaseModel):
    total_subscribers: int
    premium_count: int
    vip_count: int
    free_count: int
    mrr: float
    currency: str = "USD"


class SubscriptionAdminResponse(BaseModel):
    id: int
    user_id: int
    user_email: str | None = None
    plan: str
    status: str
    started_at: datetime

    model_config = {"from_attributes": True}
