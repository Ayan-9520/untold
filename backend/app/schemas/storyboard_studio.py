"""Storyboard Studio Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase

SCENE_STATUSES = ("draft", "review", "approved", "locked")


class StoryboardSceneResponse(ORMBase):
    id: int
    project_id: int
    scene_number: int
    sort_order: int
    duration_seconds: int
    narration: str | None
    dialogue: str | None
    camera_angle: str | None
    camera_movement: str | None
    shot_type: str | None
    visual_prompt: str | None
    environment: str | None
    lighting: str | None
    mood: str | None
    transition: str | None
    reference_image_url: str | None
    status: str
    created_at: datetime
    updated_at: datetime | None


class StoryboardSceneCreate(BaseModel):
    scene_number: int | None = None
    duration_seconds: int = Field(default=10, ge=0, le=3600)
    narration: str | None = Field(default=None, max_length=20_000)
    dialogue: str | None = Field(default=None, max_length=20_000)
    camera_angle: str | None = Field(default=None, max_length=120)
    camera_movement: str | None = Field(default=None, max_length=120)
    shot_type: str | None = Field(default=None, max_length=120)
    visual_prompt: str | None = Field(default=None, max_length=10_000)
    environment: str | None = Field(default=None, max_length=200)
    lighting: str | None = Field(default=None, max_length=120)
    mood: str | None = Field(default=None, max_length=120)
    transition: str | None = Field(default=None, max_length=120)
    reference_image_url: str | None = Field(default=None, max_length=2000)
    status: str = "draft"


class StoryboardSceneUpdate(BaseModel):
    scene_number: int | None = Field(default=None, ge=1)
    duration_seconds: int | None = Field(default=None, ge=0, le=3600)
    narration: str | None = Field(default=None, max_length=20_000)
    dialogue: str | None = Field(default=None, max_length=20_000)
    camera_angle: str | None = Field(default=None, max_length=120)
    camera_movement: str | None = Field(default=None, max_length=120)
    shot_type: str | None = Field(default=None, max_length=120)
    visual_prompt: str | None = Field(default=None, max_length=10_000)
    environment: str | None = Field(default=None, max_length=200)
    lighting: str | None = Field(default=None, max_length=120)
    mood: str | None = Field(default=None, max_length=120)
    transition: str | None = Field(default=None, max_length=120)
    reference_image_url: str | None = Field(default=None, max_length=2000)
    status: str | None = None


class StoryboardReorderRequest(BaseModel):
    scene_ids: list[int] = Field(min_length=1)


class StoryboardImportRequest(BaseModel):
    replace_existing: bool = False
    default_duration_seconds: int = Field(default=15, ge=1, le=600)


class StoryboardAIGenerateRequest(BaseModel):
    replace_existing: bool = False
    default_duration_seconds: int = Field(default=15, ge=1, le=600)
    prompt: str | None = Field(default=None, max_length=5000)
    provider: str | None = Field(default=None, max_length=64)


class StoryboardAIGenerateResponse(BaseModel):
    summary: str
    scenes_created: int
    provider: str
    generation_id: int | None = None
    interaction_id: int | None = None


class StoryboardAIHistoryItem(BaseModel):
    id: int
    action: str
    prompt: str
    provider: str
    generation_id: int | None = None
    scenes_created: int
    summary: str
    created_at: datetime


class StoryboardProviderInfo(BaseModel):
    id: str
    label: str
    available: bool


class StoryboardApprovalRequest(BaseModel):
    notes: str | None = Field(default=None, max_length=2000)


class StoryboardApprovalResponse(ORMBase):
    id: int
    status: str
    notes: str | None
    requested_by_id: int
    approver_id: int | None
    created_at: datetime
    resolved_at: datetime | None


class StoryboardRevisionResponse(ORMBase):
    id: int
    project_id: int
    version: int
    label: str | None
    scene_count: int
    created_by_id: int
    author_name: str | None = None
    created_at: datetime


class StoryboardRevisionSave(BaseModel):
    label: str | None = Field(default=None, max_length=300)


class StoryboardWorkspaceResponse(BaseModel):
    project_id: int
    project_title: str
    scene_count: int
    total_duration_seconds: int
    has_script: bool = False
    approval_status: str = "draft"
    scenes: list[StoryboardSceneResponse]
    revisions: list[StoryboardRevisionResponse]
    ai_history: list[StoryboardAIHistoryItem] = []
    providers: list[StoryboardProviderInfo] = []
    approval: StoryboardApprovalResponse | None = None
