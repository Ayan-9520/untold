"""AI Music Studio — background scores, queue, favorites, cloud storage."""

from __future__ import annotations

import time
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.domain.music.providers.registry import get_music_registry
from app.domain.music.types import MUSIC_CATEGORIES, MusicGenerateRequest
from app.domain.studio.enums import AIGenerationModule, AIGenerationStatus, AssetType
from app.models import User
from app.models.studio_platform import (
    AIGeneration,
    AIMusicVersion,
    AIPromptLibrary,
    StudioAsset,
    StudioNotification,
)
from app.schemas.music_studio import MusicGenerateCreate, MusicPreviewCreate
from app.services.generation_telemetry_service import finalize_generation_success
from app.services.studio_platform_service import StudioPlatformService

_MUSIC_MODULE = AIGenerationModule.MUSIC

_PROGRESS_STAGES = [
    ("validating", 10),
    ("composing", 40),
    ("arranging", 65),
    ("mastering", 85),
    ("uploading", 95),
]

_DEFAULT_MUSIC_PROMPTS = [
    {
        "title": "Sports highlight bed",
        "module": "music",
        "prompt_template": "High-energy stadium underscore for {topic} highlights. Driving rhythm, crowd-ready momentum.",
        "description": "Upbeat sports background track.",
        "tags": ["sports"],
        "parameters": {"category": "sports"},
    },
    {
        "title": "Epic legacy theme",
        "module": "music",
        "prompt_template": "Cinematic orchestral swell for a legacy moment in {topic}. Heroic, emotional peak.",
        "description": "Epic score for key story beats.",
        "tags": ["epic"],
        "parameters": {"category": "epic"},
    },
    {
        "title": "Documentary ambient",
        "module": "music",
        "prompt_template": "Gentle reflective underscore beneath narration about {topic}. Warm, unobtrusive.",
        "description": "Documentary bed music.",
        "tags": ["documentary"],
        "parameters": {"category": "documentary"},
    },
    {
        "title": "Suspense investigation",
        "module": "music",
        "prompt_template": "Tense low-frequency pulse for investigative segment on {topic}. Slow build.",
        "description": "Suspense underscore.",
        "tags": ["suspense"],
        "parameters": {"category": "suspense"},
    },
]


class MusicStudioService:
    @staticmethod
    def _job_dict(gen: AIGeneration, author_name: str | None = None) -> dict:
        params = gen.parameters or {}
        meta = gen.output_meta or {}
        return {
            "id": gen.id,
            "project_id": gen.project_id,
            "module": gen.module,
            "prompt": gen.prompt,
            "parameters": gen.parameters,
            "category": params.get("category", "documentary"),
            "duration_seconds": params.get("duration_seconds", 60),
            "loop": params.get("loop", True),
            "fade_in_seconds": params.get("fade_in_seconds", 2.0),
            "fade_out_seconds": params.get("fade_out_seconds", 3.0),
            "provider": gen.provider or "demo",
            "status": gen.status,
            "output_text": gen.output_text,
            "output_meta": gen.output_meta,
            "progress": meta.get("progress", 0),
            "stage": meta.get("stage"),
            "bpm": meta.get("bpm"),
            "result_url": gen.result_url,
            "r2_key": gen.r2_key,
            "error": gen.error,
            "is_favorite": gen.is_favorite,
            "retry_count": gen.retry_count or 0,
            "created_by_id": gen.created_by_id,
            "author_name": author_name,
            "created_at": gen.created_at,
            "started_at": gen.started_at,
            "completed_at": gen.completed_at,
            "cancelled_at": gen.cancelled_at,
        }

    @staticmethod
    def _music_query(db: Session):
        return (
            db.query(AIGeneration, User)
            .outerjoin(User, User.id == AIGeneration.created_by_id)
            .filter(AIGeneration.module == _MUSIC_MODULE)
            .order_by(AIGeneration.created_at.desc())
        )

    @staticmethod
    def _status_counts(db: Session) -> dict[str, int]:
        rows = (
            db.query(AIGeneration.status, func.count(AIGeneration.id))
            .filter(AIGeneration.module == _MUSIC_MODULE)
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
    def _build_request(data: MusicGenerateCreate | MusicPreviewCreate) -> MusicGenerateRequest:
        category = data.category if data.category in MUSIC_CATEGORIES else "documentary"
        return MusicGenerateRequest(
            prompt=data.prompt.strip(),
            category=category,
            duration_seconds=max(10, min(data.duration_seconds, 180)),
            loop=data.loop,
            fade_in_seconds=max(0.0, min(data.fade_in_seconds, 10.0)),
            fade_out_seconds=max(0.0, min(data.fade_out_seconds, 15.0)),
            project_id=data.project_id,
        )

    @staticmethod
    def get_overview(db: Session, user: User) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        MusicStudioService.seed_music_prompts(db)
        return {
            "categories": [
                {"id": c, "label": c.replace("_", " ").title()} for c in MUSIC_CATEGORIES
            ],
            "providers": get_music_registry().list_providers(),
            "queue_counts": MusicStudioService._status_counts(db),
        }

    @staticmethod
    def create_generation(db: Session, user: User, data: MusicGenerateCreate) -> AIGeneration:
        if data.project_id:
            StudioPlatformService.require_permission(db, user, data.project_id, "ai.generate")
        else:
            StudioPlatformService.require_permission(db, user, None, "ai.generate")

        if not data.prompt.strip():
            raise ConflictError("Music brief is required")

        req = MusicStudioService._build_request(data)
        params = {
            "category": req.category,
            "duration_seconds": req.duration_seconds,
            "loop": req.loop,
            "fade_in_seconds": req.fade_in_seconds,
            "fade_out_seconds": req.fade_out_seconds,
            **(data.parameters or {}),
        }

        gen = AIGeneration(
            project_id=data.project_id,
            module=_MUSIC_MODULE,
            prompt=data.prompt.strip(),
            parameters=params,
            provider=data.provider or get_music_registry().resolve().id,
            status=AIGenerationStatus.QUEUED,
            created_by_id=user.id,
        )
        db.add(gen)
        db.flush()

        from app.workers.studio_tasks import run_ai_generation

        task = run_ai_generation.delay(gen.id)
        gen.celery_task_id = task.id
        StudioPlatformService.log_activity(db, user.id, "music.job_queued", data.project_id, "ai_generation", gen.id)
        db.commit()
        db.refresh(gen)
        return gen

    @staticmethod
    def preview(db: Session, user: User, data: MusicPreviewCreate) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        if not data.prompt.strip():
            raise ConflictError("Preview brief is required")
        req = MusicStudioService._build_request(data)
        result = get_music_registry().preview(req, provider_id=data.provider)
        return {
            "audio_url": result.result_url,
            "duration_seconds": result.duration_seconds,
            "provider": result.provider,
            "mime_type": result.mime_type,
        }

    @staticmethod
    def execute_music_job(db: Session, generation_id: int) -> None:
        gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
        if not gen or gen.status == AIGenerationStatus.CANCELLED:
            return

        gen.status = AIGenerationStatus.RUNNING
        gen.started_at = datetime.now(timezone.utc)
        gen.output_meta = {"progress": 0, "stage": "starting"}
        db.commit()

        params = gen.parameters or {}
        try:
            for stage, pct in _PROGRESS_STAGES:
                gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
                if not gen or gen.status == AIGenerationStatus.CANCELLED:
                    return
                MusicStudioService._set_progress(db, gen, stage, pct)
                time.sleep(0.35)

            gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
            if not gen or gen.status == AIGenerationStatus.CANCELLED:
                return

            result = get_music_registry().generate(
                MusicGenerateRequest(
                    prompt=gen.prompt,
                    category=params.get("category", "documentary"),
                    duration_seconds=int(params.get("duration_seconds", 60)),
                    loop=bool(params.get("loop", True)),
                    fade_in_seconds=float(params.get("fade_in_seconds", 2.0)),
                    fade_out_seconds=float(params.get("fade_out_seconds", 3.0)),
                    project_id=gen.project_id,
                ),
                provider_id=gen.provider,
            )

            gen.status = AIGenerationStatus.COMPLETED
            gen.completed_at = datetime.now(timezone.utc)
            gen.output_text = result.output_text
            meta = dict(result.meta or {})
            meta["progress"] = 100
            meta["stage"] = "complete"
            meta["mime_type"] = result.mime_type
            gen.output_meta = meta
            gen.result_url = result.result_url
            gen.r2_key = result.r2_key
            gen.provider = result.provider

            MusicStudioService._save_version(
                db, gen.id, gen.created_by_id, result.result_url, result.r2_key, meta, label="v1",
            )

            finalize_generation_success(
                db, gen, started_at=gen.started_at, output_text=result.output_text, meta=meta,
            )

            if gen.created_by_id:
                db.add(
                    StudioNotification(
                        user_id=gen.created_by_id,
                        notification_type="music_job_complete",
                        title=f"Music ready — {params.get('category', 'score')}",
                        body=gen.prompt[:120],
                        data={"generation_id": gen.id, "result_url": gen.result_url},
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
    def _save_version(
        db: Session,
        generation_id: int,
        user_id: int | None,
        result_url: str | None,
        r2_key: str | None,
        meta: dict | None,
        label: str | None = None,
    ) -> AIMusicVersion:
        latest = (
            db.query(func.max(AIMusicVersion.version))
            .filter(AIMusicVersion.generation_id == generation_id)
            .scalar()
            or 0
        )
        row = AIMusicVersion(
            generation_id=generation_id,
            version=int(latest) + 1,
            label=label,
            result_url=result_url,
            r2_key=r2_key,
            output_meta=meta,
            created_by_id=user_id,
        )
        db.add(row)
        return row

    @staticmethod
    def get_queue(db: Session, user: User) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        q = MusicStudioService._music_query(db)
        queued = q.filter(AIGeneration.status == AIGenerationStatus.QUEUED).limit(50).all()
        running = q.filter(AIGeneration.status == AIGenerationStatus.RUNNING).limit(20).all()
        return {
            "queued": [MusicStudioService._job_dict(g, u.full_name if u else None) for g, u in queued],
            "running": [MusicStudioService._job_dict(g, u.full_name if u else None) for g, u in running],
            "counts": MusicStudioService._status_counts(db),
        }

    @staticmethod
    def get_history(
        db: Session,
        user: User,
        category: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        q = MusicStudioService._music_query(db)
        if category:
            q = q.filter(AIGeneration.parameters.contains({"category": category}))
        total = q.count()
        rows = q.offset(offset).limit(limit).all()
        return {
            "items": [MusicStudioService._job_dict(g, u.full_name if u else None) for g, u in rows],
            "total": total,
        }

    @staticmethod
    def get_favorites(db: Session, user: User, limit: int = 50) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        rows = (
            MusicStudioService._music_query(db)
            .filter(AIGeneration.is_favorite.is_(True))
            .limit(limit)
            .all()
        )
        return [MusicStudioService._job_dict(g, u.full_name if u else None) for g, u in rows]

    @staticmethod
    def toggle_favorite(db: Session, user: User, generation_id: int) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
        if not gen or gen.module != _MUSIC_MODULE:
            raise NotFoundError("Music generation")
        gen.is_favorite = not gen.is_favorite
        db.commit()
        return {"id": gen.id, "is_favorite": gen.is_favorite}

    @staticmethod
    def list_versions(db: Session, user: User, generation_id: int) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        rows = (
            db.query(AIMusicVersion)
            .filter(AIMusicVersion.generation_id == generation_id)
            .order_by(AIMusicVersion.version.desc())
            .all()
        )
        return [
            {
                "id": v.id,
                "generation_id": v.generation_id,
                "version": v.version,
                "label": v.label,
                "result_url": v.result_url,
                "created_at": v.created_at,
            }
            for v in rows
        ]

    @staticmethod
    def save_to_asset_library(db: Session, user: User, generation_id: int) -> dict:
        gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
        if not gen or not gen.r2_key:
            raise NotFoundError("Music generation")
        StudioPlatformService.require_permission(db, user, gen.project_id, "asset.upload")
        meta = gen.output_meta or {}
        params = gen.parameters or {}
        asset = StudioAsset(
            project_id=gen.project_id,
            title=gen.prompt[:200],
            asset_type=AssetType.AUDIO,
            folder="audio",
            filename=gen.r2_key.rsplit("/", 1)[-1],
            r2_key=gen.r2_key,
            url=gen.result_url,
            preview_url=gen.result_url,
            size_bytes=meta.get("size_bytes", 0),
            mime_type=meta.get("mime_type", "audio/wav"),
            tags=["ai-generated", "music", params.get("category", "score")],
            cloud_provider=gen.provider,
            meta={
                "generation_id": gen.id,
                "duration_seconds": meta.get("duration_seconds"),
                "loop": params.get("loop"),
                "bpm": meta.get("bpm"),
            },
            uploaded_by_id=user.id,
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)
        return {"asset_id": asset.id, "url": asset.url, "folder": asset.folder}

    @staticmethod
    def seed_music_prompts(db: Session) -> None:
        for item in _DEFAULT_MUSIC_PROMPTS:
            exists = (
                db.query(AIPromptLibrary)
                .filter(AIPromptLibrary.title == item["title"], AIPromptLibrary.module == item["module"])
                .first()
            )
            if exists:
                continue
            db.add(
                AIPromptLibrary(
                    title=item["title"],
                    module=item["module"],
                    prompt_template=item["prompt_template"],
                    description=item.get("description"),
                    parameters=item.get("parameters"),
                    tags=item.get("tags", []),
                    is_public=True,
                )
            )
        db.commit()

    @staticmethod
    def list_prompts(db: Session, user: User, category: str | None = None) -> list[dict]:
        from app.services.ai_studio_service import AIStudioService

        MusicStudioService.seed_music_prompts(db)
        prompts = AIStudioService.list_prompts(db, user, None)
        filtered = [p for p in prompts if p["module"] == "music"]
        if category:
            filtered = [p for p in filtered if (p.get("parameters") or {}).get("category") == category]
        return filtered
