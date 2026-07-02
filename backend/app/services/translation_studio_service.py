"""AI Translation Studio — scripts, subtitles, metadata, TM, approval."""

from __future__ import annotations

import time
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.domain.studio.enums import AIGenerationModule, AIGenerationStatus, ApprovalStatus
from app.domain.translation.providers.registry import get_translation_registry
from app.domain.translation.types import (
    CONTENT_TYPE_LABELS,
    CONTENT_TYPES,
    TRANSLATION_LANGUAGES,
    TranslationRequest,
)
from app.models import User
from app.models.studio_platform import (
    AIGeneration,
    AITranslationMemory,
    AITranslationVersion,
    StudioApproval,
    StudioNotification,
)
from app.schemas.translation_studio import TranslationApprovalRequest, TranslationGenerateCreate
from app.services.generation_telemetry_service import finalize_generation_success
from app.services.studio_platform_service import StudioPlatformService

_TRANSLATION_MODULE = AIGenerationModule.TRANSLATION

_PROGRESS_STAGES = [
    ("analyzing", 15),
    ("translation_memory", 35),
    ("translating", 60),
    ("syncing_subtitles", 80),
    ("finalizing", 92),
]


class TranslationStudioService:
    @staticmethod
    def _job_dict(gen: AIGeneration, author_name: str | None = None) -> dict:
        params = gen.parameters or {}
        meta = gen.output_meta or {}
        return {
            "id": gen.id,
            "project_id": gen.project_id,
            "module": gen.module,
            "prompt": gen.prompt,
            "source_text": params.get("source_text", gen.prompt),
            "parameters": gen.parameters,
            "content_type": params.get("content_type", "script"),
            "source_lang": params.get("source_lang", "en"),
            "target_lang": params.get("target_lang", "es"),
            "auto_sync": params.get("auto_sync", True),
            "generate_srt": params.get("generate_srt", True),
            "generate_vtt": params.get("generate_vtt", True),
            "provider": gen.provider or "demo",
            "status": gen.status,
            "output_text": gen.output_text,
            "translated_text": meta.get("translated_text") or gen.output_text,
            "output_meta": gen.output_meta,
            "progress": meta.get("progress", 0),
            "stage": meta.get("stage"),
            "tm_hit": meta.get("tm_hit", False),
            "srt_url": meta.get("srt_url"),
            "vtt_url": meta.get("vtt_url"),
            "srt_content": meta.get("srt_content"),
            "vtt_content": meta.get("vtt_content"),
            "version_id": meta.get("version_id"),
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
    def _translation_query(db: Session):
        return (
            db.query(AIGeneration, User)
            .outerjoin(User, User.id == AIGeneration.created_by_id)
            .filter(AIGeneration.module == _TRANSLATION_MODULE)
            .order_by(AIGeneration.created_at.desc())
        )

    @staticmethod
    def _status_counts(db: Session) -> dict[str, int]:
        rows = (
            db.query(AIGeneration.status, func.count(AIGeneration.id))
            .filter(AIGeneration.module == _TRANSLATION_MODULE)
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
    def _lookup_tm(
        db: Session,
        source_lang: str,
        target_lang: str,
        content_type: str,
        source_text: str,
    ) -> AITranslationMemory | None:
        text = source_text.strip()
        if not text:
            return None
        return (
            db.query(AITranslationMemory)
            .filter(
                AITranslationMemory.source_lang == source_lang,
                AITranslationMemory.target_lang == target_lang,
                AITranslationMemory.content_type == content_type,
                AITranslationMemory.source_text == text,
            )
            .first()
        )

    @staticmethod
    def _store_tm(
        db: Session,
        source_lang: str,
        target_lang: str,
        content_type: str,
        source_text: str,
        translated_text: str,
        user_id: int | None,
    ) -> None:
        text = source_text.strip()
        if not text or not translated_text.strip():
            return
        existing = TranslationStudioService._lookup_tm(db, source_lang, target_lang, content_type, text)
        if existing:
            existing.translated_text = translated_text.strip()
            existing.usage_count = (existing.usage_count or 0) + 1
            existing.updated_at = datetime.now(timezone.utc)
            return
        db.add(
            AITranslationMemory(
                source_lang=source_lang,
                target_lang=target_lang,
                content_type=content_type,
                source_text=text,
                translated_text=translated_text.strip(),
                created_by_id=user_id,
            )
        )

    @staticmethod
    def get_overview(db: Session, user: User) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        tm_count = db.query(func.count(AITranslationMemory.id)).scalar() or 0
        return {
            "languages": [{"code": c, "label": l} for c, l in TRANSLATION_LANGUAGES],
            "content_types": [
                {"id": c, "label": CONTENT_TYPE_LABELS.get(c, c.title())} for c in CONTENT_TYPES
            ],
            "providers": get_translation_registry().list_providers(),
            "queue_counts": TranslationStudioService._status_counts(db),
            "translation_memory_count": tm_count,
        }

    @staticmethod
    def create_generation(db: Session, user: User, data: TranslationGenerateCreate) -> AIGeneration:
        if data.project_id:
            StudioPlatformService.require_permission(db, user, data.project_id, "ai.generate")
        else:
            StudioPlatformService.require_permission(db, user, None, "ai.generate")

        if not data.source_text.strip():
            raise ConflictError("Source text is required")

        lang_codes = {c for c, _ in TRANSLATION_LANGUAGES}
        ctype = data.content_type if data.content_type in CONTENT_TYPES else "script"
        source = data.source_lang if data.source_lang in lang_codes else "en"
        target = data.target_lang if data.target_lang in lang_codes else "es"
        if source == target:
            raise ConflictError("Source and target language must differ")

        params = {
            "source_text": data.source_text.strip(),
            "content_type": ctype,
            "source_lang": source,
            "target_lang": target,
            "auto_sync": data.auto_sync,
            "generate_srt": data.generate_srt,
            "generate_vtt": data.generate_vtt,
            **(data.parameters or {}),
        }

        gen = AIGeneration(
            project_id=data.project_id,
            module=_TRANSLATION_MODULE,
            prompt=data.source_text.strip()[:500],
            parameters=params,
            provider=data.provider or get_translation_registry().resolve().id,
            status=AIGenerationStatus.QUEUED,
            created_by_id=user.id,
        )
        db.add(gen)
        db.flush()

        from app.workers.studio_tasks import run_ai_generation

        task = run_ai_generation.delay(gen.id)
        gen.celery_task_id = task.id
        StudioPlatformService.log_activity(
            db, user.id, "translation.job_queued", data.project_id, "ai_generation", gen.id,
        )
        db.commit()
        db.refresh(gen)
        return gen

    @staticmethod
    def execute_translation_job(db: Session, generation_id: int) -> None:
        gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
        if not gen or gen.status == AIGenerationStatus.CANCELLED:
            return

        gen.status = AIGenerationStatus.RUNNING
        gen.started_at = datetime.now(timezone.utc)
        gen.output_meta = {"progress": 0, "stage": "starting", "approval_status": "none"}
        db.commit()

        params = gen.parameters or {}
        source_text = params.get("source_text", gen.prompt or "")
        source_lang = params.get("source_lang", "en")
        target_lang = params.get("target_lang", "es")
        content_type = params.get("content_type", "script")

        try:
            for stage, pct in _PROGRESS_STAGES:
                gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
                if not gen or gen.status == AIGenerationStatus.CANCELLED:
                    return
                TranslationStudioService._set_progress(db, gen, stage, pct)
                time.sleep(0.25)

            gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
            if not gen or gen.status == AIGenerationStatus.CANCELLED:
                return

            tm_row = TranslationStudioService._lookup_tm(
                db, source_lang, target_lang, content_type, source_text,
            )
            tm_hit = False
            meta_override: dict = {}
            if tm_row:
                tm_hit = True
                tm_row.usage_count = (tm_row.usage_count or 0) + 1
                meta_override["translated_override"] = tm_row.translated_text

            result = get_translation_registry().translate(
                TranslationRequest(
                    source_text=source_text,
                    content_type=content_type,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    auto_sync=bool(params.get("auto_sync", True)),
                    generate_srt=bool(params.get("generate_srt", True)),
                    generate_vtt=bool(params.get("generate_vtt", True)),
                    project_id=gen.project_id,
                    meta=meta_override,
                ),
                provider_id=gen.provider,
            )
            result.tm_hit = tm_hit

            if not tm_hit:
                TranslationStudioService._store_tm(
                    db,
                    source_lang,
                    target_lang,
                    content_type,
                    source_text,
                    result.translated_text,
                    gen.created_by_id,
                )

            version_num = (
                db.query(func.count(AITranslationVersion.id))
                .filter(AITranslationVersion.generation_id == gen.id)
                .scalar()
                or 0
            ) + 1
            version_row = AITranslationVersion(
                generation_id=gen.id,
                version=version_num,
                label=f"{content_type} · {source_lang}→{target_lang}",
                result_url=result.result_url,
                r2_key=result.r2_key,
                output_meta={
                    "translated_text": result.translated_text,
                    "srt_url": result.srt_url,
                    "vtt_url": result.vtt_url,
                    "tm_hit": tm_hit,
                    **(result.meta or {}),
                },
                created_by_id=gen.created_by_id,
            )
            db.add(version_row)
            db.flush()

            gen.status = AIGenerationStatus.COMPLETED
            gen.completed_at = datetime.now(timezone.utc)
            gen.output_text = result.translated_text
            gen.result_url = result.result_url
            gen.r2_key = result.r2_key
            gen.provider = result.provider
            meta = dict(result.meta or {})
            meta["progress"] = 100
            meta["stage"] = "complete"
            meta["translated_text"] = result.translated_text
            meta["tm_hit"] = tm_hit
            meta["srt_url"] = result.srt_url
            meta["vtt_url"] = result.vtt_url
            meta["srt_content"] = result.srt_content
            meta["vtt_content"] = result.vtt_content
            meta["version_id"] = version_row.id
            meta["approval_status"] = "none"
            gen.output_meta = meta

            finalize_generation_success(
                db,
                gen,
                started_at=gen.started_at,
                output_text=result.translated_text,
                meta=meta,
            )

            if gen.created_by_id:
                db.add(
                    StudioNotification(
                        user_id=gen.created_by_id,
                        notification_type="translation_job_complete",
                        title=f"Translation ready — {source_lang}→{target_lang}",
                        body=source_text[:120],
                        data={"generation_id": gen.id, "tm_hit": tm_hit},
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
        q = TranslationStudioService._translation_query(db)
        queued = q.filter(AIGeneration.status == AIGenerationStatus.QUEUED).limit(50).all()
        running = q.filter(AIGeneration.status == AIGenerationStatus.RUNNING).limit(20).all()
        return {
            "queued": [TranslationStudioService._job_dict(g, u.full_name if u else None) for g, u in queued],
            "running": [TranslationStudioService._job_dict(g, u.full_name if u else None) for g, u in running],
            "counts": TranslationStudioService._status_counts(db),
        }

    @staticmethod
    def get_history(db: Session, user: User, limit: int = 50, offset: int = 0) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        q = TranslationStudioService._translation_query(db)
        total = q.count()
        rows = q.offset(offset).limit(limit).all()
        return {
            "items": [TranslationStudioService._job_dict(g, u.full_name if u else None) for g, u in rows],
            "total": total,
        }

    @staticmethod
    def list_versions(db: Session, user: User, generation_id: int) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        rows = (
            db.query(AITranslationVersion)
            .filter(AITranslationVersion.generation_id == generation_id)
            .order_by(AITranslationVersion.version.desc())
            .all()
        )
        return [
            {
                "id": v.id,
                "generation_id": v.generation_id,
                "version": v.version,
                "label": v.label,
                "result_url": v.result_url,
                "output_meta": v.output_meta,
                "created_at": v.created_at,
            }
            for v in rows
        ]

    @staticmethod
    def get_job_subtitles(db: Session, user: User, job_id: int) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        gen = db.query(AIGeneration).filter(
            AIGeneration.id == job_id, AIGeneration.module == _TRANSLATION_MODULE,
        ).first()
        if not gen:
            raise NotFoundError("Translation job")
        meta = gen.output_meta or {}
        return {
            "srt": meta.get("srt_content"),
            "vtt": meta.get("vtt_content"),
            "srt_url": meta.get("srt_url"),
            "vtt_url": meta.get("vtt_url"),
        }

    @staticmethod
    def list_translation_memory(
        db: Session,
        user: User,
        source_lang: str | None = None,
        target_lang: str | None = None,
        content_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        q = db.query(AITranslationMemory).order_by(AITranslationMemory.updated_at.desc())
        if source_lang:
            q = q.filter(AITranslationMemory.source_lang == source_lang)
        if target_lang:
            q = q.filter(AITranslationMemory.target_lang == target_lang)
        if content_type:
            q = q.filter(AITranslationMemory.content_type == content_type)
        total = q.count()
        rows = q.offset(offset).limit(limit).all()
        return {
            "items": [
                {
                    "id": r.id,
                    "source_lang": r.source_lang,
                    "target_lang": r.target_lang,
                    "content_type": r.content_type,
                    "source_text": r.source_text,
                    "translated_text": r.translated_text,
                    "usage_count": r.usage_count,
                    "updated_at": r.updated_at,
                    "created_at": r.created_at,
                }
                for r in rows
            ],
            "total": total,
        }

    @staticmethod
    def delete_translation_memory(db: Session, user: User, entry_id: int) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        row = db.query(AITranslationMemory).filter(AITranslationMemory.id == entry_id).first()
        if not row:
            raise NotFoundError("Translation memory entry")
        db.delete(row)
        db.commit()
        return {"deleted": entry_id}

    @staticmethod
    def request_approval(
        db: Session, user: User, generation_id: int, data: TranslationApprovalRequest,
    ) -> dict:
        gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
        if not gen or gen.status != AIGenerationStatus.COMPLETED:
            raise ConflictError("Only completed translation jobs can be submitted for approval")
        project_id = gen.project_id or data.project_id
        if not project_id:
            raise ConflictError("Project is required for approval")
        StudioPlatformService.require_permission(db, user, project_id, "ai.generate")

        approval = StudioApproval(
            project_id=project_id,
            entity_type="ai_translation",
            entity_id=gen.id,
            requested_by_id=user.id,
            status=ApprovalStatus.PENDING,
            notes=data.notes,
        )
        db.add(approval)
        meta = dict(gen.output_meta or {})
        meta["approval_status"] = "pending"
        gen.output_meta = meta
        db.flush()
        meta["approval_id"] = approval.id
        gen.output_meta = meta
        db.commit()
        return {"approval_id": approval.id, "status": "pending"}

    @staticmethod
    def approve(
        db: Session, user: User, generation_id: int, data: TranslationApprovalRequest | None = None,
    ) -> dict:
        gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
        if not gen:
            raise NotFoundError("Translation job")
        if gen.project_id:
            StudioPlatformService.require_permission(db, user, gen.project_id, "publish.approve")

        approval = (
            db.query(StudioApproval)
            .filter(StudioApproval.entity_type == "ai_translation", StudioApproval.entity_id == gen.id)
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
    def reject(
        db: Session, user: User, generation_id: int, data: TranslationApprovalRequest | None = None,
    ) -> dict:
        gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
        if not gen:
            raise NotFoundError("Translation job")
        if gen.project_id:
            StudioPlatformService.require_permission(db, user, gen.project_id, "publish.approve")

        approval = (
            db.query(StudioApproval)
            .filter(StudioApproval.entity_type == "ai_translation", StudioApproval.entity_id == gen.id)
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
