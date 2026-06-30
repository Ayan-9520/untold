"""Script AI writer orchestration — provider abstraction + full generation persistence."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.domain.script.providers.registry import get_script_registry
from app.domain.script.types import STYLE_ACTIONS, SCRIPT_ACTIONS, ScriptAgentRequest
from app.domain.studio.enums import AIGenerationModule, AIGenerationStatus, ScriptStyle
from app.models import User
from app.models.studio_platform import AIGeneration, Script, ScriptAIInteraction, ScriptVersion
from app.services.script_studio_service import ScriptStudioService


class ScriptAgentService:
    @staticmethod
    def _normalize_action(action: str) -> str:
        if action == "summarize":
            return "shorten"
        return action if action in SCRIPT_ACTIONS else "generate"

    @staticmethod
    def _persist_interaction(
        db: Session,
        script: Script,
        user: User,
        action: str,
        prompt: str | None,
        selection: str | None,
        target_language: str | None,
        tone: str | None,
        response: dict,
        provider: str,
        generation_id: int | None,
    ) -> ScriptAIInteraction:
        row = ScriptAIInteraction(
            script_id=script.id,
            action=action,
            prompt=prompt,
            selection=selection,
            target_language=target_language,
            tone=tone,
            response=response,
            provider=provider,
            ai_generation_id=generation_id,
            created_by_id=user.id,
        )
        db.add(row)
        return row

    @staticmethod
    def _apply_result(
        db: Session,
        script: Script,
        current: ScriptVersion,
        action: str,
        result_html: str,
        selection: str | None,
        suggested_style: str | None,
    ) -> None:
        append_actions = {"generate", "chapter", "scene", "hook", "cta"}
        if action in append_actions and not selection:
            current.content = (current.content or "") + result_html
        elif selection and selection in (current.content or ""):
            current.content = (current.content or "").replace(selection, result_html, 1)
        elif action in append_actions:
            current.content = (current.content or "") + result_html
        else:
            current.content = result_html

        if suggested_style and suggested_style in {s.value for s in ScriptStyle}:
            current.style = ScriptStyle(suggested_style)
        elif action in STYLE_ACTIONS:
            style_val = STYLE_ACTIONS[action]
            if style_val in {s.value for s in ScriptStyle}:
                current.style = ScriptStyle(style_val)

        script.content_version = (script.content_version or 0) + 1
        script.last_auto_saved_at = datetime.now(timezone.utc)

    @staticmethod
    def run_agent(
        db: Session,
        user: User,
        script_id: int,
        action: str,
        *,
        prompt: str | None = None,
        selection: str | None = None,
        target_language: str | None = "es",
        tone: str | None = None,
        provider_id: str | None = None,
        apply: bool = False,
    ) -> dict:
        action = ScriptAgentService._normalize_action(action)
        script = ScriptStudioService._get_script(db, script_id)
        from app.domain.studio.permissions import StudioPermissionService

        StudioPermissionService.require_permission(db, user, script.project_id, "script.edit")
        current = ScriptStudioService._current_version(db, script)

        gen = AIGeneration(
            project_id=script.project_id,
            module=AIGenerationModule.SCRIPT,
            prompt=prompt or action,
            parameters={
                "action": action,
                "script_id": script_id,
                "target_language": target_language,
                "tone": tone,
                "provider": provider_id,
            },
            status=AIGenerationStatus.QUEUED,
            created_by_id=user.id,
        )
        db.add(gen)
        db.flush()

        registry = get_script_registry()
        try:
            agent_result = registry.write(
                ScriptAgentRequest(
                    action=action,
                    title=script.title,
                    prompt=prompt,
                    content=current.content or "",
                    selection=selection,
                    style=current.style.value if current.style else "documentary",
                    target_language=target_language or "es",
                    tone=tone,
                    context={"content_version": script.content_version},
                    project_id=script.project_id,
                    script_id=script_id,
                ),
                provider_id=provider_id,
            )
            gen.status = AIGenerationStatus.COMPLETED
            gen.provider = agent_result.provider
            gen.output_text = agent_result.result
            gen.output_meta = agent_result.meta
            gen.completed_at = datetime.now(timezone.utc)
        except Exception as exc:
            gen.status = AIGenerationStatus.FAILED
            gen.error = str(exc)[:2000]
            agent_result = registry.write(
                ScriptAgentRequest(
                    action=action,
                    title=script.title,
                    prompt=prompt,
                    content=current.content or "",
                    selection=selection,
                    style=current.style.value if current.style else "documentary",
                    target_language=target_language or "es",
                    tone=tone,
                    project_id=script.project_id,
                    script_id=script_id,
                ),
                provider_id="demo",
            )
            gen.output_text = agent_result.result
            gen.provider = agent_result.provider
            gen.status = AIGenerationStatus.COMPLETED
            gen.completed_at = datetime.now(timezone.utc)

        response = {
            "result": agent_result.result,
            "action": action,
            "provider": agent_result.provider,
            "suggested_style": agent_result.suggested_style,
            "meta": agent_result.meta,
        }

        interaction = ScriptAgentService._persist_interaction(
            db,
            script,
            user,
            action,
            prompt,
            selection,
            target_language,
            tone,
            response,
            agent_result.provider,
            gen.id,
        )

        auto_apply = apply or (action == "generate" and not selection)
        if auto_apply and agent_result.result:
            ScriptAgentService._apply_result(
                db,
                script,
                current,
                action,
                agent_result.result,
                selection,
                agent_result.suggested_style,
            )
            script.last_edited_by_id = user.id

        db.commit()
        db.refresh(interaction)
        db.refresh(gen)
        return {
            **response,
            "generation_id": gen.id,
            "interaction_id": interaction.id,
            "applied": auto_apply,
            "created_at": interaction.created_at,
        }

    @staticmethod
    def list_history(db: Session, user: User, script_id: int, limit: int = 40) -> list[dict]:
        script = ScriptStudioService._get_script(db, script_id)
        from app.domain.studio.permissions import StudioPermissionService

        StudioPermissionService.require_permission(db, user, script.project_id, "project.read")
        rows = (
            db.query(ScriptAIInteraction)
            .filter(ScriptAIInteraction.script_id == script_id)
            .order_by(ScriptAIInteraction.created_at.desc())
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
                "result_preview": (r.response.get("result") or "")[:300],
                "created_at": r.created_at,
            }
            for r in rows
        ]

    @staticmethod
    def list_providers() -> list[dict]:
        return get_script_registry().list_providers()
