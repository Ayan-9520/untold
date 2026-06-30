"""AI Video Studio — queue, progress, history, storage."""

from __future__ import annotations

import time
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.domain.studio.enums import AIGenerationModule, AIGenerationStatus, AssetType
from app.domain.video.providers.registry import get_video_registry
from app.domain.video.safety import validate_video_prompt
from app.domain.video.types import VIDEO_TYPES, VideoGenerateRequest
from app.models import User
from app.models.studio_platform import (
    AIGeneration,
    AIPromptLibrary,
    AIVideoVersion,
    StudioAsset,
    StudioNotification,
)
from app.schemas.video_studio import VideoGenerateCreate
from app.services.studio_platform_service import StudioPlatformService

_VIDEO_MODULE = AIGenerationModule.VIDEO

_ASPECT_MAP = {
    "16:9": (1280, 720),
    "9:16": (720, 1280),
    "1:1": (720, 720),
}

_PROGRESS_STAGES = [
    ("validating", 10),
    ("composing", 35),
    ("rendering", 60),
    ("encoding", 80),
    ("uploading", 95),
]

_DEFAULT_VIDEO_PROMPTS = [
    {
        "title": "B-roll — stadium atmosphere",
        "module": "video",
        "prompt_template": "Slow cinematic B-roll of stadium lights and crowd energy for {topic}. Original footage style, no logos.",
        "description": "Ambient stadium B-roll clip.",
        "tags": ["b_roll", "sports"],
        "parameters": {"video_type": "b_roll"},
    },
    {
        "title": "Drone — aerial venue reveal",
        "module": "video",
        "prompt_template": "Drone-style aerial reveal sweeping over a sports venue related to {topic}. Golden hour, original scene.",
        "description": "Aerial establishing shot.",
        "tags": ["drone"],
        "parameters": {"video_type": "drone"},
    },
    {
        "title": "Sports intro — team legacy",
        "module": "video",
        "prompt_template": "High-energy sports broadcast intro for {topic}. Bold typography motion, original graphics only.",
        "description": "Broadcast-style opener.",
        "tags": ["sports_intro"],
        "parameters": {"video_type": "sports_intro"},
    },
    {
        "title": "Motion graphics — stats lower third",
        "module": "video",
        "prompt_template": "Clean motion graphics lower-third animation highlighting key stats for {topic}.",
        "description": "Data-driven motion graphic.",
        "tags": ["motion_graphics"],
        "parameters": {"video_type": "motion_graphics"},
    },
    {
        "title": "Cinematic — slow motion highlight",
        "module": "video",
        "prompt_template": "Cinematic slow-motion style highlight moment for {topic}. Dramatic lighting, original composition.",
        "description": "Emotional slow-motion beat.",
        "tags": ["slow_motion", "cinematic"],
        "parameters": {"video_type": "slow_motion"},
    },
]


class VideoStudioService:
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
            "video_type": params.get("video_type", "b_roll"),
            "duration_seconds": params.get("duration_seconds", 8),
            "aspect_ratio": params.get("aspect_ratio", "16:9"),
            "provider": gen.provider or "demo",
            "status": gen.status,
            "output_text": gen.output_text,
            "output_meta": gen.output_meta,
            "progress": meta.get("progress", 0),
            "stage": meta.get("stage"),
            "preview_url": meta.get("poster_url") or meta.get("preview_url"),
            "mime_type": meta.get("mime_type"),
            "result_url": gen.result_url,
            "r2_key": gen.r2_key,
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
    def _video_query(db: Session):
        return (
            db.query(AIGeneration, User)
            .outerjoin(User, User.id == AIGeneration.created_by_id)
            .filter(AIGeneration.module == _VIDEO_MODULE)
            .order_by(AIGeneration.created_at.desc())
        )

    @staticmethod
    def _status_counts(db: Session) -> dict[str, int]:
        rows = (
            db.query(AIGeneration.status, func.count(AIGeneration.id))
            .filter(AIGeneration.module == _VIDEO_MODULE)
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
        VideoStudioService.seed_video_prompts(db)
        return {
            "video_types": [
                {"id": t, "label": t.replace("_", " ").title()} for t in VIDEO_TYPES
            ],
            "providers": get_video_registry().list_providers(),
            "queue_counts": VideoStudioService._status_counts(db),
        }

    @staticmethod
    def create_generation(db: Session, user: User, data: VideoGenerateCreate) -> AIGeneration:
        if data.project_id:
            StudioPlatformService.require_permission(db, user, data.project_id, "ai.generate")
        else:
            StudioPlatformService.require_permission(db, user, None, "ai.generate")

        violation = validate_video_prompt(data.prompt)
        if violation:
            raise ConflictError(violation)

        video_type = data.video_type if data.video_type in VIDEO_TYPES else "b_roll"
        params = {
            "video_type": video_type,
            "duration_seconds": max(4, min(data.duration_seconds, 30)),
            "aspect_ratio": data.aspect_ratio,
            "fps": data.fps,
            **(data.parameters or {}),
        }

        gen = AIGeneration(
            project_id=data.project_id,
            module=_VIDEO_MODULE,
            prompt=data.prompt,
            parameters=params,
            provider=data.provider or get_video_registry().resolve().id,
            status=AIGenerationStatus.QUEUED,
            created_by_id=user.id,
        )
        db.add(gen)
        db.flush()

        from app.workers.studio_tasks import run_ai_generation

        task = run_ai_generation.delay(gen.id)
        gen.celery_task_id = task.id
        StudioPlatformService.log_activity(db, user.id, "video.job_queued", data.project_id, "ai_generation", gen.id)
        db.commit()
        db.refresh(gen)
        return gen

    @staticmethod
    def execute_video_job(db: Session, generation_id: int) -> None:
        gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
        if not gen or gen.status == AIGenerationStatus.CANCELLED:
            return

        violation = validate_video_prompt(gen.prompt)
        if violation:
            gen.status = AIGenerationStatus.FAILED
            gen.error = violation
            db.commit()
            return

        gen.status = AIGenerationStatus.RUNNING
        gen.started_at = datetime.now(timezone.utc)
        gen.output_meta = {"progress": 0, "stage": "starting"}
        db.commit()

        params = gen.parameters or {}
        video_type = params.get("video_type", "b_roll")
        aspect = params.get("aspect_ratio", "16:9")
        duration = int(params.get("duration_seconds", 8))
        fps = int(params.get("fps", 24))
        width, height = _ASPECT_MAP.get(aspect, (1280, 720))

        try:
            for stage, pct in _PROGRESS_STAGES:
                gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
                if not gen or gen.status == AIGenerationStatus.CANCELLED:
                    return
                VideoStudioService._set_progress(db, gen, stage, pct)
                time.sleep(0.4)

            gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
            if not gen or gen.status == AIGenerationStatus.CANCELLED:
                return

            result = get_video_registry().generate(
                VideoGenerateRequest(
                    prompt=gen.prompt,
                    video_type=video_type,
                    duration_seconds=duration,
                    aspect_ratio=aspect,
                    fps=fps,
                    width=width,
                    height=height,
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
            meta["preview_url"] = result.preview_url
            meta["duration_seconds"] = result.duration_seconds
            gen.output_meta = meta
            gen.result_url = result.result_url
            gen.r2_key = result.r2_key
            gen.provider = result.provider

            VideoStudioService._save_version(
                db,
                gen.id,
                gen.created_by_id,
                result.result_url,
                result.r2_key,
                meta,
                label="v1",
            )

            if gen.created_by_id:
                db.add(
                    StudioNotification(
                        user_id=gen.created_by_id,
                        notification_type="video_job_complete",
                        title=f"Video ready — {video_type.replace('_', ' ')}",
                        body=gen.prompt[:120],
                        data={
                            "generation_id": gen.id,
                            "video_type": video_type,
                            "result_url": gen.result_url,
                            "preview_url": result.preview_url,
                        },
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
    ) -> AIVideoVersion:
        latest = (
            db.query(func.max(AIVideoVersion.version))
            .filter(AIVideoVersion.generation_id == generation_id)
            .scalar()
            or 0
        )
        row = AIVideoVersion(
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
        q = VideoStudioService._video_query(db)
        queued = q.filter(AIGeneration.status == AIGenerationStatus.QUEUED).limit(50).all()
        running = q.filter(AIGeneration.status == AIGenerationStatus.RUNNING).limit(20).all()
        return {
            "queued": [VideoStudioService._job_dict(g, u.full_name if u else None) for g, u in queued],
            "running": [VideoStudioService._job_dict(g, u.full_name if u else None) for g, u in running],
            "counts": VideoStudioService._status_counts(db),
        }

    @staticmethod
    def get_history(
        db: Session,
        user: User,
        video_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        q = VideoStudioService._video_query(db)
        if video_type:
            q = q.filter(AIGeneration.parameters.contains({"video_type": video_type}))
        total = q.count()
        rows = q.offset(offset).limit(limit).all()
        return {
            "items": [VideoStudioService._job_dict(g, u.full_name if u else None) for g, u in rows],
            "total": total,
        }

    @staticmethod
    def list_versions(db: Session, user: User, generation_id: int) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        rows = (
            db.query(AIVideoVersion)
            .filter(AIVideoVersion.generation_id == generation_id)
            .order_by(AIVideoVersion.version.desc())
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
            raise NotFoundError("Video generation")
        StudioPlatformService.require_permission(db, user, gen.project_id, "asset.upload")
        video_type = (gen.parameters or {}).get("video_type", "b_roll")
        meta = gen.output_meta or {}
        asset = StudioAsset(
            project_id=gen.project_id,
            title=gen.prompt[:200],
            asset_type=AssetType.VIDEO,
            folder="videos",
            filename=gen.r2_key.rsplit("/", 1)[-1],
            r2_key=gen.r2_key,
            url=gen.result_url,
            preview_url=meta.get("poster_url") or meta.get("preview_url") or gen.result_url,
            size_bytes=meta.get("size_bytes", 0),
            mime_type=meta.get("mime_type", "text/html"),
            tags=["ai-generated", video_type],
            cloud_provider=gen.provider,
            meta={"generation_id": gen.id, "duration_seconds": meta.get("duration_seconds")},
            uploaded_by_id=user.id,
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)
        return {"asset_id": asset.id, "url": asset.url, "folder": asset.folder}

    @staticmethod
    def seed_video_prompts(db: Session) -> None:
        for item in _DEFAULT_VIDEO_PROMPTS:
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
    def list_prompts(db: Session, user: User, video_type: str | None = None) -> list[dict]:
        from app.services.ai_studio_service import AIStudioService

        VideoStudioService.seed_video_prompts(db)
        prompts = AIStudioService.list_prompts(db, user, None)
        filtered = [p for p in prompts if p["module"] == "video"]
        if video_type:
            filtered = [p for p in filtered if (p.get("parameters") or {}).get("video_type") == video_type]
        return filtered
