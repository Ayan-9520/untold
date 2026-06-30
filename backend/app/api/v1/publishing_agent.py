"""AI Publishing Agent REST API."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_studio_user
from app.db.session import get_db
from app.models import User
from app.schemas.publishing_agent import (
    PublishingAgentAnalyticsResponse,
    PublishingAgentApprovalRequest,
    PublishingAgentCreate,
    PublishingAgentHistoryResponse,
    PublishingAgentOverviewResponse,
    PublishingAgentQueueResponse,
    PublishingAgentRetryRequest,
    PublishingAgentRunResponse,
    WebhookCreate,
    WebhookResponse,
    WebhookUpdate,
)
from app.services.publishing_agent_service import PublishingAgentService
from app.services.publishing_cms_service import PublishingCmsService

router = APIRouter(prefix="/studio/platform/publishing-agent", tags=["AI Publishing Agent"])


@router.get("/overview", response_model=PublishingAgentOverviewResponse)
def agent_overview(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return PublishingAgentService.get_overview(db, user)


@router.post("/dispatch", response_model=PublishingAgentRunResponse, status_code=201)
def dispatch_publish(
    data: PublishingAgentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    run = PublishingAgentService.create_run(db, user, data)
    project = None
    from app.models.studio import Production

    project = db.query(Production).filter(Production.id == run.project_id).first()
    return PublishingAgentService._run_dict(run, project)


@router.get("/queue", response_model=PublishingAgentQueueResponse)
def agent_queue(
    limit: int = Query(default=50, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return PublishingAgentService.get_queue(db, user, limit)


@router.get("/history", response_model=PublishingAgentHistoryResponse)
def agent_history(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return PublishingAgentService.get_history(db, user, limit, offset)


@router.get("/analytics", response_model=PublishingAgentAnalyticsResponse)
def agent_analytics(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return PublishingAgentService.get_analytics(db, user, days)


@router.post("/runs/{run_id}/approve", response_model=PublishingAgentRunResponse)
def approve_run(
    run_id: int,
    data: PublishingAgentApprovalRequest | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return PublishingAgentService.approve_run(db, user, run_id, data.notes if data else None)


@router.post("/runs/{run_id}/reject", response_model=PublishingAgentRunResponse)
def reject_run(
    run_id: int,
    data: PublishingAgentApprovalRequest | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return PublishingAgentService.reject_run(db, user, run_id, data.notes if data else None)


@router.post("/runs/{run_id}/retry", response_model=PublishingAgentRunResponse)
def retry_run(
    run_id: int,
    data: PublishingAgentRetryRequest | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return PublishingAgentService.retry_run(db, user, run_id, data)


@router.post("/jobs/{job_id}/retry")
def retry_single_job(
    job_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return PublishingCmsService.retry_job(db, user, job_id)


@router.get("/webhooks", response_model=list[WebhookResponse])
def list_webhooks(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return PublishingAgentService.list_webhooks(db, user)


@router.post("/webhooks", response_model=WebhookResponse, status_code=201)
def create_webhook(
    data: WebhookCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return PublishingAgentService.create_webhook(db, user, data)


@router.patch("/webhooks/{webhook_id}", response_model=WebhookResponse)
def update_webhook(
    webhook_id: int,
    data: WebhookUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return PublishingAgentService.update_webhook(db, user, webhook_id, data)


@router.delete("/webhooks/{webhook_id}")
def delete_webhook(
    webhook_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return PublishingAgentService.delete_webhook(db, user, webhook_id)
