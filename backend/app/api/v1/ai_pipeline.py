import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin
from app.db.session import get_db
from app.models import User
from app.schemas.ai_pipeline import (
    LocalizationJobCreate,
    LocalizationJobListResponse,
    LocalizationJobResponse,
    MembershipStatsResponse,
    SubscriptionAdminResponse,
    SubscriptionAdminUpdate,
)
from app.schemas.common import PaginatedResponse
from app.services.ai_pipeline_service import AIPipelineService, MembershipAdminService

router = APIRouter(prefix="/admin", tags=["Admin — AI & Membership"])


@router.get("/ai/jobs", response_model=LocalizationJobListResponse)
def list_localization_jobs(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    items, total = AIPipelineService.list_jobs(db, limit=limit)
    return LocalizationJobListResponse(items=items, total=total)


@router.get("/ai/jobs/{job_id}", response_model=LocalizationJobResponse)
def get_localization_job(
    job_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    job = AIPipelineService.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Localization job not found")
    return job


@router.post("/ai/jobs", response_model=LocalizationJobResponse, status_code=201)
def create_localization_job(
    data: LocalizationJobCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return AIPipelineService.create_job(db, data)


@router.post("/ai/jobs/{job_id}/process", response_model=LocalizationJobResponse)
def process_localization_job(
    job_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    job = AIPipelineService.process_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Localization job not found")
    return job


@router.get("/membership/stats", response_model=MembershipStatsResponse)
def membership_stats(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return MembershipAdminService.get_stats(db)


@router.get("/membership/subscriptions", response_model=PaginatedResponse[SubscriptionAdminResponse])
def list_subscriptions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    items, total = MembershipAdminService.list_subscriptions(db, skip=(page - 1) * page_size, limit=page_size)
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.patch("/membership/subscriptions/{sub_id}", response_model=SubscriptionAdminResponse)
def update_subscription(
    sub_id: int,
    data: SubscriptionAdminUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    updated = MembershipAdminService.update_subscription(db, sub_id, data.plan, data.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return updated
