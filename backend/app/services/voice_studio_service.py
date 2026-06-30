"""AI Voice Studio — narration queue, preview, subtitles, translation, storage."""

from __future__ import annotations

import time
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.domain.studio.enums import AIGenerationModule, AIGenerationStatus, AssetType
from app.domain.voice.providers.registry import get_voice_registry
from app.domain.voice.translation import demo_translate
from app.domain.voice.types import VOICE_EMOTIONS, VOICE_LANGUAGES, VOICES_BY_LANGUAGE, VoiceGenerateRequest
from app.models import User
from app.models.studio_platform import (
    AIGeneration,
    AIPromptLibrary,
    AIVoiceVersion,
    StudioAsset,
    StudioNotification,
)
from app.schemas.voice_studio import VoiceGenerateCreate, VoicePreviewCreate, VoiceTranslateCreate
from app.services.studio_platform_service import StudioPlatformService

_VOICE_MODULE = AIGenerationModule.VOICE
_LANG_CODES = {code for code, _ in VOICE_LANGUAGES}

_PROGRESS_STAGES = [
    ("validating", 10),
    ("synthesizing", 45),
    ("syncing_subtitles", 75),
    ("uploading", 92),
]

_DEFAULT_VOICE_PROMPTS = [
    {
        "title": "Documentary opener — English",
        "module": "voice",
        "prompt_template": "Welcome to an untold story about {topic}. Tonight we explore the moments that changed everything.",
        "description": "Neutral documentary narration opener.",
        "tags": ["narration", "en"],
        "parameters": {"language": "en", "emotion": "neutral"},
    },
    {
        "title": "Hindi sports recap",
        "module": "voice",
        "prompt_template": "Aaj hum {topic} ki sabse yaadgar palon par nazar daalenge — jahan junoon ne itihaas likha.",
        "description": "Warm Hindi recap narration.",
        "tags": ["narration", "hi"],
        "parameters": {"language": "hi", "emotion": "warm"},
    },
    {
        "title": "Arabic highlight reel",
        "module": "voice",
        "prompt_template": "في هذه اللحظات الأسطورية من {topic}، نعيش شغف الرياضة بكل تفاصيله.",
        "description": "Authoritative Arabic sports narration.",
        "tags": ["narration", "ar"],
        "parameters": {"language": "ar", "emotion": "authoritative"},
    },
    {
        "title": "Spanish episode intro",
        "module": "voice",
        "prompt_template": "En este episodio sobre {topic}, descubrimos las historias que merecen ser contadas.",
        "description": "Energetic Spanish intro.",
        "tags": ["narration", "es"],
        "parameters": {"language": "es", "emotion": "energetic"},
    },
]


class VoiceStudioService:
    @staticmethod
    def _job_dict(gen: AIGeneration, author_name: str | None = None) -> dict:
        params = gen.parameters or {}
        meta = gen.output_meta or {}
        return {
            "id": gen.id,
            "project_id": gen.project_id,
            "module": gen.module,
            "text": gen.prompt,
            "prompt": gen.prompt,
            "parameters": gen.parameters,
            "language": params.get("language", "en"),
            "emotion": params.get("emotion", "neutral"),
            "pitch": params.get("pitch", 1.0),
            "speed": params.get("speed", 1.0),
            "voice_id": params.get("voice_id", "en-documentary"),
            "translate_to": params.get("translate_to"),
            "sync_subtitles": params.get("sync_subtitles", True),
            "provider": gen.provider or "demo",
            "status": gen.status,
            "output_text": gen.output_text,
            "output_meta": gen.output_meta,
            "progress": meta.get("progress", 0),
            "stage": meta.get("stage"),
            "duration_seconds": meta.get("duration_seconds"),
            "subtitles_url": meta.get("subtitles_url"),
            "translated_text": meta.get("translated_text"),
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
    def _voice_query(db: Session):
        return (
            db.query(AIGeneration, User)
            .outerjoin(User, User.id == AIGeneration.created_by_id)
            .filter(AIGeneration.module == _VOICE_MODULE)
            .order_by(AIGeneration.created_at.desc())
        )

    @staticmethod
    def _status_counts(db: Session) -> dict[str, int]:
        rows = (
            db.query(AIGeneration.status, func.count(AIGeneration.id))
            .filter(AIGeneration.module == _VOICE_MODULE)
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
    def _build_request(data: VoiceGenerateCreate | VoicePreviewCreate) -> VoiceGenerateRequest:
        language = data.language if data.language in _LANG_CODES else "en"
        emotion = data.emotion if data.emotion in VOICE_EMOTIONS else "neutral"
        voices = VOICES_BY_LANGUAGE.get(language, [])
        voice_ids = {v["id"] for v in voices}
        voice_id = data.voice_id if data.voice_id in voice_ids else (voices[0]["id"] if voices else "en-documentary")
        translate_to = data.translate_to if data.translate_to in _LANG_CODES else None
        return VoiceGenerateRequest(
            text=data.text.strip(),
            language=language,
            emotion=emotion,
            pitch=max(0.5, min(data.pitch, 2.0)),
            speed=max(0.5, min(data.speed, 2.0)),
            voice_id=voice_id,
            translate_to=translate_to,
            sync_subtitles=data.sync_subtitles,
            project_id=data.project_id,
        )

    @staticmethod
    def get_overview(db: Session, user: User) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        VoiceStudioService.seed_voice_prompts(db)
        return {
            "languages": [{"id": code, "label": label} for code, label in VOICE_LANGUAGES],
            "emotions": [{"id": e, "label": e.replace("_", " ").title()} for e in VOICE_EMOTIONS],
            "voices_by_language": VOICES_BY_LANGUAGE,
            "providers": get_voice_registry().list_providers(),
            "queue_counts": VoiceStudioService._status_counts(db),
        }

    @staticmethod
    def create_generation(db: Session, user: User, data: VoiceGenerateCreate) -> AIGeneration:
        if data.project_id:
            StudioPlatformService.require_permission(db, user, data.project_id, "ai.generate")
        else:
            StudioPlatformService.require_permission(db, user, None, "ai.generate")

        if not data.text.strip():
            raise ConflictError("Narration text is required")

        req = VoiceStudioService._build_request(data)
        params = {
            "language": req.language,
            "emotion": req.emotion,
            "pitch": req.pitch,
            "speed": req.speed,
            "voice_id": req.voice_id,
            "translate_to": req.translate_to,
            "sync_subtitles": req.sync_subtitles,
            **(data.parameters or {}),
        }

        gen = AIGeneration(
            project_id=data.project_id,
            module=_VOICE_MODULE,
            prompt=data.text.strip(),
            parameters=params,
            provider=data.provider or get_voice_registry().resolve().id,
            status=AIGenerationStatus.QUEUED,
            created_by_id=user.id,
        )
        db.add(gen)
        db.flush()

        from app.workers.studio_tasks import run_ai_generation

        task = run_ai_generation.delay(gen.id)
        gen.celery_task_id = task.id
        StudioPlatformService.log_activity(db, user.id, "voice.job_queued", data.project_id, "ai_generation", gen.id)
        db.commit()
        db.refresh(gen)
        return gen

    @staticmethod
    def preview(db: Session, user: User, data: VoicePreviewCreate) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        if not data.text.strip():
            raise ConflictError("Preview text is required")
        req = VoiceStudioService._build_request(data)
        result = get_voice_registry().preview(req, provider_id=data.provider)
        return {
            "audio_url": result.result_url,
            "duration_seconds": result.duration_seconds,
            "provider": result.provider,
            "mime_type": result.mime_type,
        }

    @staticmethod
    def translate_text(db: Session, user: User, data: VoiceTranslateCreate) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        source = data.language if data.language in _LANG_CODES else "en"
        target = data.translate_to if data.translate_to in _LANG_CODES else "en"
        translated = demo_translate(data.text.strip(), source, target)
        return {
            "source_language": source,
            "target_language": target,
            "original_text": data.text.strip(),
            "translated_text": translated,
        }

    @staticmethod
    def execute_voice_job(db: Session, generation_id: int) -> None:
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
                VoiceStudioService._set_progress(db, gen, stage, pct)
                time.sleep(0.35)

            gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
            if not gen or gen.status == AIGenerationStatus.CANCELLED:
                return

            result = get_voice_registry().generate(
                VoiceGenerateRequest(
                    text=gen.prompt,
                    language=params.get("language", "en"),
                    emotion=params.get("emotion", "neutral"),
                    pitch=float(params.get("pitch", 1.0)),
                    speed=float(params.get("speed", 1.0)),
                    voice_id=params.get("voice_id", "en-documentary"),
                    translate_to=params.get("translate_to"),
                    sync_subtitles=bool(params.get("sync_subtitles", True)),
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
            meta["duration_seconds"] = result.duration_seconds
            meta["subtitles_url"] = result.subtitles_url
            meta["subtitles_srt"] = result.subtitles_srt
            meta["subtitles_vtt"] = result.subtitles_vtt
            meta["translated_text"] = result.translated_text
            gen.output_meta = meta
            gen.result_url = result.result_url
            gen.r2_key = result.r2_key
            gen.provider = result.provider

            VoiceStudioService._save_version(
                db, gen.id, gen.created_by_id, result.result_url, result.r2_key, meta, label="v1",
            )

            if gen.created_by_id:
                db.add(
                    StudioNotification(
                        user_id=gen.created_by_id,
                        notification_type="voice_job_complete",
                        title=f"Narration ready — {params.get('language', 'en').upper()}",
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
    ) -> AIVoiceVersion:
        latest = (
            db.query(func.max(AIVoiceVersion.version))
            .filter(AIVoiceVersion.generation_id == generation_id)
            .scalar()
            or 0
        )
        row = AIVoiceVersion(
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
        q = VoiceStudioService._voice_query(db)
        queued = q.filter(AIGeneration.status == AIGenerationStatus.QUEUED).limit(50).all()
        running = q.filter(AIGeneration.status == AIGenerationStatus.RUNNING).limit(20).all()
        return {
            "queued": [VoiceStudioService._job_dict(g, u.full_name if u else None) for g, u in queued],
            "running": [VoiceStudioService._job_dict(g, u.full_name if u else None) for g, u in running],
            "counts": VoiceStudioService._status_counts(db),
        }

    @staticmethod
    def get_history(
        db: Session,
        user: User,
        language: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        q = VoiceStudioService._voice_query(db)
        if language:
            q = q.filter(AIGeneration.parameters.contains({"language": language}))
        total = q.count()
        rows = q.offset(offset).limit(limit).all()
        return {
            "items": [VoiceStudioService._job_dict(g, u.full_name if u else None) for g, u in rows],
            "total": total,
        }

    @staticmethod
    def get_job_subtitles(db: Session, user: User, job_id: int) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        gen = db.query(AIGeneration).filter(AIGeneration.id == job_id, AIGeneration.module == _VOICE_MODULE).first()
        if not gen:
            raise NotFoundError("Voice generation")
        meta = gen.output_meta or {}
        return {
            "srt": meta.get("subtitles_srt"),
            "vtt": meta.get("subtitles_vtt"),
            "subtitles_url": meta.get("subtitles_url"),
        }

    @staticmethod
    def list_versions(db: Session, user: User, generation_id: int) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        rows = (
            db.query(AIVoiceVersion)
            .filter(AIVoiceVersion.generation_id == generation_id)
            .order_by(AIVoiceVersion.version.desc())
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
            raise NotFoundError("Voice generation")
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
            tags=["ai-generated", "narration", params.get("language", "en")],
            cloud_provider=gen.provider,
            meta={
                "generation_id": gen.id,
                "subtitles_url": meta.get("subtitles_url"),
                "duration_seconds": meta.get("duration_seconds"),
            },
            uploaded_by_id=user.id,
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)
        return {"asset_id": asset.id, "url": asset.url, "folder": asset.folder}

    @staticmethod
    def seed_voice_prompts(db: Session) -> None:
        for item in _DEFAULT_VOICE_PROMPTS:
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
    def list_prompts(db: Session, user: User, language: str | None = None) -> list[dict]:
        from app.services.ai_studio_service import AIStudioService

        VoiceStudioService.seed_voice_prompts(db)
        prompts = AIStudioService.list_prompts(db, user, None)
        filtered = [p for p in prompts if p["module"] == "voice"]
        if language:
            filtered = [p for p in filtered if (p.get("parameters") or {}).get("language") == language]
        return filtered
