"""Workflow Engine REST API (alias for production pipeline)."""

from fastapi import APIRouter

from app.api.v1 import production_pipeline, workflow_builder
from app.schemas.production_pipeline import (
    ProductionPipelineOverviewResponse,
    ProductionPipelineRunResponse,
    WorkflowHistoryResponse,
    WorkflowLogsResponse,
    WorkflowPromptsResponse,
    WorkflowStatusResponse,
)

router = APIRouter(prefix="/studio/platform/workflow-engine", tags=["Workflow Engine"])

router.add_api_route("/overview", production_pipeline.pipeline_overview, methods=["GET"], response_model=ProductionPipelineOverviewResponse)
router.add_api_route("/prompts", production_pipeline.workflow_prompts, methods=["GET"], response_model=WorkflowPromptsResponse)
router.add_api_route("/history", production_pipeline.workflow_history, methods=["GET"], response_model=WorkflowHistoryResponse)
router.add_api_route("/runs", production_pipeline.list_pipeline_runs, methods=["GET"], response_model=list[ProductionPipelineRunResponse])
router.add_api_route("/runs", production_pipeline.start_pipeline, methods=["POST"], response_model=ProductionPipelineRunResponse, status_code=201)
router.add_api_route("/runs/{run_id}", production_pipeline.get_pipeline_run, methods=["GET"], response_model=ProductionPipelineRunResponse)
router.add_api_route("/runs/{run_id}/status", production_pipeline.workflow_status, methods=["GET"], response_model=WorkflowStatusResponse)
router.add_api_route("/runs/{run_id}/logs", production_pipeline.workflow_logs, methods=["GET"], response_model=WorkflowLogsResponse)
router.add_api_route("/runs/{run_id}/run", production_pipeline.workflow_run, methods=["POST"], response_model=ProductionPipelineRunResponse)
router.add_api_route("/runs/{run_id}/cancel", production_pipeline.cancel_pipeline_run, methods=["POST"], response_model=ProductionPipelineRunResponse)
router.add_api_route("/runs/{run_id}/retry", production_pipeline.retry_pipeline_run, methods=["POST"], response_model=ProductionPipelineRunResponse)
router.add_api_route("/runs/{run_id}/approve", production_pipeline.approve_pipeline_run, methods=["POST"], response_model=ProductionPipelineRunResponse)
router.add_api_route("/runs/{run_id}/reject", production_pipeline.reject_pipeline_run, methods=["POST"], response_model=ProductionPipelineRunResponse)

router.include_router(workflow_builder.router)
