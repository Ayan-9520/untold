"""AI SEO Studio — multi-variant metadata, scoring, approval."""

from __future__ import annotations

import time
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.domain.seo.providers.registry import get_seo_registry
from app.domain.seo.types import CONTENT_TYPES, SEOGenerateRequest
from app.domain.studio.enums import AIGenerationModule, AIGenerationStatus, ApprovalStatus
from app.models import User
from app.models.studio_platform import AIGeneration, AISEOVariant, StudioApproval, StudioNotification
from app.schemas.seo_studio import SEOApprovalRequest, SEOApplyProjectRequest, SEOGenerateCreate, SEOSelectVariantRequest
from app.services.generation_telemetry_service import finalize_generation_success
from app.services.studio_platform_service import StudioPlatformService

_SEO_MODULE = AIGenerationModule.SEO

_PROGRESS_STAGES = [
    ("analyzing", 20),
    ("generating_variants", 50),
    ("scoring", 75),
    ("finalizing", 92),
]


class SEOStudioService:
    @staticmethod
    def _variant_payload(v) -> dict:
        return {
            "label": v.label,
            "youtube_title": v.youtube_title,
            "meta_title": v.meta_title,
            "description": v.description,
            "keywords": v.keywords,
            "hashtags": v.hashtags,
            "tags": v.tags,
            "open_graph": v.open_graph,
            "twitter_cards": v.twitter_cards,
            "schema_org": v.schema_org,
            "seo_score": v.seo_score,
            "suggestions": v.suggestions,
        }

    @staticmethod
    def _job_dict(gen: AIGeneration, author_name: str | None = None) -> dict:
        params = gen.parameters or {}
        meta = gen.output_meta or {}
        return {
            "id": gen.id,
            "project_id": gen.project_id,
            "module": gen.module,
            "prompt": gen.prompt,
            "topic": gen.prompt,
            "parameters": gen.parameters,
            "content_type": params.get("content_type", "video"),
            "target_keyword": params.get("target_keyword", ""),
            "variant_count": params.get("variant_count", 3),
            "provider": gen.provider or "demo",
            "status": gen.status,
            "output_text": gen.output_text,
            "output_meta": gen.output_meta,
            "progress": meta.get("progress", 0),
            "stage": meta.get("stage"),
            "variants": meta.get("variants", []),
            "selected_variant_id": meta.get("selected_variant_id"),
            "seo_score": meta.get("best_seo_score"),
            "approval_status": meta.get("approval_status", "none"),
            "result_url": gen.result_url,
            "error": gen.error,
            "retry_count": gen.retry_count or 0,
            "created_by_id": gen.created_by_id,
            "author_name": author_name,
            "created_at": gen.created_at,
            "started_at": gen.started_at,
            "completed_at": gen.completed_at,
            "cancelled_at": gen.cancelled_at,
        }

    @staticmethod
    def _seo_query(db: Session):
        return (
            db.query(AIGeneration, User)
            .outerjoin(User, User.id == AIGeneration.created_by_id)
            .filter(AIGeneration.module == _SEO_MODULE)
            .order_by(AIGeneration.created_at.desc())
        )

    @staticmethod
    def _status_counts(db: Session) -> dict[str, int]:
        rows = (
            db.query(AIGeneration.status, func.count(AIGeneration.id))
            .filter(AIGeneration.module == _SEO_MODULE)
            .group_by(AIGeneration.status)
            .all()
        )
        base = {s.value: 0 for s in AIGenerationStatus}
        for status, count in rows:
            key = status.value if hasattr(status, "value") else str(status)
            base[key] = count
        return base

    @staticmethod
    def _set_progress(db: Session, gen: AIGeneration, stage: str, progress: int) -> None:
        meta = dict(gen.output_meta or {})
        meta["stage"] = stage
        meta["progress"] = progress
        gen.output_meta = meta
        db.commit()

    @staticmethod
    def get_overview(db: Session, user: User) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        return {
            "content_types": [{"id": c, "label": c.title()} for c in CONTENT_TYPES],
            "providers": get_seo_registry().list_providers(),
            "queue_counts": SEOStudioService._status_counts(db),
        }

    @staticmethod
    def create_generation(db: Session, user: User, data: SEOGenerateCreate) -> AIGeneration:
        if data.project_id:
            StudioPlatformService.require_permission(db, user, data.project_id, "ai.generate")
        else:
            StudioPlatformService.require_permission(db, user, None, "ai.generate")

        if not data.topic.strip():
            raise ConflictError("Topic is required")

        ctype = data.content_type if data.content_type in CONTENT_TYPES else "video"
        params = {
            "content_type": ctype,
            "target_keyword": data.target_keyword or "",
            "variant_count": max(1, min(data.variant_count, 5)),
            **(data.parameters or {}),
        }

        gen = AIGeneration(
            project_id=data.project_id,
            module=_SEO_MODULE,
            prompt=data.topic.strip(),
            parameters=params,
            provider=data.provider or get_seo_registry().resolve().id,
            status=AIGenerationStatus.QUEUED,
            created_by_id=user.id,
        )
        db.add(gen)
        db.flush()

        from app.workers.studio_tasks import run_ai_generation

        task = run_ai_generation.delay(gen.id)
        gen.celery_task_id = task.id
        StudioPlatformService.log_activity(db, user.id, "seo.job_queued", data.project_id, "ai_generation", gen.id)
        db.commit()
        db.refresh(gen)
        return gen

    @staticmethod
    def execute_seo_job(db: Session, generation_id: int) -> None:
        gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
        if not gen or gen.status == AIGenerationStatus.CANCELLED:
            return

        gen.status = AIGenerationStatus.RUNNING
        gen.started_at = datetime.now(timezone.utc)
        gen.output_meta = {"progress": 0, "stage": "starting", "approval_status": "none"}
        db.commit()

        params = gen.parameters or {}
        try:
            for stage, pct in _PROGRESS_STAGES:
                gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
                if not gen or gen.status == AIGenerationStatus.CANCELLED:
                    return
                SEOStudioService._set_progress(db, gen, stage, pct)
                time.sleep(0.3)

            gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
            if not gen or gen.status == AIGenerationStatus.CANCELLED:
                return

            result = get_seo_registry().generate(
                SEOGenerateRequest(
                    topic=gen.prompt,
                    content_type=params.get("content_type", "video"),
                    target_keyword=params.get("target_keyword", ""),
                    variant_count=int(params.get("variant_count", 3)),
                    project_id=gen.project_id,
                ),
                provider_id=gen.provider,
            )

            variant_rows: list[dict] = []
            for i, v in enumerate(result.variants, start=1):
                payload = SEOStudioService._variant_payload(v)
                row = AISEOVariant(
                    generation_id=gen.id,
                    variant=i,
                    label=v.label,
                    seo_score=v.seo_score,
                    payload=payload,
                    is_selected=(i == 1),
                    created_by_id=gen.created_by_id,
                )
                db.add(row)
                db.flush()
                variant_rows.append({"id": row.id, "variant": i, **payload})

            best = max(result.variants, key=lambda x: x.seo_score) if result.variants else None

            gen.status = AIGenerationStatus.COMPLETED
            gen.completed_at = datetime.now(timezone.utc)
            gen.output_text = result.output_text
            meta = dict(result.meta or {})
            meta["progress"] = 100
            meta["stage"] = "complete"
            meta["variants"] = variant_rows
            meta["best_seo_score"] = best.seo_score if best else 0
            meta["selected_variant_id"] = variant_rows[0]["id"] if variant_rows else None
            meta["approval_status"] = "none"
            gen.output_meta = meta
            gen.provider = result.provider

            finalize_generation_success(
                db, gen, started_at=gen.started_at, output_text=result.output_text, meta=meta,
            )

            if gen.created_by_id:
                db.add(
                    StudioNotification(
                        user_id=gen.created_by_id,
                        notification_type="seo_job_complete",
                        title=f"SEO pack ready — score {meta['best_seo_score']}/100",
                        body=gen.prompt[:120],
                        data={"generation_id": gen.id, "variants": len(variant_rows)},
                    )
                )
            db.commit()
        except Exception as exc:
            gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
            if gen and gen.status != AIGenerationStatus.CANCELLED:
                gen.status = AIGenerationStatus.FAILED
                meta = dict(gen.output_meta or {})
                meta["stage"] = "failed"
                gen.output_meta = meta
                gen.error = str(exc)
                db.commit()
            raise

    @staticmethod
    def get_queue(db: Session, user: User) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        q = SEOStudioService._seo_query(db)
        queued = q.filter(AIGeneration.status == AIGenerationStatus.QUEUED).limit(50).all()
        running = q.filter(AIGeneration.status == AIGenerationStatus.RUNNING).limit(20).all()
        return {
            "queued": [SEOStudioService._job_dict(g, u.full_name if u else None) for g, u in queued],
            "running": [SEOStudioService._job_dict(g, u.full_name if u else None) for g, u in running],
            "counts": SEOStudioService._status_counts(db),
        }

    @staticmethod
    def get_history(db: Session, user: User, limit: int = 50, offset: int = 0) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        q = SEOStudioService._seo_query(db)
        total = q.count()
        rows = q.offset(offset).limit(limit).all()
        return {
            "items": [SEOStudioService._job_dict(g, u.full_name if u else None) for g, u in rows],
            "total": total,
        }

    @staticmethod
    def list_variants(db: Session, user: User, generation_id: int) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        rows = (
            db.query(AISEOVariant)
            .filter(AISEOVariant.generation_id == generation_id)
            .order_by(AISEOVariant.variant.asc())
            .all()
        )
        return [
            {
                "id": r.id,
                "generation_id": r.generation_id,
                "variant": r.variant,
                "label": r.label,
                "seo_score": r.seo_score,
                "is_selected": r.is_selected,
                **r.payload,
            }
            for r in rows
        ]

    @staticmethod
    def select_variant(db: Session, user: User, generation_id: int, data: SEOSelectVariantRequest) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
        if not gen:
            raise NotFoundError("SEO generation")
        rows = db.query(AISEOVariant).filter(AISEOVariant.generation_id == generation_id).all()
        selected = None
        for r in rows:
            r.is_selected = r.id == data.variant_id
            if r.is_selected:
                selected = r
        if not selected:
            raise NotFoundError("SEO variant")
        meta = dict(gen.output_meta or {})
        meta["selected_variant_id"] = selected.id
        meta["selected_variant"] = selected.payload
        gen.output_meta = meta
        db.commit()
        return {"selected_variant_id": selected.id, "seo_score": selected.seo_score}

    @staticmethod
    def request_approval(db: Session, user: User, generation_id: int, data: SEOApprovalRequest) -> dict:
        gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
        if not gen or gen.status != AIGenerationStatus.COMPLETED:
            raise ConflictError("Only completed SEO jobs can be submitted for approval")
        project_id = gen.project_id or data.project_id
        if not project_id:
            raise ConflictError("Project is required for approval")
        StudioPlatformService.require_permission(db, user, project_id, "ai.generate")

        approval = StudioApproval(
            project_id=project_id,
            entity_type="ai_seo",
            entity_id=gen.id,
            requested_by_id=user.id,
            status=ApprovalStatus.PENDING,
            notes=data.notes,
        )
        db.add(approval)
        meta = dict(gen.output_meta or {})
        meta["approval_status"] = "pending"
        meta["approval_id"] = None
        gen.output_meta = meta
        db.flush()
        meta["approval_id"] = approval.id
        gen.output_meta = meta
        db.commit()
        return {"approval_id": approval.id, "status": "pending"}

    @staticmethod
    def approve(db: Session, user: User, generation_id: int, data: SEOApprovalRequest | None = None) -> dict:
        gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
        if not gen:
            raise NotFoundError("SEO generation")
        project_id = gen.project_id
        if project_id:
            StudioPlatformService.require_permission(db, user, project_id, "publish.approve")

        approval = (
            db.query(StudioApproval)
            .filter(StudioApproval.entity_type == "ai_seo", StudioApproval.entity_id == gen.id)
            .order_by(StudioApproval.created_at.desc())
            .first()
        )
        if approval:
            approval.status = ApprovalStatus.APPROVED
            approval.approver_id = user.id
            approval.resolved_at = datetime.now(timezone.utc)
            if data and data.notes:
                approval.notes = data.notes

        meta = dict(gen.output_meta or {})
        meta["approval_status"] = "approved"
        gen.output_meta = meta
        db.commit()
        return {"generation_id": gen.id, "approval_status": "approved"}

    @staticmethod
    def reject(db: Session, user: User, generation_id: int, data: SEOApprovalRequest | None = None) -> dict:
        gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
        if not gen:
            raise NotFoundError("SEO generation")
        if gen.project_id:
            StudioPlatformService.require_permission(db, user, gen.project_id, "publish.approve")

        approval = (
            db.query(StudioApproval)
            .filter(StudioApproval.entity_type == "ai_seo", StudioApproval.entity_id == gen.id)
            .order_by(StudioApproval.created_at.desc())
            .first()
        )
        if approval:
            approval.status = ApprovalStatus.REJECTED
            approval.approver_id = user.id
            approval.resolved_at = datetime.now(timezone.utc)
            if data and data.notes:
                approval.notes = data.notes

        meta = dict(gen.output_meta or {})
        meta["approval_status"] = "rejected"
        gen.output_meta = meta
        db.commit()
        return {"generation_id": gen.id, "approval_status": "rejected"}

    @staticmethod
    def export_pack(db: Session, user: User, generation_id: int, variant_id: int | None = None) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
        if not gen or gen.status != AIGenerationStatus.COMPLETED:
            raise NotFoundError("Completed SEO generation")

        row = None
        if variant_id:
            row = db.query(AISEOVariant).filter(
                AISEOVariant.id == variant_id, AISEOVariant.generation_id == generation_id,
            ).first()
        if not row:
            row = (
                db.query(AISEOVariant)
                .filter(AISEOVariant.generation_id == generation_id, AISEOVariant.is_selected.is_(True))
                .first()
            )
        if not row:
            row = (
                db.query(AISEOVariant)
                .filter(AISEOVariant.generation_id == generation_id)
                .order_by(AISEOVariant.seo_score.desc())
                .first()
            )
        if not row:
            raise NotFoundError("SEO variant")

        pack = {
            "youtube_title": row.payload.get("youtube_title"),
            "meta_title": row.payload.get("meta_title"),
            "description": row.payload.get("description"),
            "keywords": row.payload.get("keywords", []),
            "hashtags": row.payload.get("hashtags", []),
            "tags": row.payload.get("tags", []),
            "open_graph": row.payload.get("open_graph", {}),
            "twitter_cards": row.payload.get("twitter_cards", {}),
            "schema_org": row.payload.get("schema_org", {}),
            "seo_score": row.seo_score,
            "suggestions": row.payload.get("suggestions", []),
        }
        try:
            from app.domain.plugins.registry import PluginEventBus

            project_id = gen.project_id
            if pack.get("meta_title"):
                title_result = PluginEventBus.run_hooks(
                    db,
                    "seo.format_title",
                    {"title": pack["meta_title"], "project_id": project_id},
                    user_id=user.id,
                    commit=False,
                )
                pack["meta_title"] = title_result.get("title", pack["meta_title"])
            if pack.get("description"):
                desc_result = PluginEventBus.run_hooks(
                    db,
                    "seo.format_description",
                    {"description": pack["description"], "project_id": project_id},
                    user_id=user.id,
                    commit=False,
                )
                pack["description"] = desc_result.get("description", pack["description"])
        except Exception:
            pass
        return {"generation_id": gen.id, "variant_id": row.id, "pack": pack}

    @staticmethod
    def apply_to_project(
        db: Session, user: User, generation_id: int, data: SEOApplyProjectRequest,
    ) -> dict:
        from app.models.studio import Production

        gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
        if not gen or gen.status != AIGenerationStatus.COMPLETED:
            raise ConflictError("Only completed SEO jobs can be applied to a project")

        project_id = data.project_id or gen.project_id
        if not project_id:
            raise ConflictError("Project is required")

        StudioPlatformService.require_permission(db, user, project_id, "project.update")
        export_data = SEOStudioService.export_pack(db, user, generation_id, data.variant_id)
        pack = export_data["pack"]

        project = db.query(Production).filter(Production.id == project_id).first()
        if not project:
            raise NotFoundError("Project")

        project.seo_title = pack.get("meta_title") or pack.get("youtube_title")
        project.seo_description = pack.get("description")
        project.seo_keywords = pack.get("keywords", [])
        db.commit()

        return {
            "project_id": project.id,
            "seo_title": project.seo_title,
            "seo_description": project.seo_description,
            "seo_keywords": project.seo_keywords or [],
        }
