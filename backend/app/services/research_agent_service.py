"""Research AI agent orchestration — provider abstraction + persistence."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.domain.research.providers.registry import get_research_registry
from app.domain.research.types import ResearchAgentRequest
from app.models import User
from app.models.studio_platform import ResearchAIInteraction, ResearchSession, ResearchTimelineEvent
from app.services.research_studio_service import ResearchStudioService


class ResearchAgentService:
    @staticmethod
    def _persist_interaction(
        db: Session,
        session: ResearchSession,
        user: User,
        action: str,
        prompt: str,
        response: dict,
        provider: str,
    ) -> ResearchAIInteraction:
        row = ResearchAIInteraction(
            research_id=session.id,
            action=action,
            prompt=prompt,
            response=response,
            provider=provider,
            created_by_id=user.id,
        )
        db.add(row)
        return row

    @staticmethod
    def _apply_result(db: Session, session: ResearchSession, result, user_id: int) -> None:
        if result.summary:
            session.ai_summary = result.summary
        if result.statistics:
            session.statistics = result.statistics
        if result.public_facts:
            session.public_facts = result.public_facts
        if result.follow_up_questions:
            session.follow_up_questions = result.follow_up_questions
        if result.timeline_events:
            for ev in result.timeline_events:
                exists = (
                    db.query(ResearchTimelineEvent)
                    .filter(
                        ResearchTimelineEvent.research_id == session.id,
                        ResearchTimelineEvent.title == ev.get("title"),
                    )
                    .first()
                )
                if exists:
                    continue
                event_date = ev.get("event_date")
                if isinstance(event_date, str):
                    event_date = datetime.fromisoformat(event_date.replace("Z", "+00:00"))
                db.add(
                    ResearchTimelineEvent(
                        research_id=session.id,
                        event_date=event_date or datetime.now(timezone.utc),
                        title=ev.get("title", "Event"),
                        description=ev.get("description"),
                        event_type=ev.get("event_type", "milestone"),
                        created_by_id=user_id,
                    )
                )

    @staticmethod
    def run_agent(
        db: Session,
        user: User,
        research_id: int,
        action: str,
        prompt: str,
        *,
        provider_id: str | None = None,
        apply: bool = True,
    ) -> dict:
        session = ResearchStudioService._get_session(db, research_id)
        from app.domain.studio.permissions import StudioPermissionService
        StudioPermissionService.require_permission(db, user, session.project_id, "research.edit")

        registry = get_research_registry()
        result = registry.research(
            ResearchAgentRequest(
                action=action,
                topic=session.topic,
                prompt=prompt,
                context={
                    "sources_count": len(session.sources or []),
                    "has_summary": bool(session.ai_summary),
                },
                project_id=session.project_id,
                research_id=research_id,
            ),
            provider_id=provider_id,
        )

        response = {
            "summary": result.summary,
            "suggestions": result.suggestions,
            "follow_up_questions": result.follow_up_questions,
            "statistics": result.statistics,
            "public_facts": result.public_facts,
            "timeline_events": result.timeline_events,
            "fact_check_hints": result.fact_check_hints,
            "provider": result.provider,
            "meta": result.meta,
        }

        interaction = ResearchAgentService._persist_interaction(
            db, session, user, action, prompt, response, result.provider
        )

        if apply:
            ResearchAgentService._apply_result(db, session, result, user.id)

        db.commit()
        db.refresh(interaction)
        return {
            **response,
            "interaction_id": interaction.id,
            "created_at": interaction.created_at,
        }

    @staticmethod
    def list_history(db: Session, user: User, research_id: int, limit: int = 30) -> list[dict]:
        session = ResearchStudioService._get_session(db, research_id)
        from app.domain.studio.permissions import StudioPermissionService
        StudioPermissionService.require_permission(db, user, session.project_id, "project.read")
        rows = (
            db.query(ResearchAIInteraction)
            .filter(ResearchAIInteraction.research_id == research_id)
            .order_by(ResearchAIInteraction.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": r.id,
                "action": r.action,
                "prompt": r.prompt,
                "provider": r.provider,
                "response": r.response,
                "created_at": r.created_at,
            }
            for r in rows
        ]

    @staticmethod
    def list_providers() -> list[dict]:
        return get_research_registry().list_providers()

    @staticmethod
    def update_topic(db: Session, user: User, research_id: int, topic: str) -> ResearchSession:
        session = ResearchStudioService._get_session(db, research_id)
        from app.domain.studio.permissions import StudioPermissionService
        StudioPermissionService.require_permission(db, user, session.project_id, "research.edit")
        session.topic = topic.strip()
        if not session.workspace_content or session.workspace_content.startswith("# "):
            session.workspace_content = f"# {session.topic}\n\n## Research brief\n\n"
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def request_approval(db: Session, user: User, research_id: int) -> ResearchSession:
        session = ResearchStudioService._get_session(db, research_id)
        from app.domain.studio.permissions import StudioPermissionService
        StudioPermissionService.require_permission(db, user, session.project_id, "research.edit")
        session.status = "pending_approval"
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def approve(db: Session, user: User, research_id: int) -> ResearchSession:
        from app.domain.studio.permissions import StudioPermissionService
        return StudioPlatformService.approve_research(db, user, research_id)

    @staticmethod
    def reject(db: Session, user: User, research_id: int, notes: str | None = None) -> ResearchSession:
        session = ResearchStudioService._get_session(db, research_id)
        from app.domain.studio.permissions import StudioPermissionService
        StudioPermissionService.require_permission(db, user, session.project_id, "research.approve")
        session.status = "rejected"
        session.rejection_notes = notes
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def filter_sources(sources: list[dict], *, search: str | None = None, source_type: str | None = None) -> list[dict]:
        out = sources
        if search:
            q = search.lower()
            out = [s for s in out if q in (s.get("title") or "").lower() or q in (s.get("url") or "").lower()]
        if source_type:
            out = [s for s in out if s.get("source_type") == source_type]
        return out
