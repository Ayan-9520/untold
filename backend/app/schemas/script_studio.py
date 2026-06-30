"""Script Studio Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.studio.enums import ScriptStyle
from app.schemas.common import ORMBase


class ScriptWorkspaceResponse(ORMBase):
    id: int
    project_id: int
    project_title: str | None = None
    title: str
    status: str
    content: str
    style: ScriptStyle
    content_version: int
    current_version: int
    last_auto_saved_at: datetime | None
    last_edited_by_id: int | None
    last_edited_by_name: str | None = None
    approved_at: datetime | None
    active_collaborators: list[dict] = []
    created_at: datetime
    updated_at: datetime | None


class ScriptWorkspaceAutoSave(BaseModel):
    content: str = Field(max_length=500_000)
    style: ScriptStyle | None = None
    expected_version: int | None = None


class ScriptCollaboratorHeartbeat(BaseModel):
    pass


class ScriptCommentResponse(ORMBase):
    id: int
    user_id: int
    author_name: str | None = None
    content: str
    created_at: datetime


class ScriptCommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=10_000)


class ScriptVersionResponse(ORMBase):
    id: int
    version: int
    content: str
    style: ScriptStyle
    snapshot_label: str | None
    created_by_id: int
    author_name: str | None = None
    created_at: datetime


class ScriptVersionSave(BaseModel):
    snapshot_label: str | None = Field(default=None, max_length=200)


class ScriptApprovalRequest(BaseModel):
    notes: str | None = Field(default=None, max_length=2000)


class ScriptApprovalResponse(ORMBase):
    id: int
    status: str
    notes: str | None
    requested_by_id: int
    approver_id: int | None
    created_at: datetime
    resolved_at: datetime | None


class ScriptAIRequest(BaseModel):
    action: str = Field(default="generate", max_length=64)
    prompt: str | None = Field(default=None, max_length=10_000)
    selection: str | None = Field(default=None, max_length=50_000)
    target_language: str | None = Field(default="es", max_length=16)
    tone: str | None = Field(default=None, max_length=64)
    provider: str | None = Field(default=None, max_length=64)
    apply: bool = False


class ScriptAIResponse(BaseModel):
    result: str
    action: str
    generation_id: int | None = None
    interaction_id: int | None = None
    provider: str | None = None
    suggested_style: str | None = None
    applied: bool = False


class ScriptAIHistoryItem(BaseModel):
    id: int
    action: str
    prompt: str
    provider: str
    generation_id: int | None = None
    result_preview: str
    created_at: datetime


class ScriptProviderInfo(BaseModel):
    id: str
    label: str
    available: bool


class ScriptFullResponse(BaseModel):
    workspace: ScriptWorkspaceResponse
    versions: list[ScriptVersionResponse]
    comments: list[ScriptCommentResponse]
    approval: ScriptApprovalResponse | None = None
    ai_history: list[ScriptAIHistoryItem] = []
    providers: list[ScriptProviderInfo] = []
