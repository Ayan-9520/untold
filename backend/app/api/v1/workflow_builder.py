"""Workflow builder & platform API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_studio_user
from app.db.session import get_db
from app.models import User
from app.schemas.production_pipeline import ProductionPipelineRunResponse
from app.schemas.workflow_builder import (
    WorkflowDashboardResponse,
    WorkflowDefinitionCreate,
    WorkflowDefinitionResponse,
    WorkflowDefinitionUpdate,
    WorkflowExecuteRequest,
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
def workflow_webhook_trigger(secret: str, payload: dict[str, Any], db: Session = Depends(get_db)):
    return WorkflowTriggerService.fire_webhook(db, secret, payload)
