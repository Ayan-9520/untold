"""Workflow builder service — definitions, versions, templates, execution."""

from __future__ import annotations

import secrets
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.domain.workflow.default_graph import SYSTEM_TEMPLATES, documentary_pipeline_graph
from app.domain.workflow.graph import WorkflowGraph
from app.domain.workflow.logs import append_log
from app.domain.workflow.nodes import NODE_CATALOG
from app.domain.workflow.prompts import merge_prompts
from app.models import User
from app.models.studio_platform import (
    ProductionPipelineRun,
    WorkflowDefinition,
    WorkflowDefinitionVersion,
    WorkflowTrigger,
)
from app.schemas.workflow_builder import (
    WorkflowDefinitionCreate,
    WorkflowDefinitionUpdate,
    WorkflowExecuteRequest,
    WorkflowGraphSchema,
    WorkflowVersionCreate,
)
from app.services.production_pipeline_service import ProductionPipelineService
from app.services.studio_platform_service import StudioPlatformService


class WorkflowBuilderService:
    @staticmethod
    def ensure_system_templates(db: Session) -> None:
        existing = db.query(WorkflowDefinition).filter(WorkflowDefinition.is_system.is_(True)).count()
        if existing:
            return
        for tpl in SYSTEM_TEMPLATES:
            defn = WorkflowDefinition(
                name=tpl["name"],
                description=tpl["description"],
                is_template=True,
                is_system=True,
                status="published",
            )
            db.add(defn)
            db.flush()
            version = WorkflowDefinitionVersion(
                definition_id=defn.id,
                version=1,
                graph=tpl["graph"],
                changelog="Initial system template",
            )
            db.add(version)
            db.flush()
            defn.current_version_id = version.id
        db.commit()

    @staticmethod
    def _definition_dict(defn: WorkflowDefinition, *, include_version: bool = True) -> dict:
        current = None
        if include_version and defn.current_version_id:
            for v in defn.versions or []:
                if v.id == defn.current_version_id:
                    current = WorkflowBuilderService._version_dict(v)
                    break
        return {
            "id": defn.id,
            "name": defn.name,
            "description": defn.description,
            "project_id": defn.project_id,
            "is_template": defn.is_template,
            "is_system": defn.is_system,
            "status": defn.status,
            "current_version_id": defn.current_version_id,
            "created_at": defn.created_at,
            "updated_at": defn.updated_at,
            "current_version": current,
        }

    @staticmethod
    def _version_dict(version: WorkflowDefinitionVersion) -> dict:
        return {
            "id": version.id,
            "definition_id": version.definition_id,
            "version": version.version,
            "graph": version.graph,
            "changelog": version.changelog,
            "created_at": version.created_at,
        }

    @staticmethod
    def node_catalog() -> dict:
        return {"nodes": NODE_CATALOG}

    @staticmethod
    def list_definitions(
        db: Session,
        user: User,
        *,
        templates_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        WorkflowBuilderService.ensure_system_templates(db)
        q = db.query(WorkflowDefinition).options(joinedload(WorkflowDefinition.versions))
        if templates_only:
            q = q.filter(WorkflowDefinition.is_template.is_(True))
        else:
            q = q.filter(WorkflowDefinition.is_template.is_(False))
        total = q.count()
        rows = q.order_by(WorkflowDefinition.updated_at.desc()).offset(offset).limit(limit).all()
        return {
            "items": [WorkflowBuilderService._definition_dict(r) for r in rows],
            "total": total,
        }

    @staticmethod
    def list_templates(db: Session, user: User) -> dict:
        return WorkflowBuilderService.list_definitions(db, user, templates_only=True)

    @staticmethod
    def get_definition(db: Session, user: User, definition_id: int) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        defn = (
            db.query(WorkflowDefinition)
            .options(joinedload(WorkflowDefinition.versions))
            .filter(WorkflowDefinition.id == definition_id)
            .first()
        )
        if not defn:
            raise NotFoundError("Workflow definition")
        return WorkflowBuilderService._definition_dict(defn)

    @staticmethod
    def create_definition(db: Session, user: User, data: WorkflowDefinitionCreate) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        graph_data = data.graph.model_dump() if data.graph else documentary_pipeline_graph()
        graph = WorkflowGraph.from_dict(graph_data)
        errors = graph.validate()
        if errors:
            raise BadRequestError("; ".join(errors))

        defn = WorkflowDefinition(
            name=data.name.strip(),
            description=data.description,
            project_id=data.project_id,
            is_template=data.is_template,
            status="draft",
            created_by_id=user.id,
        )
        db.add(defn)
        db.flush()
        version = WorkflowDefinitionVersion(
            definition_id=defn.id,
            version=1,
            graph=graph.to_dict(),
            changelog="Initial version",
            created_by_id=user.id,
        )
        db.add(version)
        db.flush()
        defn.current_version_id = version.id
        db.commit()
        db.refresh(defn)
        return WorkflowBuilderService.get_definition(db, user, defn.id)

    @staticmethod
    def update_definition(db: Session, user: User, definition_id: int, data: WorkflowDefinitionUpdate) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        defn = db.query(WorkflowDefinition).filter(WorkflowDefinition.id == definition_id).first()
        if not defn:
            raise NotFoundError("Workflow definition")
        if defn.is_system:
            raise ConflictError("System templates cannot be modified")
        if data.name is not None:
            defn.name = data.name.strip()
        if data.description is not None:
            defn.description = data.description
        if data.status is not None:
            defn.status = data.status
        if data.project_id is not None:
            defn.project_id = data.project_id
        db.commit()
        return WorkflowBuilderService.get_definition(db, user, definition_id)

    @staticmethod
    def delete_definition(db: Session, user: User, definition_id: int) -> None:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        defn = db.query(WorkflowDefinition).filter(WorkflowDefinition.id == definition_id).first()
        if not defn:
            raise NotFoundError("Workflow definition")
        if defn.is_system:
            raise ConflictError("System templates cannot be deleted")
        db.delete(defn)
        db.commit()

    @staticmethod
    def create_version(db: Session, user: User, definition_id: int, data: WorkflowVersionCreate) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        defn = db.query(WorkflowDefinition).filter(WorkflowDefinition.id == definition_id).first()
        if not defn:
            raise NotFoundError("Workflow definition")
        graph = WorkflowGraph.from_dict(data.graph.model_dump())
        errors = graph.validate()
        if errors:
            raise BadRequestError("; ".join(errors))

        max_version = (
            db.query(func.max(WorkflowDefinitionVersion.version))
            .filter(WorkflowDefinitionVersion.definition_id == definition_id)
            .scalar()
            or 0
        )
        version = WorkflowDefinitionVersion(
            definition_id=definition_id,
            version=max_version + 1,
            graph=graph.to_dict(),
            changelog=data.changelog,
            created_by_id=user.id,
        )
        db.add(version)
        db.flush()
        defn.current_version_id = version.id
        if defn.status == "draft":
            defn.status = "published"
        db.commit()
        return WorkflowBuilderService._version_dict(version)

    @staticmethod
    def list_versions(db: Session, user: User, definition_id: int) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        rows = (
            db.query(WorkflowDefinitionVersion)
            .filter(WorkflowDefinitionVersion.definition_id == definition_id)
            .order_by(WorkflowDefinitionVersion.version.desc())
            .all()
        )
        return [WorkflowBuilderService._version_dict(v) for v in rows]

    @staticmethod
    def get_version(db: Session, user: User, definition_id: int, version_id: int) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        version = (
            db.query(WorkflowDefinitionVersion)
            .filter(
                WorkflowDefinitionVersion.id == version_id,
                WorkflowDefinitionVersion.definition_id == definition_id,
            )
            .first()
        )
        if not version:
            raise NotFoundError("Workflow version")
        return WorkflowBuilderService._version_dict(version)

    @staticmethod
    def restore_version(db: Session, user: User, definition_id: int, version_id: int) -> dict:
        """Set current version to a historical snapshot (creates new version copy)."""
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        version = (
            db.query(WorkflowDefinitionVersion)
            .filter(
                WorkflowDefinitionVersion.id == version_id,
                WorkflowDefinitionVersion.definition_id == definition_id,
            )
            .first()
        )
        if not version:
            raise NotFoundError("Workflow version")
        from app.schemas.workflow_builder import WorkflowGraphSchema

        return WorkflowBuilderService.create_version(
            db,
            user,
            definition_id,
            WorkflowVersionCreate(
                graph=WorkflowGraphSchema(**version.graph),
                changelog=f"Restored from v{version.version}",
            ),
        )

    @staticmethod
    def clone_template(db: Session, user: User, template_id: int, *, name: str | None = None) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        tpl = db.query(WorkflowDefinition).filter(WorkflowDefinition.id == template_id).first()
        if not tpl or not tpl.is_template:
            raise NotFoundError("Workflow template")
        version = (
            db.query(WorkflowDefinitionVersion)
            .filter(WorkflowDefinitionVersion.id == tpl.current_version_id)
            .first()
        )
        if not version:
            raise BadRequestError("Template has no version")
        return WorkflowBuilderService.create_definition(
            db,
            user,
            WorkflowDefinitionCreate(
                name=name or f"{tpl.name} (copy)",
                description=tpl.description,
                graph=WorkflowGraphSchema(**version.graph),
                is_template=False,
            ),
        )

    @staticmethod
    def execute_definition(
        db: Session,
        user: User | None,
        definition_id: int,
        data: WorkflowExecuteRequest,
        *,
        trigger: WorkflowTrigger | None = None,
    ) -> ProductionPipelineRun:
        if user:
            StudioPlatformService.require_permission(db, user, data.project_id, "ai.generate")

        defn = db.query(WorkflowDefinition).filter(WorkflowDefinition.id == definition_id).first()
        if not defn:
            raise NotFoundError("Workflow definition")

        version_id = data.version_id or defn.current_version_id
        version = (
            db.query(WorkflowDefinitionVersion)
            .filter(WorkflowDefinitionVersion.id == version_id, WorkflowDefinitionVersion.definition_id == definition_id)
            .first()
        )
        if not version:
            raise NotFoundError("Workflow version")

        graph = WorkflowGraph.from_dict(version.graph)
        errors = graph.validate()
        if errors:
            raise BadRequestError("; ".join(errors))

        prompt_overrides = data.prompts or {}
        merged_prompts = merge_prompts(prompt_overrides)
        requires_approval = data.requires_approval
        status = "scheduled" if data.scheduled_at else ("pending_approval" if requires_approval else "queued")
        approval_status = "pending" if requires_approval else "none"

        run = ProductionPipelineRun(
            project_id=data.project_id,
            topic=data.topic.strip(),
            status=status,
            requires_approval=requires_approval,
            approval_status=approval_status,
            progress=0,
            retry_count=0,
            workflow_definition_id=definition_id,
            workflow_version_id=version.id,
            workflow_trigger_id=trigger.id if trigger else None,
            trigger_type=trigger.trigger_type if trigger else data.trigger_type,
            graph_snapshot=version.graph,
            node_executions=None,
            scheduled_at=data.scheduled_at,
            output_meta={
                "providers": data.providers,
                "publish_platforms": data.publish_platforms,
                "prompts": merged_prompts,
                "translation_language": data.translation_language,
                "logs": [],
                "workflow_definition_id": definition_id,
                "workflow_version": version.version,
            },
            created_by_id=user.id if user else (trigger.created_by_id if trigger else None),
        )
        db.add(run)
        db.flush()
        append_log(db, run.id, f"Workflow run created from definition #{definition_id} v{version.version}", level="info")

        if data.scheduled_at:
            append_log(db, run.id, f"Scheduled for {data.scheduled_at.isoformat()}", level="info")
        elif requires_approval:
            append_log(db, run.id, "Awaiting approval before run", level="warn")
        elif data.auto_run:
            ProductionPipelineService._dispatch(db, run, user.id if user else None)

        db.commit()
        db.refresh(run)
        return run

    @staticmethod
    def dashboard(db: Session, user: User) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        WorkflowBuilderService.ensure_system_templates(db)
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        total_definitions = db.query(WorkflowDefinition).filter(WorkflowDefinition.is_template.is_(False)).count()
        total_templates = db.query(WorkflowDefinition).filter(WorkflowDefinition.is_template.is_(True)).count()
        runs_today = (
            db.query(ProductionPipelineRun).filter(ProductionPipelineRun.created_at >= today_start).count()
        )
        runs_active = (
            db.query(ProductionPipelineRun)
            .filter(ProductionPipelineRun.status.in_(["queued", "running", "pending_approval", "scheduled"]))
            .count()
        )
        runs_completed = db.query(ProductionPipelineRun).filter(ProductionPipelineRun.status == "completed").count()
        runs_failed = db.query(ProductionPipelineRun).filter(ProductionPipelineRun.status == "failed").count()
        recent = (
            db.query(ProductionPipelineRun)
            .order_by(ProductionPipelineRun.created_at.desc())
            .limit(12)
            .all()
        )
        return {
            "total_definitions": total_definitions,
            "total_templates": total_templates,
            "runs_today": runs_today,
            "runs_active": runs_active,
            "runs_completed": runs_completed,
            "runs_failed": runs_failed,
            "recent_runs": [ProductionPipelineService._run_dict(r) for r in recent],
        }
