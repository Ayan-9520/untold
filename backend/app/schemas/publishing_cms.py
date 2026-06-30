"""Publishing CMS Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.studio.enums import PublishPlatform
from app.schemas.common import ORMBase

PUBLISH_PLATFORMS = ("originals", "youtube", "instagram", "facebook", "x", "threads")
VISIBILITY_STATES = ("draft", "published", "archived")
JOB_STATUSES = ("pending_approval", "scheduled", "queued", "processing", "published", "failed", "cancelled")


class PublishingOverview(BaseModel):
    total_jobs: int
    pending_approval: int
    scheduled: int
    failed: int
    published: int
    platform_counts: dict[str, int]
    visibility_counts: dict[str, int]


class PublishingPackageUpdate(BaseModel):
    seo_title: str | None = Field(default=None, max_length=500)
    seo_description: str | None = None
    seo_keywords: list[str] | None = None
    thumbnail_url: str | None = Field(default=None, max_length=1000)
    visibility: str | None = None


class PublishingScheduleRequest(BaseModel):
    platform: PublishPlatform
    scheduled_at: datetime | None = None
    requires_approval: bool = True
    seo_title: str | None = None
    seo_description: str | None = None
    seo_keywords: list[str] | None = None
    thumbnail_url: str | None = None
    meta: dict | None = None


class PublishJobDetail(ORMBase):
    id: int
    project_id: int
    project_title: str | None = None
    platform: str
    scheduled_at: datetime | None
    status: str
    approval_status: str
    published_at: datetime | None
    requires_approval: bool
    retry_count: int
    error_message: str | None
    thumbnail_url: str | None
    seo_title: str | None
    seo_description: str | None
    seo_keywords: list[str] | None
    created_at: datetime


class PublishingWorkspaceResponse(BaseModel):
    project_id: int
    project_title: str
    visibility: str
    publishing_status: str
    seo_title: str | None
    seo_description: str | None
    seo_keywords: list[str] | None
    thumbnail_url: str | None
    jobs: list[PublishJobDetail]
    pending_approvals: int


class ApprovalAction(BaseModel):
    notes: str | None = None
