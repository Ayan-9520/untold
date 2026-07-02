"""AI Studio — queue, history, prompt library, provider abstraction."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.domain.ai.providers.registry import get_provider_registry
from app.domain.ai.types import AIJobRequest
from app.domain.studio.enums import AIGenerationModule, AIGenerationStatus
from app.models import User
from app.models.studio_platform import AIGeneration, AIPromptLibrary, StudioNotification
from app.schemas.ai_studio import (
    AIGenerationCreate,
    AIModuleInfo,
    AIPromptCreate,
    AIPromptUpdate,
)
from app.services.generation_telemetry_service import (
    apply_create_defaults,
    apply_failure,
    finalize_generation_success,
    telemetry_dict,
)
from app.domain.tenancy.ai_scope import (
    resolve_generation_organization_id,
    scope_ai_generations_query,
)
from app.services.studio_platform_service import StudioPlatformService

_MODULE_CATALOG: list[AIModuleInfo] = [
    AIModuleInfo(id="research", label="Research AI", description="Summaries, angles, and source strategies.", output_type="text"),
    AIModuleInfo(id="script", label="Script AI", description="Draft and refine documentary narration.", output_type="text"),
    AIModuleInfo(id="image", label="Image AI", description="Concept frames and still references.", output_type="media"),
    AIModuleInfo(id="video", label="Video AI", description="B-roll beats and motion prompts.", output_type="media"),
    AIModuleInfo(id="voice", label="Voice AI", description="Narration scripts and voice-over text.", output_type="text"),
    AIModuleInfo(id="music", label="Music AI", description="Score briefs and mood direction.", output_type="text"),
    AIModuleInfo(id="thumbnail", label="Thumbnail AI", description="CTR-focused thumbnail concepts.", output_type="media"),
    AIModuleInfo(id="seo", label="SEO AI", description="Titles, meta, tags, and schema.", output_type="text"),
    AIModuleInfo(id="translation", label="Translation AI", description="Localize scripts and metadata.", output_type="text"),
]

_DEFAULT_PROMPTS: list[dict] = [
    {
        "title": "Research brief from topic",
        "module": "research",
        "prompt_template": "Create a research brief for a documentary about: {topic}\n\nInclude timeline, key figures, controversies, and 5 primary sources to verify.",
        "description": "Kick off research with structured angles.",
        "tags": ["research", "brief"],
    },
    {
        "title": "Opening narration",
        "module": "script",
        "prompt_template": "Write a 45-second opening narration for: {topic}\n\nTone: cinematic documentary. Hook with a defining moment.",
        "description": "Strong cold open for scripts.",
        "tags": ["script", "opening"],
    },
    {
        "title": "Thumbnail CTR concepts",
        "module": "thumbnail",
        "prompt_template": "Generate 5 YouTube thumbnail concepts for: {topic}\n\nInclude composition, text overlay, and emotion.",
        "description": "High-CTR thumbnail ideation.",
        "tags": ["thumbnail", "youtube"],
    },
    {
        "title": "SEO title pack",
        "module": "seo",
        "prompt_template": "Write 10 SEO titles (max 60 chars) and a meta description for: {topic}",
        "description": "Publishing-ready SEO copy.",
        "tags": ["seo", "titles"],
    },
    {
        "title": "Translate script excerpt",
        "module": "translation",
        "prompt_template": "Translate to {language}:\n\n{excerpt}",
        "description": "Localization helper.",
        "tags": ["translation"],
        "parameters": {"language": "es"},
    },
]


class AIStudioService:
    @staticmethod
    def _job_dict(
        gen: AIGeneration,
        author_name: str | None = None,
        project_title: str | None = None,
    ) -> dict:
        tel = telemetry_dict(gen)
        return {
            "id": gen.id,
            "project_id": gen.project_id,
            "project_title": project_title,
            "module": gen.module,
            "prompt": gen.prompt,
            "parameters": gen.parameters,
            "provider": gen.provider or "demo",
            "status": gen.status,
            "output_text": gen.output_text,
            "output_meta": gen.output_meta,
            "result_url": gen.result_url,
            "error": gen.error,
            "retry_count": gen.retry_count or 0,
            "created_by_id": gen.created_by_id,
            "author_name": author_name,
            "created_at": gen.created_at,
            "started_at": gen.started_at,
            "completed_at": gen.completed_at,
            "cancelled_at": gen.cancelled_at,
            **tel,
        }

    @staticmethod
    def get_overview(db: Session, user: User) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        registry = get_provider_registry()
        counts = AIStudioService._status_counts(db, user)
        return {
            "modules": _MODULE_CATALOG,
            "providers": registry.list_providers(),
            "queue_counts": counts,
        }

    @staticmethod
    def _status_counts(db: Session, user: User) -> dict[str, int]:
        base_query = scope_ai_generations_query(db, user, db.query(AIGeneration))
        rows = base_query.with_entities(AIGeneration.status, func.count(AIGeneration.id)).group_by(AIGeneration.status).all()
        base = {s.value: 0 for s in AIGenerationStatus}
        for status, count in rows:
            key = status.value if hasattr(status, "value") else str(status)
            base[key] = count
        return base

    @staticmethod
    def create_generation(db: Session, user: User, data: AIGenerationCreate) -> AIGeneration:
        if data.project_id:
            StudioPlatformService.require_permission(db, user, data.project_id, "ai.generate")
        else:
            StudioPlatformService.require_permission(db, user, None, "ai.generate")

        registry = get_provider_registry()
        provider_id = data.provider
        if provider_id:
            provider = registry.get(provider_id)
            if not provider or not provider.is_available():
                provider_id = registry.resolve(data.module.value, None).id
        else:
            provider_id = registry.resolve(data.module.value, None).id

        gen = AIGeneration(
            project_id=data.project_id,
            organization_id=resolve_generation_organization_id(db, user, data.project_id),
            module=data.module,
            prompt=data.prompt,
            parameters=data.parameters,
            provider=provider_id,
            status=AIGenerationStatus.QUEUED,
            created_by_id=user.id,
        )
        apply_create_defaults(gen)
        db.add(gen)
        db.flush()

        from app.workers.studio_tasks import run_ai_generation

        task = run_ai_generation.delay(gen.id)
        gen.celery_task_id = task.id
        StudioPlatformService.log_activity(
            db, user.id, "ai.job_queued", data.project_id, "ai_generation", gen.id
        )
        db.commit()
        db.refresh(gen)
        return gen

    @staticmethod
    def get_queue(db: Session, user: User) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        queued = AIStudioService._jobs_query(db, user).filter(AIGeneration.status == AIGenerationStatus.QUEUED).limit(50).all()
        running = AIStudioService._jobs_query(db, user).filter(AIGeneration.status == AIGenerationStatus.RUNNING).limit(20).all()
        return {
            "queued": [AIStudioService._job_dict(g, u.full_name if u else None, pt) for g, u, pt in queued],
            "running": [AIStudioService._job_dict(g, u.full_name if u else None, pt) for g, u, pt in running],
            "counts": AIStudioService._status_counts(db, user),
        }

    @staticmethod
    def _jobs_query(db: Session, user: User):
        from app.models.studio import Production

        query = (
            db.query(AIGeneration, User, Production.title)
            .outerjoin(User, User.id == AIGeneration.created_by_id)
            .outerjoin(Production, Production.id == AIGeneration.project_id)
            .order_by(AIGeneration.created_at.desc())
        )
        return scope_ai_generations_query(db, user, query)

    @staticmethod
    def get_history(
        db: Session,
        user: User,
        module: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        q = AIStudioService._jobs_query(db, user)
        if module:
            try:
                mod = AIGenerationModule(module)
                q = q.filter(AIGeneration.module == mod)
            except ValueError:
                pass
        total = q.count()
        rows = q.offset(offset).limit(limit).all()
        return {
            "items": [AIStudioService._job_dict(g, u.full_name if u else None, pt) for g, u, pt in rows],
            "total": total,
        }

    @staticmethod
    def get_telemetry(
        db: Session,
        user: User,
        module: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        q = AIStudioService._jobs_query(db, user)
        if module:
            try:
                mod = AIGenerationModule(module)
                q = q.filter(AIGeneration.module == mod)
            except ValueError:
                pass
        total = q.count()
        rows = q.offset(offset).limit(limit).all()
        items = [AIStudioService._job_dict(g, u.full_name if u else None, pt) for g, u, pt in rows]
        totals = {
            "input_tokens": sum(i["input_tokens"] or 0 for i in items),
            "output_tokens": sum(i["output_tokens"] or 0 for i in items),
            "cost_usd": round(sum(i["cost_usd"] or 0 for i in items), 4),
            "failures": sum(i["failure_count"] or 0 for i in items),
            "retries": sum(i["retries"] or 0 for i in items),
        }
        return {"items": items, "total": total, "totals": totals}

    @staticmethod
    def _get_job_for_user(db: Session, user: User, job_id: int) -> AIGeneration:
        row = (
            AIStudioService._jobs_query(db, user)
            .filter(AIGeneration.id == job_id)
            .first()
        )
        if not row:
            raise NotFoundError("AI job")
        gen, _, _ = row
        return gen

    @staticmethod
    def get_job(db: Session, user: User, job_id: int) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        row = (
            AIStudioService._jobs_query(db, user)
            .filter(AIGeneration.id == job_id)
            .first()
        )
        if not row:
            raise NotFoundError("AI job")
        gen, u, pt = row
        return AIStudioService._job_dict(gen, u.full_name if u else None, pt)

    @staticmethod
    def retry_job(db: Session, user: User, job_id: int) -> AIGeneration:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        gen = AIStudioService._get_job_for_user(db, user, job_id)
        if gen.status not in (AIGenerationStatus.FAILED, AIGenerationStatus.CANCELLED):
            raise ConflictError("Only failed or cancelled jobs can be retried")
        gen.status = AIGenerationStatus.QUEUED
        gen.error = None
        gen.output_text = None
        gen.output_meta = None
        gen.result_url = None
        gen.started_at = None
        gen.completed_at = None
        gen.cancelled_at = None
        gen.retry_count = (gen.retry_count or 0) + 1
        db.flush()
        from app.workers.studio_tasks import run_ai_generation

        task = run_ai_generation.delay(gen.id)
        gen.celery_task_id = task.id
        db.commit()
        db.refresh(gen)
        return gen

    @staticmethod
    def cancel_job(db: Session, user: User, job_id: int) -> AIGeneration:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        gen = AIStudioService._get_job_for_user(db, user, job_id)
        if gen.status not in (AIGenerationStatus.QUEUED, AIGenerationStatus.RUNNING):
            raise ConflictError("Only queued or running jobs can be cancelled")
        gen.status = AIGenerationStatus.CANCELLED
        gen.cancelled_at = datetime.now(timezone.utc)
        if gen.celery_task_id:
            try:
                from app.workers.celery_app import celery_app

                celery_app.control.revoke(gen.celery_task_id, terminate=True)
            except Exception:
                pass
        db.commit()
        db.refresh(gen)
        return gen

    @staticmethod
    def seed_prompt_library(db: Session) -> None:
        if db.query(AIPromptLibrary).count() > 0:
            return
        for item in _DEFAULT_PROMPTS:
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
    def list_prompts(db: Session, user: User, module: str | None = None) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        AIStudioService.seed_prompt_library(db)
        q = (
            db.query(AIPromptLibrary, User)
            .outerjoin(User, User.id == AIPromptLibrary.created_by_id)
            .order_by(AIPromptLibrary.module, AIPromptLibrary.title)
        )
        if module:
            q = q.filter(AIPromptLibrary.module == module)
        return [
            {
                "id": p.id,
                "title": p.title,
                "module": p.module,
                "prompt_template": p.prompt_template,
                "description": p.description,
                "parameters": p.parameters,
                "tags": p.tags or [],
                "is_public": p.is_public,
                "created_by_id": p.created_by_id,
                "author_name": u.full_name if u else None,
                "created_at": p.created_at,
                "updated_at": p.updated_at,
            }
            for p, u in q.all()
        ]

    @staticmethod
    def create_prompt(db: Session, user: User, data: AIPromptCreate) -> AIPromptLibrary:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        prompt = AIPromptLibrary(
            title=data.title,
            module=data.module,
            prompt_template=data.prompt_template,
            description=data.description,
            parameters=data.parameters,
            tags=data.tags,
            is_public=data.is_public,
            created_by_id=user.id,
        )
        db.add(prompt)
        db.commit()
        db.refresh(prompt)
        return prompt

    @staticmethod
    def update_prompt(db: Session, user: User, prompt_id: int, data: AIPromptUpdate) -> AIPromptLibrary:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        prompt = db.query(AIPromptLibrary).filter(AIPromptLibrary.id == prompt_id).first()
        if not prompt:
            raise NotFoundError("Prompt")
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(prompt, key, value)
        db.commit()
        db.refresh(prompt)
        return prompt

    @staticmethod
    def delete_prompt(db: Session, user: User, prompt_id: int) -> None:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        prompt = db.query(AIPromptLibrary).filter(AIPromptLibrary.id == prompt_id).first()
        if not prompt:
            raise NotFoundError("Prompt")
        db.delete(prompt)
        db.commit()

    @staticmethod
    def execute_job(db: Session, generation_id: int) -> None:
        """Called from Celery worker — uses provider registry."""
        gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
        if not gen:
            return
        if gen.status == AIGenerationStatus.CANCELLED:
            return

        from app.services.ai_cost_service import AICostService

        AICostService.check_budgets(db, gen)

        module_val = gen.module.value if hasattr(gen.module, "value") else str(gen.module)
        if module_val in ("image", "thumbnail"):
            from app.services.image_studio_service import ImageStudioService

            ImageStudioService.execute_image_job(db, generation_id)
            return
        if module_val == "video":
            from app.services.video_studio_service import VideoStudioService

            VideoStudioService.execute_video_job(db, generation_id)
            return
        if module_val == "voice":
            from app.services.voice_studio_service import VoiceStudioService

            VoiceStudioService.execute_voice_job(db, generation_id)
            return
        if module_val == "music":
            from app.services.music_studio_service import MusicStudioService

            MusicStudioService.execute_music_job(db, generation_id)
            return
        if module_val == "shorts":
            from app.services.shorts_studio_service import ShortsStudioService

            ShortsStudioService.execute_shorts_job(db, generation_id)
            return
        if module_val == "seo":
            from app.services.seo_studio_service import SEOStudioService

            SEOStudioService.execute_seo_job(db, generation_id)
            return
        if module_val == "translation":
            from app.services.translation_studio_service import TranslationStudioService

            TranslationStudioService.execute_translation_job(db, generation_id)
            return

        gen.status = AIGenerationStatus.RUNNING
        gen.started_at = datetime.now(timezone.utc)
        db.commit()

        cached = AICostService.get_cache_hit(db, module_val, gen.prompt, gen.parameters)
        if cached:
            gen.status = AIGenerationStatus.COMPLETED
            gen.completed_at = datetime.now(timezone.utc)
            gen.output_text = cached.get("output_text")
            gen.output_meta = {k: v for k, v in cached.items() if not k.startswith("_")}
            gen.result_url = cached.get("result_url")
            gen.provider = cached.get("provider") or gen.provider
            meta = dict(gen.output_meta or {})
            meta["cache_hit"] = True
            meta["cost_saved_usd"] = cached.get("_cost_saved_usd", 0)
            meta["cost_usd"] = 0
            finalize_generation_success(
                db, gen, started_at=gen.started_at, output_text=gen.output_text, meta=meta, model=cached.get("model"),
            )
            db.commit()
            return

        provider, model = AICostService.resolve_model_for_generation(db, gen)
        if provider:
            gen.provider = provider
        if model:
            gen.model = model
            gen.parameters = {**(gen.parameters or {}), "model": model}
        db.commit()

        registry = get_provider_registry()
        request = AIJobRequest(
            module=gen.module.value if hasattr(gen.module, "value") else str(gen.module),
            prompt=gen.prompt,
            parameters=gen.parameters or {},
            project_id=gen.project_id,
        )

        attempts: list[dict[str, str | None]] = [{"provider": gen.provider, "model": gen.model}]
        for fb in AICostService.get_fallback_chain(db, module_val):
            entry = {"provider": fb.get("provider"), "model": fb.get("model")}
            if entry not in attempts:
                attempts.append(entry)

        last_exc: Exception | None = None
        result = None
        for attempt in attempts:
            if not attempt.get("provider"):
                continue
            try:
                req_params = {**(gen.parameters or {}), "model": attempt.get("model")} if attempt.get("model") else (gen.parameters or {})
                request = AIJobRequest(
                    module=module_val,
                    prompt=gen.prompt,
                    parameters=req_params,
                    project_id=gen.project_id,
                )
                result = registry.generate(request, provider_id=attempt["provider"])
                gen.provider = result.provider or attempt["provider"]
                if attempt.get("model"):
                    gen.model = attempt["model"]
                break
            except Exception as exc:
                last_exc = exc
                gen.retry_count = (gen.retry_count or 0) + 1
                db.commit()

        if result is None:
            raise last_exc or RuntimeError("All AI providers failed")

        try:
            gen.status = AIGenerationStatus.COMPLETED
            gen.completed_at = datetime.now(timezone.utc)
            gen.output_text = result.output_text
            gen.output_meta = result.meta
            gen.result_url = result.result_url
            gen.r2_key = result.r2_key
            gen.provider = result.provider
            gen.parameters = {**(gen.parameters or {}), "output": result.output_text}
            AICostService.store_cache(
                db,
                module=module_val,
                prompt=gen.prompt,
                parameters=gen.parameters,
                payload={
                    "output_text": result.output_text,
                    "result_url": result.result_url,
                    "provider": gen.provider,
                    "model": gen.model,
                    "meta": result.meta,
                },
                model=gen.model,
                provider=gen.provider,
                cost_usd=float(gen.cost_usd or 0),
            )
            finalize_generation_success(
                db,
                gen,
                started_at=gen.started_at,
                output_text=result.output_text,
                meta=result.meta,
            )

            if gen.created_by_id:
                db.add(
                    StudioNotification(
                        user_id=gen.created_by_id,
                        notification_type="ai_job_complete",
                        title=f"AI job completed — {gen.module.value}",
                        body=gen.prompt[:120],
                        data={"generation_id": gen.id, "module": gen.module.value, "provider": gen.provider},
                    )
                )
            db.commit()
            try:
                from app.domain.plugins.registry import PluginEventBus

                PluginEventBus.emit(
                    db,
                    "ai.job.completed",
                    {
                        "generation_id": gen.id,
                        "module": gen.module.value if hasattr(gen.module, "value") else str(gen.module),
                        "project_id": gen.project_id,
                        "provider": gen.provider,
                        "cost_usd": float(gen.cost_usd or 0),
                    },
                    user_id=gen.created_by_id,
                    commit=True,
                )
            except Exception:
                pass
        except Exception as exc:
            gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
            if gen and gen.status != AIGenerationStatus.CANCELLED:
                gen.status = AIGenerationStatus.FAILED
                gen.error = str(exc)
                apply_failure(gen, started_at=gen.started_at)
                db.commit()
            raise
