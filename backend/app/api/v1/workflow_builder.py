"""Workflow builder & platform API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Header, Query, Request
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_studio_user
from app.core.exceptions import UnauthorizedError
from app.db.session import get_db
from app.middleware.rate_limit import limiter
from app.models import User
from app.schemas.production_pipeline import ProductionPipelineRunResponse
from app.schemas.workflow_builder import (
    WorkflowDashboardResponse,
    WorkflowDefinitionCreate,
    WorkflowDefinitionResponse,
    WorkflowDefinitionUpdate,
    WorkflowExecuteRequest,
    WorkflowExecutionLogsPage,
    WorkflowNodeCatalogResponse,
    WorkflowTriggerCreate,
    WorkflowTriggerResponse,
    WorkflowTriggerUpdate,
    WorkflowVersionCreate,
    WorkflowVersionResponse,
)
from app.services.workflow_builder_service import WorkflowBuilderService
from app.services.workflow_trigger_service import WorkflowTriggerService

router = APIRouter()
_settings = get_settings()


def _resolve_workflow_api_key(
    x_workflow_api_key: str | None,
    authorization: str | None,
) -> str | None:
    if x_workflow_api_key:
        return x_workflow_api_key
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return None


def _require_workflow_event_auth(
    db: Session = Depends(get_db),
    x_workflow_event_key: str | None = Header(None, alias="X-Workflow-Event-Key"),
    x_workflow_api_key: str | None = Header(None, alias="X-Workflow-API-Key"),
    authorization: str | None = Header(None),
) -> None:
    configured = _settings.workflow_event_secret
    if configured and x_workflow_event_key and x_workflow_event_key == configured:
        return
    api_key = _resolve_workflow_api_key(x_workflow_api_key, authorization)
    if api_key:
        WorkflowTriggerService.verify_api_key(db, api_key)
        return
    raise UnauthorizedError("X-Workflow-Event-Key or X-Workflow-API-Key required")


@router.get("/catalog/nodes", response_model=WorkflowNodeCatalogResponse)
def workflow_node_catalog(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return WorkflowBuilderService.node_catalog()


@router.get("/dashboard", response_model=WorkflowDashboardResponse)
def workflow_dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return WorkflowBuilderService.dashboard(db, user)


@router.get("/definitions")
def list_workflow_definitions(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return WorkflowBuilderService.list_definitions(db, user, limit=limit, offset=offset)


@router.get("/templates")
def list_workflow_templates(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return WorkflowBuilderService.list_templates(db, user)


@router.post("/definitions", response_model=WorkflowDefinitionResponse, status_code=201)
def create_workflow_definition(
    data: WorkflowDefinitionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return WorkflowBuilderService.create_definition(db, user, data)


@router.get("/definitions/{definition_id}", response_model=WorkflowDefinitionResponse)
def get_workflow_definition(
    definition_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return WorkflowBuilderService.get_definition(db, user, definition_id)


@router.patch("/definitions/{definition_id}", response_model=WorkflowDefinitionResponse)
def update_workflow_definition(
    definition_id: int,
    data: WorkflowDefinitionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return WorkflowBuilderService.update_definition(db, user, definition_id, data)


@router.delete("/definitions/{definition_id}", status_code=204)
def delete_workflow_definition(
    definition_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    WorkflowBuilderService.delete_definition(db, user, definition_id)


@router.get("/definitions/{definition_id}/versions", response_model=list[WorkflowVersionResponse])
def list_workflow_versions(
    definition_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return WorkflowBuilderService.list_versions(db, user, definition_id)


@router.post("/definitions/{definition_id}/versions", response_model=WorkflowVersionResponse, status_code=201)
def create_workflow_version(
    definition_id: int,
    data: WorkflowVersionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return WorkflowBuilderService.create_version(db, user, definition_id, data)


@router.get("/definitions/{definition_id}/versions/{version_id}", response_model=WorkflowVersionResponse)
def get_workflow_version(
    definition_id: int,
    version_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return WorkflowBuilderService.get_version(db, user, definition_id, version_id)


@router.post("/definitions/{definition_id}/versions/{version_id}/restore", response_model=WorkflowVersionResponse)
def restore_workflow_version(
    definition_id: int,
    version_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return WorkflowBuilderService.restore_version(db, user, definition_id, version_id)


@router.get("/runs/{run_id}/execution-logs", response_model=WorkflowExecutionLogsPage)
def workflow_execution_logs(
    run_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    level: str | None = Query(None),
    node_id: str | None = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    from app.domain.workflow.logs import query_execution_logs
    from app.services.production_pipeline_service import ProductionPipelineService

    ProductionPipelineService.get_run(db, user, run_id)
    items, total = query_execution_logs(db, run_id, level=level, node_id=node_id, limit=limit, offset=offset)
    return {"items": items, "total": total}


@router.post("/definitions/{definition_id}/execute", response_model=ProductionPipelineRunResponse, status_code=201)
def execute_workflow_definition(
    definition_id: int,
    data: WorkflowExecuteRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    run = WorkflowBuilderService.execute_definition(db, user, definition_id, data)
    from app.services.production_pipeline_service import ProductionPipelineService

    return ProductionPipelineService._run_dict(run)


@router.post("/templates/{template_id}/clone", response_model=WorkflowDefinitionResponse, status_code=201)
def clone_workflow_template(
    template_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    name: str | None = Query(None),
):
    return WorkflowBuilderService.clone_template(db, user, template_id, name=name)


@router.get("/definitions/{definition_id}/triggers", response_model=list[WorkflowTriggerResponse])
def list_workflow_triggers(
    definition_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return WorkflowTriggerService.list_triggers(db, user, definition_id)


@router.post("/definitions/{definition_id}/triggers", response_model=WorkflowTriggerResponse, status_code=201)
def create_workflow_trigger(
    definition_id: int,
    data: WorkflowTriggerCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return WorkflowTriggerService.create_trigger(db, user, definition_id, data)


@router.patch("/definitions/{definition_id}/triggers/{trigger_id}", response_model=WorkflowTriggerResponse)
def update_workflow_trigger(
    definition_id: int,
    trigger_id: int,
    data: WorkflowTriggerUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return WorkflowTriggerService.update_trigger(db, user, definition_id, trigger_id, data)


@router.delete("/definitions/{definition_id}/triggers/{trigger_id}", status_code=204)
def delete_workflow_trigger(
    definition_id: int,
    trigger_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    WorkflowTriggerService.delete_trigger(db, user, definition_id, trigger_id)


@router.post("/webhooks/{secret}")
@limiter.limit(_settings.rate_limit_auth)
def workflow_webhook_trigger(
    request: Request,
    secret: str,
    payload: dict[str, Any],
    db: Session = Depends(get_db),
):
    return WorkflowTriggerService.fire_webhook(db, secret, payload)


@router.post("/api/trigger")
@limiter.limit(_settings.rate_limit_auth)
def workflow_api_trigger(
    request: Request,
    payload: dict[str, Any],
    db: Session = Depends(get_db),
    x_workflow_api_key: str | None = Header(None, alias="X-Workflow-API-Key"),
    authorization: str | None = Header(None),
):
    api_key = _resolve_workflow_api_key(x_workflow_api_key, authorization)
    if not api_key:
        raise UnauthorizedError("X-Workflow-API-Key or Bearer token required")
    return WorkflowTriggerService.fire_api(db, api_key, payload)


@router.post("/email/{token}")
@limiter.limit(_settings.rate_limit_auth)
def workflow_email_trigger(
    request: Request,
    token: str,
    payload: dict[str, Any],
    db: Session = Depends(get_db),
):
    return WorkflowTriggerService.fire_email(db, token, payload)


@router.post("/events/{event_name}")
@limiter.limit(_settings.rate_limit_auth)
def workflow_event_trigger(
    request: Request,
    event_name: str,
    payload: dict[str, Any],
    db: Session = Depends(get_db),
    _: None = Depends(_require_workflow_event_auth),
):
    results = WorkflowTriggerService.fire_event(db, event_name, payload)
    return {"fired": len(results), "runs": results}


@router.post("/definitions/{definition_id}/triggers/{trigger_id}/fire")
def fire_workflow_trigger(
    definition_id: int,
    trigger_id: int,
    payload: dict[str, Any],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return WorkflowTriggerService.fire_trigger_by_id(db, user, definition_id, trigger_id, payload)
