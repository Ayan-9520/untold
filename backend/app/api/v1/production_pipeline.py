"""Production pipeline & Workflow Engine REST API."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_studio_user
from app.db.session import get_db
from app.models import User
from app.schemas.production_pipeline import (
    ProductionPipelineCreate,
    ProductionPipelineOverviewResponse,
    ProductionPipelineRunResponse,
    WorkflowApprovalRequest,
    WorkflowHistoryResponse,
    WorkflowLogsResponse,
    WorkflowPromptsResponse,
    WorkflowStatusResponse,
)
from app.services.production_pipeline_service import ProductionPipelineService

router = APIRouter(prefix="/studio/platform/production-pipeline", tags=["Production Pipeline"])


@router.get("/overview", response_model=ProductionPipelineOverviewResponse)
def pipeline_overview(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return ProductionPipelineService.get_overview(db, user)


@router.get("/prompts", response_model=WorkflowPromptsResponse)
def workflow_prompts(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return ProductionPipelineService.get_prompts(db, user)


@router.get("/runs", response_model=list[ProductionPipelineRunResponse])
def list_pipeline_runs(
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return ProductionPipelineService.list_runs(db, user, limit=limit)


@router.get("/history", response_model=WorkflowHistoryResponse)
def workflow_history(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return ProductionPipelineService.history(db, user, limit=limit, offset=offset)


@router.post("/runs", response_model=ProductionPipelineRunResponse, status_code=201)
def start_pipeline(
    data: ProductionPipelineCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    run = ProductionPipelineService.create_run(db, user, data)
    return ProductionPipelineService.get_run(db, user, run.id)


@router.get("/runs/{run_id}", response_model=ProductionPipelineRunResponse)
def get_pipeline_run(
    run_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return ProductionPipelineService.get_run(db, user, run_id)


@router.get("/runs/{run_id}/status", response_model=WorkflowStatusResponse)
def workflow_status(
    run_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return ProductionPipelineService.status(db, user, run_id)


@router.get("/runs/{run_id}/logs", response_model=WorkflowLogsResponse)
def workflow_logs(
    run_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return ProductionPipelineService.logs(db, user, run_id)


@router.post("/runs/{run_id}/run", response_model=ProductionPipelineRunResponse)
def workflow_run(
    run_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    ProductionPipelineService.run(db, user, run_id)
    return ProductionPipelineService.get_run(db, user, run_id)


@router.post("/runs/{run_id}/cancel", response_model=ProductionPipelineRunResponse)
def cancel_pipeline_run(
    run_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    ProductionPipelineService.cancel_run(db, user, run_id)
    return ProductionPipelineService.get_run(db, user, run_id)


@router.post("/runs/{run_id}/retry", response_model=ProductionPipelineRunResponse)
def retry_pipeline_run(
    run_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    ProductionPipelineService.retry_run(db, user, run_id)
    return ProductionPipelineService.get_run(db, user, run_id)


@router.post("/runs/{run_id}/approve", response_model=ProductionPipelineRunResponse)
def approve_pipeline_run(
    run_id: int,
    data: WorkflowApprovalRequest | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    ProductionPipelineService.approve_run(db, user, run_id, data.notes if data else None)
    return ProductionPipelineService.get_run(db, user, run_id)


@router.post("/runs/{run_id}/reject", response_model=ProductionPipelineRunResponse)
def reject_pipeline_run(
    run_id: int,
    data: WorkflowApprovalRequest | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    ProductionPipelineService.reject_run(db, user, run_id, data.notes if data else None)
    return ProductionPipelineService.get_run(db, user, run_id)
