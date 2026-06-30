"""Workflow Engine service — run(), cancel(), retry(), approve(), reject(), history(), status(), logs()."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.domain.workflow.engine import WorkflowEngine
from app.domain.workflow.logs import append_log, get_logs
from app.domain.workflow.prompts import merge_prompts, prompt_catalog
from app.domain.workflow.steps import WORKFLOW_AGENTS
from app.models import User
from app.models.studio_platform import ProductionPipelineRun
from app.schemas.production_pipeline import ProductionPipelineCreate
from app.services.studio_platform_service import StudioPlatformService


class ProductionPipelineService:
    @staticmethod
    def _run_dict(run: ProductionPipelineRun) -> dict:
        stages = run.stages or WorkflowEngine.initial_stages()
        return {
            "id": run.id,
            "project_id": run.project_id,
            "topic": run.topic,
            "status": run.status,
            "requires_approval": bool(run.requires_approval),
            "approval_status": run.approval_status or "none",
            "retry_count": run.retry_count or 0,
            "current_stage": run.current_stage,
            "progress": run.progress or 0,
            "stages": stages,
            "output_meta": run.output_meta,
            "error_message": run.error_message,
            "created_by_id": run.created_by_id,
            "started_at": run.started_at,
            "completed_at": run.completed_at,
            "created_at": run.created_at,
            "workflow_definition_id": run.workflow_definition_id,
            "workflow_version_id": run.workflow_version_id,
            "trigger_type": run.trigger_type,
            "graph_snapshot": run.graph_snapshot,
            "node_executions": run.node_executions,
            "scheduled_at": run.scheduled_at,
        }

    @staticmethod
    def _get_run_row(db: Session, run_id: int) -> ProductionPipelineRun:
        run = db.query(ProductionPipelineRun).filter(ProductionPipelineRun.id == run_id).first()
        if not run:
            raise NotFoundError("Workflow run")
        return run

    @staticmethod
    def _dispatch(db: Session, run: ProductionPipelineRun, user_id: int | None) -> None:
        from app.workers.studio_tasks import run_production_pipeline

        task = run_production_pipeline.delay(run.id)
        run.celery_task_id = task.id
        if run.status != "running":
            run.status = "queued"
        append_log(db, run.id, "Workflow dispatched to worker", level="info")
        StudioPlatformService.log_activity(
            db, user_id, "workflow.started", run.project_id, "workflow_engine", run.id
        )
        db.flush()

    @staticmethod
    def get_overview(db: Session, user: User) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        recent = (
            db.query(ProductionPipelineRun)
            .filter(ProductionPipelineRun.created_by_id == user.id)
            .order_by(ProductionPipelineRun.created_at.desc())
            .limit(10)
            .all()
        )
        return {
            "engine": {"id": "workflow", "label": "Workflow Engine"},
            "steps": WORKFLOW_AGENTS,
            "prompts": prompt_catalog(),
            "recent_runs": [ProductionPipelineService._run_dict(r) for r in recent],
        }

    @staticmethod
    def get_prompts(db: Session, user: User) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        return {"prompts": prompt_catalog()}

    @staticmethod
    def create_run(db: Session, user: User, data: ProductionPipelineCreate) -> ProductionPipelineRun:
        if data.project_id:
            StudioPlatformService.require_permission(db, user, data.project_id, "ai.generate")
        else:
            StudioPlatformService.require_permission(db, user, None, "ai.generate")

        requires_approval = data.requires_approval
        status = "pending_approval" if requires_approval else "queued"
        approval_status = "pending" if requires_approval else "none"
        prompt_overrides = data.prompts.model_dump(exclude_none=True) if data.prompts else {}
        merged_prompts = merge_prompts(prompt_overrides)

        run = ProductionPipelineRun(
            project_id=data.project_id,
            topic=data.topic.strip(),
            status=status,
            requires_approval=requires_approval,
            approval_status=approval_status,
            progress=0,
            retry_count=0,
            stages=WorkflowEngine.initial_stages(),
            output_meta={
                "providers": {
                    "research": data.research_provider,
                    "script": data.script_provider,
                    "storyboard": data.storyboard_provider,
                    "image": data.image_provider,
                    "voice": data.voice_provider,
                    "video": data.video_provider,
                    "music": data.music_provider,
                    "translation": data.translation_provider,
                    "seo": data.seo_provider,
                    "publisher": data.publisher_provider,
                },
                "publish_platforms": data.publish_platforms or ["originals", "youtube"],
                "prompts": merged_prompts,
                "translation_language": data.translation_language,
                "logs": [],
            },
            created_by_id=user.id,
        )
        db.add(run)
        db.flush()
        append_log(db, run.id, f"Workflow created for topic: {run.topic[:120]}", level="info")

        if requires_approval:
            append_log(db, run.id, "Awaiting approval before run", level="warn")
        elif data.auto_run:
            ProductionPipelineService._dispatch(db, run, user.id)

        StudioPlatformService.log_activity(
            db, user.id, "workflow.queued", data.project_id, "workflow_engine", run.id
        )
        db.commit()
        db.refresh(run)
        return run

    @staticmethod
    def run(db: Session, user: User, run_id: int) -> ProductionPipelineRun:
        """Start or resume workflow execution."""
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        run = ProductionPipelineService._get_run_row(db, run_id)

        if run.requires_approval and run.approval_status != "approved":
            raise ConflictError("Workflow requires approval before run")

        if run.status == "running":
            raise ConflictError("Workflow is already running")

        if run.status not in ("queued", "pending_approval", "failed", "cancelled", "scheduled"):
            if run.status == "completed":
                raise ConflictError("Workflow already completed — use retry to run again")
            raise ConflictError(f"Cannot run workflow in status: {run.status}")

        if run.status in ("failed", "cancelled"):
            run.stages = WorkflowEngine.initial_stages()
            run.progress = 0
            run.current_stage = None
            run.error_message = None
            run.completed_at = None

        run.status = "queued"
        append_log(db, run.id, "Workflow run requested", level="info")
        ProductionPipelineService._dispatch(db, run, user.id)
        db.commit()
        db.refresh(run)
        return run

    @staticmethod
    def cancel_run(db: Session, user: User, run_id: int) -> ProductionPipelineRun:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        run = ProductionPipelineService._get_run_row(db, run_id)
        if run.status not in ("queued", "running", "pending_approval"):
            raise ConflictError("Only queued, running, or pending workflows can be cancelled")
        run.status = "cancelled"
        run.completed_at = datetime.now(timezone.utc)
        append_log(db, run.id, "Workflow cancelled", level="warn")
        if run.celery_task_id:
            try:
                from app.workers.celery_app import celery_app

                celery_app.control.revoke(run.celery_task_id, terminate=True)
            except Exception:
                pass
        db.commit()
        db.refresh(run)
        return run

    @staticmethod
    def retry_run(db: Session, user: User, run_id: int) -> ProductionPipelineRun:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        run = ProductionPipelineService._get_run_row(db, run_id)
        if run.status not in ("failed", "cancelled", "completed"):
            raise ConflictError("Only failed, cancelled, or completed workflows can be retried")

        if run.requires_approval and run.approval_status == "rejected":
            raise ConflictError("Rejected workflows cannot be retried — create a new run")

        run.retry_count = (run.retry_count or 0) + 1
        run.status = "queued"
        run.approval_status = "approved" if run.requires_approval else run.approval_status
        run.error_message = None
        run.progress = 0
        run.current_stage = None
        run.started_at = None
        run.completed_at = None
        run.stages = WorkflowEngine.initial_stages()
        append_log(db, run.id, f"Workflow retry #{run.retry_count}", level="info")
        ProductionPipelineService._dispatch(db, run, user.id)
        db.commit()
        db.refresh(run)
        return run

    @staticmethod
    def approve_run(db: Session, user: User, run_id: int, notes: str | None = None) -> ProductionPipelineRun:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        run = ProductionPipelineService._get_run_row(db, run_id)
        if not run.requires_approval:
            raise BadRequestError("This workflow does not require approval")
        if run.approval_status != "pending":
            raise ConflictError("Workflow is not pending approval")

        run.approval_status = "approved"
        run.status = "queued"
        meta = dict(run.output_meta or {})
        pending_node = meta.get("pending_node_id")
        if pending_node and run.graph_snapshot:
            node_executions = dict(run.node_executions or {})
            if pending_node in node_executions:
                node_executions[pending_node] = {
                    **node_executions[pending_node],
                    "status": "completed",
                }
            run.node_executions = node_executions
            meta["resume_after_node"] = pending_node
            meta.pop("pending_node_id", None)
            run.output_meta = meta
        msg = "Workflow approved"
        if notes:
            meta = dict(run.output_meta or {})
            meta["approval_notes"] = notes
            run.output_meta = meta
            msg = f"{msg}: {notes[:200]}"
        append_log(db, run.id, msg, level="info")
        ProductionPipelineService._dispatch(db, run, user.id)
        db.commit()
        db.refresh(run)
        return run

    @staticmethod
    def reject_run(db: Session, user: User, run_id: int, notes: str | None = None) -> ProductionPipelineRun:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        run = ProductionPipelineService._get_run_row(db, run_id)
        if not run.requires_approval:
            raise BadRequestError("This workflow does not require approval")
        if run.approval_status != "pending":
            raise ConflictError("Workflow is not pending approval")

        run.approval_status = "rejected"
        run.status = "cancelled"
        run.error_message = notes or "Rejected by approver"
        run.completed_at = datetime.now(timezone.utc)
        append_log(db, run.id, run.error_message, level="error")
        db.commit()
        db.refresh(run)
        return run

    @staticmethod
    def get_run(db: Session, user: User, run_id: int) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        return ProductionPipelineService._run_dict(ProductionPipelineService._get_run_row(db, run_id))

    @staticmethod
    def status(db: Session, user: User, run_id: int) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        run = ProductionPipelineService._get_run_row(db, run_id)
        return {
            "id": run.id,
            "status": run.status,
            "approval_status": run.approval_status or "none",
            "current_stage": run.current_stage,
            "progress": run.progress or 0,
            "retry_count": run.retry_count or 0,
            "error_message": run.error_message,
        }

    @staticmethod
    def history(db: Session, user: User, *, limit: int = 50, offset: int = 0) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        q = db.query(ProductionPipelineRun).order_by(ProductionPipelineRun.created_at.desc())
        total = q.count()
        rows = q.offset(offset).limit(limit).all()
        return {
            "items": [ProductionPipelineService._run_dict(r) for r in rows],
            "total": total,
        }

    @staticmethod
    def list_runs(db: Session, user: User, limit: int = 20) -> list[dict]:
        result = ProductionPipelineService.history(db, user, limit=limit, offset=0)
        return result["items"]

    @staticmethod
    def logs(db: Session, user: User, run_id: int) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        run = ProductionPipelineService._get_run_row(db, run_id)
        return {"run_id": run.id, "logs": get_logs(run)}

    @staticmethod
    def execute_run(db: Session, run_id: int) -> None:
        run = ProductionPipelineService._get_run_row(db, run_id)
        if run.requires_approval and run.approval_status != "approved":
            append_log(db, run.id, "Execution blocked — approval required", level="error")
            db.commit()
            return
        append_log(db, run.id, "Workflow execution started", level="info")
        db.commit()
        if run.graph_snapshot:
            from app.domain.workflow.executor import GraphExecutor

            GraphExecutor.execute_run(db, run_id)
        else:
            WorkflowEngine.execute_run(db, run_id)
