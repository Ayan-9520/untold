"""Publishing CMS REST API."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_studio_user
from app.db.session import get_db
from app.models import User
from app.schemas.publishing_cms import (
    ApprovalAction,
    PublishJobDetail,
    PublishingOverview,
    PublishingPackageUpdate,
    PublishingScheduleRequest,
    PublishingWorkspaceResponse,
)
from app.services.publishing_cms_service import PublishingCmsService

router = APIRouter(prefix="/studio/platform/publishing", tags=["Publishing CMS"])


@router.get("/overview", response_model=PublishingOverview)
def publishing_overview(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return PublishingCmsService.get_overview(db, user)


@router.get("/queue", response_model=list[PublishJobDetail])
def publishing_queue(
    status: str | None = None,
    platform: str | None = None,
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return PublishingCmsService.list_queue(db, user, status=status, platform=platform, limit=limit)


@router.get("/projects/{project_id}", response_model=PublishingWorkspaceResponse)
def get_publishing_workspace(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return PublishingCmsService.get_workspace(db, user, project_id)


@router.put("/projects/{project_id}", response_model=PublishingWorkspaceResponse)
def update_publishing_package(
    project_id: int,
    data: PublishingPackageUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return PublishingCmsService.update_package(db, user, project_id, data)


@router.post("/projects/{project_id}/schedule", response_model=PublishJobDetail, status_code=201)
def schedule_publish(
    project_id: int,
    data: PublishingScheduleRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return PublishingCmsService.schedule(db, user, project_id, data)


@router.post("/jobs/{job_id}/approve", response_model=PublishJobDetail)
def approve_publish_job(
    job_id: int,
    data: ApprovalAction | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return PublishingCmsService.approve_job(db, user, job_id, data.notes if data else None)


@router.post("/jobs/{job_id}/reject", response_model=PublishJobDetail)
def reject_publish_job(
    job_id: int,
    data: ApprovalAction | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return PublishingCmsService.reject_job(db, user, job_id, data.notes if data else None)


@router.post("/jobs/{job_id}/retry", response_model=PublishJobDetail)
def retry_publish_job(
    job_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return PublishingCmsService.retry_job(db, user, job_id)
