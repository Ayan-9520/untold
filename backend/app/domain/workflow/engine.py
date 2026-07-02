"""Workflow Engine — orchestrates production agents in sequence."""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.domain.ai.providers.registry import get_provider_registry
from app.domain.ai.types import AIJobRequest
from app.domain.image.providers.registry import get_image_registry
from app.domain.image.types import ImageGenerateRequest
from app.domain.music.providers.registry import get_music_registry
from app.domain.music.types import MusicGenerateRequest
from app.domain.seo.providers.registry import get_seo_registry
from app.domain.seo.types import SEOGenerateRequest
from app.domain.storyboard.providers.registry import get_storyboard_registry
from app.domain.storyboard.types import StoryboardAgentRequest
from app.domain.studio.enums import AIGenerationModule, AIGenerationStatus, ProjectStage
from app.domain.translation.providers.registry import get_translation_registry
from app.domain.translation.types import TranslationRequest
from app.domain.video.providers.registry import get_video_registry
from app.domain.video.types import VideoGenerateRequest
from app.domain.voice.providers.registry import get_voice_registry
from app.domain.voice.types import VoiceGenerateRequest
from app.domain.workflow.context import WorkflowContext
from app.domain.workflow.logs import append_log
from app.domain.workflow.prompts import merge_prompts, render_workflow_prompt
from app.domain.workflow.steps import WORKFLOW_AGENT_IDS, WORKFLOW_AGENTS, stage_progress

WORKFLOW_STEP_MARKETPLACE_SLUG: dict[str, str] = {
    "research": "research",
    "seo": "seo",
    "translation": "translation",
    "voice": "voice",
    "publisher": "publishing",
}
from app.models import User
from app.models.studio import Production
from app.models.studio_platform import AIGeneration, ProductionPipelineRun, StudioNotification


@dataclass
class AgentStepResult:
    generation_id: int | None = None
    output_preview: str | None = None
    result_url: str | None = None
    publish_run_id: int | None = None


class WorkflowEngine:
    @staticmethod
    def initial_stages() -> list[dict]:
        return [{"id": s["id"], "label": s["label"], "status": "pending"} for s in WORKFLOW_AGENTS]

    @staticmethod
    def _set_stage(stages: list[dict], stage_id: str, **updates) -> None:
        for stage in stages:
            if stage["id"] == stage_id:
                stage.update(updates)
                return

    @staticmethod
    def _create_generation(
        db: Session,
        *,
        run: ProductionPipelineRun,
        module: AIGenerationModule,
        prompt: str,
        provider: str | None,
        parameters: dict | None = None,
    ) -> AIGeneration:
        registry = get_provider_registry()
        provider_id = provider or registry.resolve(module.value, None).id
        gen = AIGeneration(
            project_id=run.project_id,
            module=module,
            prompt=prompt,
            parameters=parameters or {},
            provider=provider_id,
            status=AIGenerationStatus.RUNNING,
            created_by_id=run.created_by_id,
            started_at=datetime.now(timezone.utc),
        )
        db.add(gen)
        db.flush()
        return gen

    @staticmethod
    def _complete_generation(db: Session, gen: AIGeneration, *, output_text: str, meta: dict | None = None, result_url: str | None = None, r2_key: str | None = None, provider: str | None = None) -> None:
        gen.status = AIGenerationStatus.COMPLETED
        gen.completed_at = datetime.now(timezone.utc)
        gen.output_text = output_text
        gen.output_meta = meta
        gen.result_url = result_url
        if r2_key:
            gen.r2_key = r2_key
        if provider:
            gen.provider = provider

    @staticmethod
    def _advance_project_stage(db: Session, project_id: int | None, stage: str) -> None:
        if not project_id:
            return
        stage_map = {
            "idea": ProjectStage.RESEARCH.value,
            "research": ProjectStage.RESEARCH.value,
            "script": ProjectStage.SCRIPT.value,
            "storyboard": ProjectStage.STORYBOARD.value,
            "image": ProjectStage.IMAGE.value,
            "video": ProjectStage.VIDEO.value,
            "voice": ProjectStage.VIDEO.value,
            "music": ProjectStage.EDITING.value,
            "timeline": ProjectStage.EDITING.value,
            "seo": ProjectStage.REVIEW.value,
            "translation": ProjectStage.REVIEW.value,
            "publisher": ProjectStage.PUBLISHING.value,
            "analytics": ProjectStage.COMPLETED.value,
        }
        mapped = stage_map.get(stage)
        if not mapped:
            return
        project = db.query(Production).filter(Production.id == project_id).first()
        if project:
            project.stage = mapped
            db.flush()

    @staticmethod
    def _run_agent(db: Session, run: ProductionPipelineRun, ctx: WorkflowContext, step_id: str) -> AgentStepResult:
        providers = ctx.providers
        marketplace_slug = WORKFLOW_STEP_MARKETPLACE_SLUG.get(step_id)
        agent_ctx = None
        if marketplace_slug and run.created_by_id:
            from app.services.agent_runtime_service import AgentRuntimeService

            agent_ctx = AgentRuntimeService.require_enabled(db, run.created_by_id, marketplace_slug)
            if agent_ctx and not providers.get(step_id):
                provider_override = AgentRuntimeService.merged_provider(agent_ctx, step_id)
                if provider_override:
                    providers = {**providers, step_id: provider_override}

        topic = ctx.topic

        if step_id == "idea":
            summary = f"Idea captured: {topic}"
            return AgentStepResult(None, summary, None)

        if step_id == "research":
            research_prompt = render_workflow_prompt("research", ctx.prompts, ctx)
            gen = WorkflowEngine._create_generation(
                db,
                run=run,
                module=AIGenerationModule.RESEARCH,
                prompt=research_prompt,
                provider=providers.get("research"),
            )
            result = get_provider_registry().generate(
                AIJobRequest(module="research", prompt=gen.prompt, project_id=run.project_id),
                provider_id=gen.provider,
            )
            ctx.research_text = result.output_text or ""
            WorkflowEngine._complete_generation(db, gen, output_text=ctx.research_text, meta=result.meta, result_url=result.result_url, provider=result.provider)
            return AgentStepResult(gen.id, ctx.research_text[:400], result.result_url)

        if step_id == "script":
            script_prompt = render_workflow_prompt("script", ctx.prompts, ctx)
            gen = WorkflowEngine._create_generation(
                db,
                run=run,
                module=AIGenerationModule.SCRIPT,
                prompt=script_prompt,
                provider=providers.get("script"),
            )
            result = get_provider_registry().generate(
                AIJobRequest(module="script", prompt=gen.prompt, project_id=run.project_id),
                provider_id=gen.provider,
            )
            ctx.script_text = result.output_text or ""
            WorkflowEngine._complete_generation(db, gen, output_text=ctx.script_text, meta=result.meta, result_url=result.result_url, provider=result.provider)
            return AgentStepResult(gen.id, ctx.script_text[:400], result.result_url)

        if step_id == "storyboard":
            gen = WorkflowEngine._create_generation(
                db,
                run=run,
                module=AIGenerationModule.STORYBOARD,
                prompt=f"Storyboard from script for: {topic}",
                provider=providers.get("storyboard"),
                parameters={"action": "generate_from_script"},
            )
            sb_result = get_storyboard_registry().generate(
                StoryboardAgentRequest(
                    action="generate_from_script",
                    project_title=topic,
                    script_content=ctx.script_text or ctx.research_text,
                    project_id=run.project_id,
                ),
                provider_id=providers.get("storyboard"),
            )
            ctx.storyboard_scenes = sb_result.scenes or []
            ctx.storyboard_summary = sb_result.summary or ""
            output = ctx.storyboard_summary or f"{len(ctx.storyboard_scenes)} scenes planned"
            WorkflowEngine._complete_generation(db, gen, output_text=output, meta={**(sb_result.meta or {}), "scenes": ctx.storyboard_scenes}, provider=sb_result.provider)
            return AgentStepResult(gen.id, output[:400], None)

        if step_id == "image":
            image_prompt = render_workflow_prompt("thumbnail", ctx.prompts, ctx)
            gen = WorkflowEngine._create_generation(
                db,
                run=run,
                module=AIGenerationModule.IMAGE,
                prompt=image_prompt,
                provider=providers.get("image"),
                parameters={"image_type": "thumbnail", "aspect_ratio": "16:9"},
            )
            img = get_image_registry().generate(
                ImageGenerateRequest(prompt=image_prompt, image_type="thumbnail", aspect_ratio="16:9", project_id=run.project_id),
                provider_id=gen.provider,
            )
            ctx.image_text = img.output_text or ""
            ctx.image_url = img.result_url
            WorkflowEngine._complete_generation(db, gen, output_text=ctx.image_text, meta=img.meta, result_url=img.result_url, r2_key=img.r2_key, provider=img.provider)
            return AgentStepResult(gen.id, ctx.image_text[:400] or "Images generated", img.result_url)

        if step_id == "video":
            excerpt = ctx.script_excerpt(500)
            video_prompt = (
                f"Cinematic B-roll for documentary about {topic}. "
                f"Scene: {excerpt}. Stadium atmosphere, original footage style."
            )
            gen = WorkflowEngine._create_generation(
                db,
                run=run,
                module=AIGenerationModule.VIDEO,
                prompt=video_prompt,
                provider=providers.get("video"),
                parameters={"video_type": "b_roll", "duration_seconds": 8},
            )
            vid = get_video_registry().generate(
                VideoGenerateRequest(prompt=video_prompt, video_type="b_roll", duration_seconds=8, project_id=run.project_id),
                provider_id=gen.provider,
            )
            ctx.video_text = vid.output_text or ""
            ctx.video_url = vid.result_url
            WorkflowEngine._complete_generation(db, gen, output_text=ctx.video_text, meta=vid.meta, result_url=vid.result_url, r2_key=vid.r2_key, provider=vid.provider)
            return AgentStepResult(gen.id, ctx.video_text[:400] or "Video clip generated", vid.result_url)

        if step_id == "voice":
            narration = render_workflow_prompt("voice", ctx.prompts, ctx)
            if not narration.strip():
                narration = (ctx.translation_text or ctx.script_text or ctx.research_text or topic)[:800]
            gen = WorkflowEngine._create_generation(
                db,
                run=run,
                module=AIGenerationModule.VOICE,
                prompt=narration,
                provider=providers.get("voice"),
                parameters={"language": ctx.translation_language or "en", "emotion": "neutral"},
            )
            voice = get_voice_registry().generate(
                VoiceGenerateRequest(
                    text=narration[:4000],
                    language=ctx.translation_language or "en",
                    emotion="neutral",
                    project_id=run.project_id,
                ),
                provider_id=gen.provider,
            )
            ctx.voice_text = voice.output_text or narration[:200]
            ctx.voice_url = voice.result_url
            WorkflowEngine._complete_generation(db, gen, output_text=ctx.voice_text, meta=voice.meta, result_url=voice.result_url, r2_key=voice.r2_key, provider=voice.provider)
            return AgentStepResult(gen.id, ctx.voice_text[:400], voice.result_url)

        if step_id == "music":
            music_prompt = f"Documentary underscore for: {topic}. Reflective, cinematic, unobtrusive."
            gen = WorkflowEngine._create_generation(
                db,
                run=run,
                module=AIGenerationModule.MUSIC,
                prompt=music_prompt,
                provider=providers.get("music"),
                parameters={"category": "documentary", "duration_seconds": 60},
            )
            music = get_music_registry().generate(
                MusicGenerateRequest(
                    prompt=music_prompt,
                    category="documentary",
                    duration_seconds=60,
                    project_id=run.project_id,
                ),
                provider_id=gen.provider,
            )
            ctx.music_text = music.output_text or music_prompt[:200]
            ctx.music_url = music.result_url
            WorkflowEngine._complete_generation(
                db,
                gen,
                output_text=ctx.music_text,
                meta=music.meta,
                result_url=music.result_url,
                r2_key=music.r2_key,
                provider=music.provider,
            )
            return AgentStepResult(gen.id, ctx.music_text[:400] or "Music generated", music.result_url)

        if step_id == "timeline":
            ctx.timeline_summary = (
                f"Timeline ready — {len(ctx.storyboard_scenes)} storyboard scenes, "
                f"voice + video + music assets queued for assembly."
            )
            return AgentStepResult(None, ctx.timeline_summary, None)

        if step_id == "seo":
            seo_prompt = render_workflow_prompt("seo", ctx.prompts, ctx)
            gen = WorkflowEngine._create_generation(
                db,
                run=run,
                module=AIGenerationModule.SEO,
                prompt=seo_prompt,
                provider=providers.get("seo"),
                parameters={"content_type": "documentary", "variant_count": 3},
            )
            seo = get_seo_registry().generate(
                SEOGenerateRequest(
                    topic=seo_prompt[:500] if len(seo_prompt) > 80 else topic,
                    content_type="documentary",
                    target_keyword=topic.split()[0] if topic else "",
                    project_id=run.project_id,
                    meta={"workflow_prompt": seo_prompt},
                ),
                provider_id=providers.get("seo"),
            )
            ctx.seo_text = seo.output_text or ""
            ctx.seo_variants = [
                {
                    "label": v.label,
                    "youtube_title": v.youtube_title,
                    "meta_title": v.meta_title,
                    "seo_score": v.seo_score,
                }
                for v in (seo.variants or [])
            ]
            WorkflowEngine._complete_generation(db, gen, output_text=ctx.seo_text, meta={**(seo.meta or {}), "variants": ctx.seo_variants}, provider=seo.provider)
            preview = ctx.seo_variants[0]["youtube_title"] if ctx.seo_variants else ctx.seo_text[:400]
            return AgentStepResult(gen.id, preview, None)

        if step_id == "translation":
            target_lang = ctx.translation_language or "es"
            source_text = ctx.script_text or ctx.research_text or topic
            translation_prompt = render_workflow_prompt(
                "translation",
                ctx.prompts,
                ctx,
                language=target_lang,
            )
            gen = WorkflowEngine._create_generation(
                db,
                run=run,
                module=AIGenerationModule.TRANSLATION,
                prompt=translation_prompt,
                provider=providers.get("translation"),
                parameters={"language": target_lang},
            )
            trans = get_translation_registry().translate(
                TranslationRequest(
                    source_text=source_text[:8000],
                    content_type="script",
                    source_lang="en",
                    target_lang=target_lang,
                    project_id=run.project_id,
                ),
                provider_id=gen.provider,
            )
            ctx.translation_text = trans.output_text or trans.translated_text or ""
            WorkflowEngine._complete_generation(
                db,
                gen,
                output_text=ctx.translation_text,
                meta=trans.meta,
                result_url=trans.result_url,
                r2_key=trans.r2_key,
                provider=trans.provider,
            )
            return AgentStepResult(gen.id, ctx.translation_text[:400] or "Translation complete", trans.result_url)

        if step_id == "publisher":
            if run.project_id and run.created_by_id:
                user = db.query(User).filter(User.id == run.created_by_id).first()
                project = db.query(Production).filter(Production.id == run.project_id).first()
                if user and project:
                    best = ctx.seo_variants[0] if ctx.seo_variants else {}
                    from app.schemas.publishing_agent import PublishingAgentCreate
                    from app.services.publishing_agent_service import PublishingAgentService

                    pub = PublishingAgentService.create_run(
                        db,
                        user,
                        PublishingAgentCreate(
                            project_id=run.project_id,
                            platforms=[p for p in ctx.publish_platforms if p][:4] or ["originals"],
                            requires_approval=False,
                            seo_title=best.get("meta_title") or project.seo_title,
                            seo_description=ctx.seo_text[:500] if ctx.seo_text else project.seo_description,
                            thumbnail_url=ctx.image_url or project.thumbnail_url,
                        ),
                    )
                    PublishingAgentService.execute_run(db, pub.id)
                    ctx.publish_run_id = pub.id
                    ctx.publish_summary = f"Published to {', '.join(pub.platforms or [])}"
                    return AgentStepResult(None, ctx.publish_summary, None, pub.id)

            ctx.publish_summary = "Publish simulated — link a project to dispatch to platforms."
            return AgentStepResult(None, ctx.publish_summary, None)

        if step_id == "analytics":
            ctx.analytics_summary = (
                "Production complete — track views, retention, and revenue in Viewer Analytics."
            )
            return AgentStepResult(None, ctx.analytics_summary, None)

        raise ValueError(f"Unknown workflow agent: {step_id}")

    @staticmethod
    def execute_run(db: Session, run_id: int) -> None:
        run = db.query(ProductionPipelineRun).filter(ProductionPipelineRun.id == run_id).first()
        if not run or run.status in ("cancelled", "completed", "failed"):
            return

        meta = dict(run.output_meta or {})
        ctx = WorkflowContext(
            topic=run.topic,
            project_id=run.project_id,
            providers=meta.get("providers") or {},
            publish_platforms=meta.get("publish_platforms") or ["originals", "youtube"],
            prompts=merge_prompts(meta.get("prompts")),
            translation_language=meta.get("translation_language"),
        )

        run.status = "running"
        run.started_at = datetime.now(timezone.utc)
        stages = list(run.stages or WorkflowEngine.initial_stages())
        append_log(db, run_id, "Workflow engine running", level="info")
        db.commit()

        try:
            for step_id in WORKFLOW_AGENT_IDS:
                run = db.query(ProductionPipelineRun).filter(ProductionPipelineRun.id == run_id).first()
                if not run or run.status == "cancelled":
                    return

                run.current_stage = step_id
                run.progress = stage_progress(step_id)
                WorkflowEngine._set_stage(stages, step_id, status="running")
                run.stages = stages
                WorkflowEngine._advance_project_stage(db, run.project_id, step_id)
                append_log(db, run_id, f"Agent started: {step_id}", level="info", stage=step_id)
                db.commit()

                step_result = WorkflowEngine._run_agent(db, run, ctx, step_id)
                marketplace_slug = WORKFLOW_STEP_MARKETPLACE_SLUG.get(step_id)
                if marketplace_slug and run.created_by_id:
                    from app.services.agent_runtime_service import AgentRuntimeService

                    try:
                        actx = AgentRuntimeService.build_context(
                            db, run.created_by_id, marketplace_slug, project_id=run.project_id
                        )
                        AgentRuntimeService.log_execution(
                            db,
                            agent_slug=marketplace_slug,
                            installation_id=actx.installation_id,
                            user_id=run.created_by_id,
                            organization_id=actx.organization_id,
                            project_id=run.project_id,
                            run_id=run.id,
                            generation_id=step_result.generation_id,
                            status="success",
                            message=f"Workflow step: {step_id}",
                            meta={"output_preview": (step_result.output_preview or "")[:200]},
                        )
                    except Exception:
                        pass
                WorkflowEngine._set_stage(
                    stages,
                    step_id,
                    status="completed",
                    generation_id=step_result.generation_id,
                    output_preview=step_result.output_preview,
                    result_url=step_result.result_url,
                    publish_run_id=step_result.publish_run_id,
                )
                append_log(
                    db,
                    run_id,
                    f"Agent completed: {step_id}",
                    level="info",
                    stage=step_id,
                )

                run = db.query(ProductionPipelineRun).filter(ProductionPipelineRun.id == run_id).first()
                if run:
                    run.stages = stages
                    db.commit()
                time.sleep(0.1)

            run = db.query(ProductionPipelineRun).filter(ProductionPipelineRun.id == run_id).first()
            if run:
                run.status = "completed"
                run.current_stage = "complete"
                run.progress = 100
                run.completed_at = datetime.now(timezone.utc)
                run.output_meta = {
                    **meta,
                    "research_preview": ctx.research_text[:500],
                    "script_preview": ctx.script_text[:500],
                    "translation_preview": ctx.translation_text[:500] if ctx.translation_text else None,
                    "storyboard_scenes": len(ctx.storyboard_scenes),
                    "image_url": ctx.image_url,
                    "voice_url": ctx.voice_url,
                    "video_url": ctx.video_url,
                    "music_url": ctx.music_url,
                    "timeline_summary": ctx.timeline_summary,
                    "seo_variants": ctx.seo_variants,
                    "publish_run_id": ctx.publish_run_id,
                    "publish_summary": ctx.publish_summary,
                    "analytics_summary": ctx.analytics_summary,
                }
                run.stages = stages
                if run.project_id:
                    project = db.query(Production).filter(Production.id == run.project_id).first()
                    if project:
                        project.stage = ProjectStage.COMPLETED.value
                if run.created_by_id:
                    db.add(
                        StudioNotification(
                            user_id=run.created_by_id,
                            notification_type="workflow_complete",
                            title=f"Workflow complete — {run.topic[:80]}",
                            body="Idea → Research → Script → Storyboard → Images → Video → Voice → Music → Timeline → SEO → Translation → Publishing → Analytics",
                            data={"pipeline_run_id": run.id},
                        )
                    )
                append_log(db, run_id, "Workflow completed successfully", level="info")
                db.commit()

        except Exception as exc:
            run = db.query(ProductionPipelineRun).filter(ProductionPipelineRun.id == run_id).first()
            if run and run.status != "cancelled":
                failed_slug = WORKFLOW_STEP_MARKETPLACE_SLUG.get(run.current_stage or "")
                if failed_slug and run.created_by_id:
                    from app.services.agent_runtime_service import AgentRuntimeService

                    try:
                        actx = AgentRuntimeService.build_context(
                            db, run.created_by_id, failed_slug, project_id=run.project_id
                        )
                        AgentRuntimeService.log_execution(
                            db,
                            agent_slug=failed_slug,
                            installation_id=actx.installation_id,
                            user_id=run.created_by_id,
                            organization_id=actx.organization_id,
                            project_id=run.project_id,
                            run_id=run.id,
                            status="failed",
                            message=str(exc)[:500],
                            meta={"step_id": run.current_stage},
                        )
                    except Exception:
                        pass
                if run.current_stage:
                    WorkflowEngine._set_stage(stages, run.current_stage, status="failed", error=str(exc))
                run.status = "failed"
                run.error_message = str(exc)
                run.stages = stages
                run.completed_at = datetime.now(timezone.utc)
                append_log(db, run_id, f"Workflow failed: {exc}", level="error", stage=run.current_stage)
                db.commit()
            raise
