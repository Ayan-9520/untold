"""AI Shorts Studio — highlight detection, vertical clips, publishing queue."""

from __future__ import annotations

import time
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.domain.shorts.providers.registry import get_shorts_registry
from app.domain.shorts.types import PUBLISH_PLATFORM_MAP, SHORTS_PLATFORMS, ShortsGenerateRequest
from app.domain.studio.enums import AIGenerationModule, AIGenerationStatus, AssetType, PublishPlatform
from app.models import User
from app.models.studio_platform import (
    AIGeneration,
    AIShortsVersion,
    PublishJob,
    StudioAsset,
    StudioNotification,
)
from app.schemas.shorts_studio import ShortsGenerateCreate, ShortsQueuePublishCreate
from app.services.studio_platform_service import StudioPlatformService

_SHORTS_MODULE = AIGenerationModule.SHORTS

_PROGRESS_STAGES = [
    ("analyzing", 15),
    ("detecting_highlights", 35),
    ("cropping_vertical", 55),
    ("adding_captions", 75),
    ("exporting", 92),
]


class ShortsStudioService:
    @staticmethod
    def _job_dict(gen: AIGeneration, author_name: str | None = None) -> dict:
        params = gen.parameters or {}
        meta = gen.output_meta or {}
        return {
            "id": gen.id,
            "project_id": gen.project_id,
            "module": gen.module,
            "prompt": gen.prompt,
            "topic": params.get("topic", gen.prompt),
            "source_video_url": params.get("source_video_url"),
            "parameters": gen.parameters,
            "platforms": params.get("platforms", []),
            "auto_highlights": params.get("auto_highlights", True),
            "captions": params.get("captions", True),
            "auto_zoom": params.get("auto_zoom", True),
            "hook_optimization": params.get("hook_optimization", True),
            "provider": gen.provider or "demo",
            "status": gen.status,
            "output_text": gen.output_text,
            "output_meta": gen.output_meta,
            "progress": meta.get("progress", 0),
            "stage": meta.get("stage"),
            "highlights": meta.get("highlights", []),
            "clips": meta.get("clips", []),
            "thumbnail_url": meta.get("thumbnail_url"),
            "hashtags": meta.get("hashtags", []),
            "hook": meta.get("hook"),
            "publish_queue": meta.get("publish_queue", []),
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
    def _shorts_query(db: Session):
        return (
            db.query(AIGeneration, User)
            .outerjoin(User, User.id == AIGeneration.created_by_id)
            .filter(AIGeneration.module == _SHORTS_MODULE)
            .order_by(AIGeneration.created_at.desc())
        )

    @staticmethod
    def _status_counts(db: Session) -> dict[str, int]:
        rows = (
            db.query(AIGeneration.status, func.count(AIGeneration.id))
            .filter(AIGeneration.module == _SHORTS_MODULE)
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
            "platforms": [
                {"id": p, "label": p.replace("_", " ").title()} for p in SHORTS_PLATFORMS
            ],
            "providers": get_shorts_registry().list_providers(),
            "queue_counts": ShortsStudioService._status_counts(db),
        }

    @staticmethod
    def create_generation(db: Session, user: User, data: ShortsGenerateCreate) -> AIGeneration:
        if data.project_id:
            StudioPlatformService.require_permission(db, user, data.project_id, "ai.generate")
        else:
            StudioPlatformService.require_permission(db, user, None, "ai.generate")

        if not data.source_video_url.strip():
            raise ConflictError("Source video URL is required")

        platforms = [p for p in (data.platforms or SHORTS_PLATFORMS) if p in SHORTS_PLATFORMS]
        if not platforms:
            platforms = list(SHORTS_PLATFORMS)

        topic = data.topic.strip() or "UNTOLD highlight reel"
        params = {
            "source_video_url": data.source_video_url.strip(),
            "topic": topic,
            "platforms": platforms,
            "auto_highlights": data.auto_highlights,
            "captions": data.captions,
            "auto_zoom": data.auto_zoom,
            "hook_optimization": data.hook_optimization,
            "clip_duration_seconds": data.clip_duration_seconds,
            "aspect_ratio": "9:16",
            **(data.parameters or {}),
        }

        gen = AIGeneration(
            project_id=data.project_id,
            module=_SHORTS_MODULE,
            prompt=topic,
            parameters=params,
            provider=data.provider or get_shorts_registry().resolve().id,
            status=AIGenerationStatus.QUEUED,
            created_by_id=user.id,
        )
        db.add(gen)
        db.flush()

        from app.workers.studio_tasks import run_ai_generation

        task = run_ai_generation.delay(gen.id)
        gen.celery_task_id = task.id
        StudioPlatformService.log_activity(db, user.id, "shorts.job_queued", data.project_id, "ai_generation", gen.id)
        db.commit()
        db.refresh(gen)
        return gen

    @staticmethod
    def execute_shorts_job(db: Session, generation_id: int) -> None:
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
                ShortsStudioService._set_progress(db, gen, stage, pct)
                time.sleep(0.35)

            gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
            if not gen or gen.status == AIGenerationStatus.CANCELLED:
                return

            result = get_shorts_registry().generate(
                ShortsGenerateRequest(
                    source_video_url=params.get("source_video_url", ""),
                    topic=params.get("topic", gen.prompt),
                    platforms=params.get("platforms", list(SHORTS_PLATFORMS)),
                    auto_highlights=bool(params.get("auto_highlights", True)),
                    captions=bool(params.get("captions", True)),
                    auto_zoom=bool(params.get("auto_zoom", True)),
                    hook_optimization=bool(params.get("hook_optimization", True)),
                    clip_duration_seconds=int(params.get("clip_duration_seconds", 30)),
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
            meta["highlights"] = result.highlights
            meta["clips"] = result.clips
            meta["thumbnail_url"] = result.thumbnail_url
            meta["hashtags"] = result.hashtags
            meta["hook"] = result.hook
            meta["captions_vtt"] = result.captions_vtt
            meta["mime_type"] = result.mime_type
            meta["publish_queue"] = []
            gen.output_meta = meta
            gen.result_url = result.result_url
            gen.r2_key = result.r2_key
            gen.provider = result.provider

            ShortsStudioService._save_version(
                db, gen.id, gen.created_by_id, result.result_url, result.r2_key, meta, label="v1",
            )

            if gen.created_by_id:
                db.add(
                    StudioNotification(
                        user_id=gen.created_by_id,
                        notification_type="shorts_job_complete",
                        title="Shorts pack ready",
                        body=gen.prompt[:120],
                        data={"generation_id": gen.id, "clips": len(result.clips)},
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
    ) -> AIShortsVersion:
        latest = (
            db.query(func.max(AIShortsVersion.version))
            .filter(AIShortsVersion.generation_id == generation_id)
            .scalar()
            or 0
        )
        row = AIShortsVersion(
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
        q = ShortsStudioService._shorts_query(db)
        queued = q.filter(AIGeneration.status == AIGenerationStatus.QUEUED).limit(50).all()
        running = q.filter(AIGeneration.status == AIGenerationStatus.RUNNING).limit(20).all()
        return {
            "queued": [ShortsStudioService._job_dict(g, u.full_name if u else None) for g, u in queued],
            "running": [ShortsStudioService._job_dict(g, u.full_name if u else None) for g, u in running],
            "counts": ShortsStudioService._status_counts(db),
        }

    @staticmethod
    def get_history(db: Session, user: User, limit: int = 50, offset: int = 0) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        q = ShortsStudioService._shorts_query(db)
        total = q.count()
        rows = q.offset(offset).limit(limit).all()
        return {
            "items": [ShortsStudioService._job_dict(g, u.full_name if u else None) for g, u in rows],
            "total": total,
        }

    @staticmethod
    def queue_for_publishing(
        db: Session, user: User, generation_id: int, data: ShortsQueuePublishCreate,
    ) -> dict:
        gen = db.query(AIGeneration).filter(
            AIGeneration.id == generation_id, AIGeneration.module == _SHORTS_MODULE,
        ).first()
        if not gen or gen.status != AIGenerationStatus.COMPLETED:
            raise ConflictError("Only completed shorts jobs can be queued for publishing")
        if not gen.project_id:
            raise ConflictError("Project is required to queue publishing")

        StudioPlatformService.require_permission(db, user, gen.project_id, "publish.schedule")
        meta = dict(gen.output_meta or {})
        clips = meta.get("clips", [])
        platforms = data.platforms or [c.get("platform") for c in clips]
        hook = meta.get("hook", gen.prompt)
        hashtags = meta.get("hashtags", [])
        thumb = meta.get("thumbnail_url")
        created_jobs: list[dict] = []

        for plat in platforms:
            pub_plat_key = PUBLISH_PLATFORM_MAP.get(plat, "youtube")
            try:
                pub_plat = PublishPlatform(pub_plat_key)
            except ValueError:
                continue
            job = PublishJob(
                project_id=gen.project_id,
                platform=pub_plat,
                status="pending_approval",
                approval_status="pending",
                requires_approval=True,
                created_by_id=user.id,
                seo_title=hook[:500],
                seo_description=f"{gen.prompt[:200]} {' '.join(hashtags[:5])}",
                seo_keywords=hashtags[:10],
                thumbnail_url=thumb,
                meta={"shorts_generation_id": gen.id, "shorts_platform": plat},
            )
            db.add(job)
            db.flush()
            created_jobs.append({"publish_job_id": job.id, "platform": plat, "status": job.status})

        meta["publish_queue"] = created_jobs
        gen.output_meta = meta
        db.commit()
        return {"publish_jobs": created_jobs, "count": len(created_jobs)}

    @staticmethod
    def save_to_asset_library(db: Session, user: User, generation_id: int) -> dict:
        gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
        if not gen or not gen.r2_key:
            raise NotFoundError("Shorts generation")
        StudioPlatformService.require_permission(db, user, gen.project_id, "asset.upload")
        meta = gen.output_meta or {}
        asset = StudioAsset(
            project_id=gen.project_id,
            title=gen.prompt[:200],
            asset_type=AssetType.VIDEO,
            folder="videos",
            filename=gen.r2_key.rsplit("/", 1)[-1],
            r2_key=gen.r2_key,
            url=gen.result_url,
            preview_url=meta.get("thumbnail_url") or gen.result_url,
            mime_type=meta.get("mime_type", "text/html"),
            tags=["ai-generated", "shorts", "9:16"],
            cloud_provider=gen.provider,
            meta={"generation_id": gen.id, "clips": meta.get("clips")},
            uploaded_by_id=user.id,
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)
        return {"asset_id": asset.id, "url": asset.url, "folder": asset.folder}
