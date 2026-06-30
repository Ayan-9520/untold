"""Storyboard AI generator orchestration."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.domain.storyboard.providers.registry import get_storyboard_registry
from app.domain.storyboard.types import StoryboardAgentRequest
from app.domain.studio.enums import AIGenerationModule, AIGenerationStatus
from app.models import User
from app.models.studio_platform import AIGeneration, StoryboardAIInteraction, StoryboardScene
from app.services.storyboard_studio_service import StoryboardStudioService


class StoryboardAgentService:
    @staticmethod
    def _persist_interaction(
        db: Session,
        project_id: int,
        user: User,
        action: str,
        prompt: str | None,
        response: dict,
        provider: str,
        generation_id: int | None,
        scenes_created: int,
    ) -> StoryboardAIInteraction:
        row = StoryboardAIInteraction(
            project_id=project_id,
            action=action,
            prompt=prompt,
            response=response,
            provider=provider,
            ai_generation_id=generation_id,
            scenes_created=scenes_created,
            created_by_id=user.id,
        )
        db.add(row)
        return row

    @staticmethod
    def generate_from_script(
        db: Session,
        user: User,
        project_id: int,
        *,
        replace_existing: bool = False,
        default_duration_seconds: int = 15,
        prompt: str | None = None,
        provider_id: str | None = None,
    ) -> dict:
        from app.domain.studio.permissions import StudioPermissionService

        StudioPermissionService.require_permission(db, user, project_id, "storyboard.edit")
        workspace = StoryboardStudioService.get_workspace(db, user, project_id)
        script_content = StoryboardStudioService._get_script_content(db, project_id)

        gen = AIGeneration(
            project_id=project_id,
            module=AIGenerationModule.STORYBOARD,
            prompt=prompt or "generate_from_script",
            parameters={
                "action": "generate_from_script",
                "replace_existing": replace_existing,
                "default_duration_seconds": default_duration_seconds,
                "provider": provider_id,
            },
            status=AIGenerationStatus.QUEUED,
            created_by_id=user.id,
        )
        db.add(gen)
        db.flush()

        registry = get_storyboard_registry()
        try:
            result = registry.generate(
                StoryboardAgentRequest(
                    action="generate_from_script",
                    project_title=workspace["project_title"],
                    script_content=script_content,
                    prompt=prompt,
                    existing_scenes=workspace["scenes"],
                    default_duration_seconds=default_duration_seconds,
                    project_id=project_id,
                ),
                provider_id=provider_id,
            )
            gen.status = AIGenerationStatus.COMPLETED
            gen.provider = result.provider
            gen.output_text = result.summary
            gen.output_meta = {"scenes": result.scenes, **result.meta}
            gen.completed_at = datetime.now(timezone.utc)
        except Exception as exc:
            gen.status = AIGenerationStatus.FAILED
            gen.error = str(exc)[:2000]
            result = registry.generate(
                StoryboardAgentRequest(
                    action="generate_from_script",
                    project_title=workspace["project_title"],
                    script_content=script_content,
                    prompt=prompt,
                    default_duration_seconds=default_duration_seconds,
                    project_id=project_id,
                ),
                provider_id="demo",
            )
            gen.output_text = result.summary
            gen.provider = result.provider
            gen.status = AIGenerationStatus.COMPLETED
            gen.completed_at = datetime.now(timezone.utc)

        existing = StoryboardStudioService._list_scenes(db, project_id)
        if existing and not replace_existing:
            StoryboardStudioService._create_revision(db, user, project_id, "Before AI generation")
        if replace_existing and existing:
            StoryboardStudioService._create_revision(db, user, project_id, "Before AI replace")
            for scene in existing:
                db.delete(scene)
            db.flush()

        created_count = 0
        for item in result.scenes:
            scene = StoryboardScene(
                project_id=project_id,
                scene_number=item.get("scene_number", created_count + 1),
                sort_order=item.get("sort_order", item.get("scene_number", created_count + 1)),
                duration_seconds=item.get("duration_seconds", default_duration_seconds),
                narration=item.get("narration"),
                dialogue=item.get("dialogue"),
                visual_prompt=item.get("visual_prompt"),
                camera_angle=item.get("camera_angle"),
                camera_movement=item.get("camera_movement"),
                shot_type=item.get("shot_type"),
                lighting=item.get("lighting"),
                environment=item.get("environment"),
                mood=item.get("mood"),
                transition=item.get("transition"),
                reference_image_url=item.get("reference_image_url"),
                status=item.get("status", "draft"),
            )
            db.add(scene)
            created_count += 1
        db.flush()
        StoryboardStudioService._create_revision(db, user, project_id, "AI generated from script")

        response = {
            "summary": result.summary,
            "scenes_created": created_count,
            "provider": result.provider,
            "meta": result.meta,
        }
        interaction = StoryboardAgentService._persist_interaction(
            db, project_id, user, "generate_from_script", prompt, response, result.provider, gen.id, created_count
        )
        StudioPlatformService.log_activity(db, user.id, "storyboard.ai_generated", project_id, "storyboard", project_id)
        db.commit()
        db.refresh(interaction)
        return {
            **response,
            "generation_id": gen.id,
            "interaction_id": interaction.id,
            "created_at": interaction.created_at,
        }

    @staticmethod
    def list_history(db: Session, user: User, project_id: int, limit: int = 30) -> list[dict]:
        from app.domain.studio.permissions import StudioPermissionService

        StudioPermissionService.require_permission(db, user, project_id, "project.read")
        rows = (
            db.query(StoryboardAIInteraction)
            .filter(StoryboardAIInteraction.project_id == project_id)
            .order_by(StoryboardAIInteraction.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": r.id,
                "action": r.action,
                "prompt": (r.prompt or "")[:200],
                "provider": r.provider,
                "generation_id": r.ai_generation_id,
                "scenes_created": r.scenes_created,
                "summary": (r.response.get("summary") or "")[:300],
                "created_at": r.created_at,
            }
            for r in rows
        ]

    @staticmethod
    def list_providers() -> list[dict]:
        return get_storyboard_registry().list_providers()
