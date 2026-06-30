"""Research Studio — workspace, notes, references, export, AI assistant."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import NotFoundError
from app.domain.studio.enums import ApprovalStatus
from app.models import User
from app.models.studio import Production
from app.models.studio_platform import (
    ResearchBookmark,
    ResearchComment,
    ResearchFactCheck,
    ResearchNote,
    ResearchSession,
    ResearchSource,
    ResearchTimelineEvent,
    ResearchVersion,
)
from app.schemas.research_studio import (
    ResearchAIRequest,
    ResearchBookmarkCreate,
    ResearchCommentCreate,
    ResearchFactCheckCreate,
    ResearchFactCheckUpdate,
    ResearchNoteCreate,
    ResearchNoteUpdate,
    ResearchSourceCreate,
    ResearchSourceUpdate,
    ResearchTimelineEventCreate,
    ResearchWorkspaceAutoSave,
)
from app.services.studio_platform_service import StudioPlatformService


class ResearchStudioService:
    @staticmethod
    def _get_session(db: Session, research_id: int) -> ResearchSession:
        session = db.query(ResearchSession).filter(ResearchSession.id == research_id).first()
        if not session:
            raise NotFoundError("Research session")
        return session

    @staticmethod
    def get_or_create_workspace(db: Session, user: User, project_id: int) -> ResearchSession:
        StudioPlatformService.require_permission(db, user, project_id, "research.edit")
        project = db.query(Production).filter(Production.id == project_id).first()
        if not project:
            raise NotFoundError("Project")
        session = (
            db.query(ResearchSession)
            .filter(ResearchSession.project_id == project_id)
            .order_by(ResearchSession.created_at.desc())
            .first()
        )
        if not session:
            session = ResearchSession(
                project_id=project_id,
                topic=project.title,
                workspace_content=f"# {project.title}\n\n## Research brief\n\n",
            )
            db.add(session)
            db.flush()
            StudioPlatformService.log_activity(db, user.id, "research.created", project_id, "research", session.id)
            db.commit()
            db.refresh(session)
        return session

    @staticmethod
    def get_full_workspace(db: Session, user: User, research_id: int) -> dict:
        session = ResearchStudioService._get_session(db, research_id)
        StudioPlatformService.require_permission(db, user, session.project_id, "project.read")
        project = db.query(Production).filter(Production.id == session.project_id).first()

        notes = (
            db.query(ResearchNote, User)
            .join(User, User.id == ResearchNote.author_id)
            .filter(ResearchNote.research_id == research_id)
            .order_by(ResearchNote.is_pinned.desc(), ResearchNote.updated_at.desc())
            .all()
        )
        sources = (
            db.query(ResearchSource)
            .filter(ResearchSource.research_id == research_id)
            .order_by(ResearchSource.is_bookmarked.desc(), ResearchSource.created_at.desc())
            .all()
        )
        bookmarks = (
            db.query(ResearchBookmark)
            .filter(ResearchBookmark.research_id == research_id)
            .order_by(ResearchBookmark.created_at.desc())
            .all()
        )
        fact_checks = (
            db.query(ResearchFactCheck)
            .filter(ResearchFactCheck.research_id == research_id)
            .order_by(ResearchFactCheck.created_at.desc())
            .all()
        )
        comments = (
            db.query(ResearchComment, User)
            .join(User, User.id == ResearchComment.user_id)
            .filter(ResearchComment.research_id == research_id)
            .order_by(ResearchComment.created_at.desc())
            .all()
        )
        timeline = (
            db.query(ResearchTimelineEvent)
            .filter(ResearchTimelineEvent.research_id == research_id)
            .order_by(ResearchTimelineEvent.event_date.asc())
            .all()
        )
        versions = (
            db.query(ResearchVersion, User)
            .join(User, User.id == ResearchVersion.created_by_id)
            .filter(ResearchVersion.research_id == research_id)
            .order_by(ResearchVersion.version.desc())
            .limit(20)
            .all()
        )

        from app.services.research_agent_service import ResearchAgentService
        ai_history = ResearchAgentService.list_history(db, user, research_id, limit=20)
        providers = ResearchAgentService.list_providers()

        return {
            "workspace": {
                "id": session.id,
                "project_id": session.project_id,
                "project_title": project.title if project else None,
                "topic": session.topic,
                "status": session.status,
                "workspace_content": session.workspace_content or "",
                "content_version": session.content_version,
                "ai_summary": session.ai_summary,
                "statistics": session.statistics or [],
                "public_facts": session.public_facts or [],
                "follow_up_questions": session.follow_up_questions or [],
                "rejection_notes": session.rejection_notes,
                "last_auto_saved_at": session.last_auto_saved_at,
                "approved_at": session.approved_at,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
            },
            "notes": [
                {
                    "id": n.id,
                    "author_id": n.author_id,
                    "author_name": u.full_name,
                    "title": n.title,
                    "content": n.content,
                    "is_pinned": n.is_pinned,
                    "created_at": n.created_at,
                    "updated_at": n.updated_at,
                }
                for n, u in notes
            ],
            "sources": [
                {
                    "id": s.id,
                    "title": s.title,
                    "url": s.url,
                    "source_type": s.source_type,
                    "credibility_score": s.credibility_score,
                    "notes": s.notes,
                    "excerpt": s.excerpt,
                    "is_bookmarked": s.is_bookmarked,
                    "created_at": s.created_at,
                }
                for s in sources
            ],
            "bookmarks": [
                {
                    "id": b.id,
                    "title": b.title,
                    "url": b.url,
                    "excerpt": b.excerpt,
                    "color": b.color,
                    "created_at": b.created_at,
                }
                for b in bookmarks
            ],
            "fact_checks": [
                {
                    "id": fc.id,
                    "claim": fc.claim,
                    "status": fc.status,
                    "source_id": fc.source_id,
                    "notes": fc.notes,
                    "checked_by_id": fc.checked_by_id,
                    "created_at": fc.created_at,
                }
                for fc in fact_checks
            ],
            "comments": [
                {
                    "id": c.id,
                    "user_id": c.user_id,
                    "author_name": u.full_name,
                    "content": c.content,
                    "created_at": c.created_at,
                }
                for c, u in comments
            ],
            "timeline": [
                {
                    "id": t.id,
                    "event_date": t.event_date,
                    "title": t.title,
                    "description": t.description,
                    "event_type": t.event_type,
                    "created_at": t.created_at,
                }
                for t in timeline
            ],
            "versions": [
                {
                    "id": v.id,
                    "version": v.version,
                    "workspace_content": v.workspace_content,
                    "created_by_id": v.created_by_id,
                    "author_name": u.full_name,
                    "created_at": v.created_at,
                }
                for v, u in versions
            ],
            "ai_history": ai_history,
            "providers": providers,
        }

    @staticmethod
    def auto_save(db: Session, user: User, research_id: int, data: ResearchWorkspaceAutoSave) -> ResearchSession:
        session = ResearchStudioService._get_session(db, research_id)
        StudioPlatformService.require_permission(db, user, session.project_id, "research.edit")
        session.workspace_content = data.workspace_content
        session.last_auto_saved_at = datetime.now(timezone.utc)
        if data.create_version:
            ResearchStudioService._create_version_snapshot(db, session, user.id)
        else:
            session.content_version = (session.content_version or 0) + 1
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def _create_version_snapshot(db: Session, session: ResearchSession, user_id: int) -> ResearchVersion:
        version_num = (
            db.query(func.max(ResearchVersion.version))
            .filter(ResearchVersion.research_id == session.id)
            .scalar()
            or 0
        ) + 1
        snap = ResearchVersion(
            research_id=session.id,
            version=version_num,
            workspace_content=session.workspace_content or "",
            snapshot={"topic": session.topic, "content_version": session.content_version},
            created_by_id=user_id,
        )
        db.add(snap)
        session.content_version = version_num
        return snap

    @staticmethod
    def create_note(db: Session, user: User, research_id: int, data: ResearchNoteCreate) -> ResearchNote:
        session = ResearchStudioService._get_session(db, research_id)
        StudioPlatformService.require_permission(db, user, session.project_id, "research.edit")
        note = ResearchNote(
            research_id=research_id,
            author_id=user.id,
            title=data.title,
            content=data.content,
            is_pinned=data.is_pinned,
        )
        db.add(note)
        StudioPlatformService.log_activity(db, user.id, "research.note_added", session.project_id, "note", note.id)
        db.commit()
        db.refresh(note)
        return note

    @staticmethod
    def update_note(db: Session, user: User, research_id: int, note_id: int, data: ResearchNoteUpdate) -> ResearchNote:
        session = ResearchStudioService._get_session(db, research_id)
        StudioPlatformService.require_permission(db, user, session.project_id, "research.edit")
        note = db.query(ResearchNote).filter(ResearchNote.id == note_id, ResearchNote.research_id == research_id).first()
        if not note:
            raise NotFoundError("Note")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(note, field, value)
        db.commit()
        db.refresh(note)
        return note

    @staticmethod
    def delete_note(db: Session, user: User, research_id: int, note_id: int) -> None:
        session = ResearchStudioService._get_session(db, research_id)
        StudioPlatformService.require_permission(db, user, session.project_id, "research.edit")
        note = db.query(ResearchNote).filter(ResearchNote.id == note_id, ResearchNote.research_id == research_id).first()
        if not note:
            raise NotFoundError("Note")
        db.delete(note)
        db.commit()

    @staticmethod
    def add_source(db: Session, user: User, research_id: int, data: ResearchSourceCreate) -> ResearchSource:
        session = ResearchStudioService._get_session(db, research_id)
        StudioPlatformService.require_permission(db, user, session.project_id, "research.edit")
        source = ResearchSource(
            research_id=research_id,
            title=data.title,
            url=data.url,
            source_type=data.source_type,
            credibility_score=data.credibility_score,
            notes=data.notes,
            excerpt=data.excerpt,
            is_bookmarked=data.is_bookmarked,
        )
        db.add(source)
        project = db.query(Production).filter(Production.id == session.project_id).first()
        if project:
            project.sources_count = (project.sources_count or 0) + 1
        db.commit()
        db.refresh(source)
        return source

    @staticmethod
    def update_source(db: Session, user: User, research_id: int, source_id: int, data: ResearchSourceUpdate) -> ResearchSource:
        session = ResearchStudioService._get_session(db, research_id)
        StudioPlatformService.require_permission(db, user, session.project_id, "research.edit")
        source = db.query(ResearchSource).filter(ResearchSource.id == source_id, ResearchSource.research_id == research_id).first()
        if not source:
            raise NotFoundError("Reference")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(source, field, value)
        db.commit()
        db.refresh(source)
        return source

    @staticmethod
    def delete_source(db: Session, user: User, research_id: int, source_id: int) -> None:
        session = ResearchStudioService._get_session(db, research_id)
        StudioPlatformService.require_permission(db, user, session.project_id, "research.edit")
        source = db.query(ResearchSource).filter(ResearchSource.id == source_id, ResearchSource.research_id == research_id).first()
        if not source:
            raise NotFoundError("Reference")
        db.delete(source)
        db.commit()

    @staticmethod
    def add_bookmark(db: Session, user: User, research_id: int, data: ResearchBookmarkCreate) -> ResearchBookmark:
        session = ResearchStudioService._get_session(db, research_id)
        StudioPlatformService.require_permission(db, user, session.project_id, "research.edit")
        bookmark = ResearchBookmark(
            research_id=research_id,
            title=data.title,
            url=data.url,
            excerpt=data.excerpt,
            color=data.color,
            created_by_id=user.id,
        )
        db.add(bookmark)
        db.commit()
        db.refresh(bookmark)
        return bookmark

    @staticmethod
    def delete_bookmark(db: Session, user: User, research_id: int, bookmark_id: int) -> None:
        session = ResearchStudioService._get_session(db, research_id)
        StudioPlatformService.require_permission(db, user, session.project_id, "research.edit")
        bookmark = db.query(ResearchBookmark).filter(ResearchBookmark.id == bookmark_id, ResearchBookmark.research_id == research_id).first()
        if not bookmark:
            raise NotFoundError("Bookmark")
        db.delete(bookmark)
        db.commit()

    @staticmethod
    def add_fact_check(db: Session, user: User, research_id: int, data: ResearchFactCheckCreate) -> ResearchFactCheck:
        session = ResearchStudioService._get_session(db, research_id)
        StudioPlatformService.require_permission(db, user, session.project_id, "research.edit")
        fc = ResearchFactCheck(
            research_id=research_id,
            claim=data.claim,
            source_id=data.source_id,
            notes=data.notes,
            checked_by_id=user.id,
        )
        db.add(fc)
        db.commit()
        db.refresh(fc)
        return fc

    @staticmethod
    def update_fact_check(db: Session, user: User, research_id: int, fc_id: int, data: ResearchFactCheckUpdate) -> ResearchFactCheck:
        session = ResearchStudioService._get_session(db, research_id)
        StudioPlatformService.require_permission(db, user, session.project_id, "research.edit")
        fc = db.query(ResearchFactCheck).filter(ResearchFactCheck.id == fc_id, ResearchFactCheck.research_id == research_id).first()
        if not fc:
            raise NotFoundError("Fact check")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(fc, field, value)
        fc.checked_by_id = user.id
        db.commit()
        db.refresh(fc)
        return fc

    @staticmethod
    def add_comment(db: Session, user: User, research_id: int, data: ResearchCommentCreate) -> dict:
        session = ResearchStudioService._get_session(db, research_id)
        StudioPlatformService.require_permission(db, user, session.project_id, "research.edit")
        comment = ResearchComment(research_id=research_id, user_id=user.id, content=data.content)
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return {
            "id": comment.id,
            "user_id": comment.user_id,
            "author_name": user.full_name,
            "content": comment.content,
            "created_at": comment.created_at,
        }

    @staticmethod
    def add_timeline_event(db: Session, user: User, research_id: int, data: ResearchTimelineEventCreate) -> ResearchTimelineEvent:
        session = ResearchStudioService._get_session(db, research_id)
        StudioPlatformService.require_permission(db, user, session.project_id, "research.edit")
        event = ResearchTimelineEvent(
            research_id=research_id,
            event_date=data.event_date,
            title=data.title,
            description=data.description,
            event_type=data.event_type,
            created_by_id=user.id,
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def delete_timeline_event(db: Session, user: User, research_id: int, event_id: int) -> None:
        session = ResearchStudioService._get_session(db, research_id)
        StudioPlatformService.require_permission(db, user, session.project_id, "research.edit")
        event = db.query(ResearchTimelineEvent).filter(ResearchTimelineEvent.id == event_id, ResearchTimelineEvent.research_id == research_id).first()
        if not event:
            raise NotFoundError("Timeline event")
        db.delete(event)
        db.commit()

    @staticmethod
    def save_version(db: Session, user: User, research_id: int) -> ResearchVersion:
        session = ResearchStudioService._get_session(db, research_id)
        StudioPlatformService.require_permission(db, user, session.project_id, "research.edit")
        version = ResearchStudioService._create_version_snapshot(db, session, user.id)
        StudioPlatformService.log_activity(db, user.id, "research.version_saved", session.project_id, "research", session.id)
        db.commit()
        db.refresh(version)
        return version

    @staticmethod
    def restore_version(db: Session, user: User, research_id: int, version_id: int) -> ResearchSession:
        session = ResearchStudioService._get_session(db, research_id)
        StudioPlatformService.require_permission(db, user, session.project_id, "research.edit")
        version = db.query(ResearchVersion).filter(ResearchVersion.id == version_id, ResearchVersion.research_id == research_id).first()
        if not version:
            raise NotFoundError("Version")
        session.workspace_content = version.workspace_content
        session.last_auto_saved_at = datetime.now(timezone.utc)
        ResearchStudioService._create_version_snapshot(db, session, user.id)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def run_ai_assistant(db: Session, user: User, research_id: int, data: ResearchAIRequest) -> dict:
        from app.services.research_agent_service import ResearchAgentService
        action = data.action or "full_research"
        result = ResearchAgentService.run_agent(
            db, user, research_id, action, data.prompt,
            provider_id=data.provider,
            apply=True,
        )
        return {
            "summary": result.get("summary", ""),
            "suggestions": result.get("suggestions", []),
            "follow_up_questions": result.get("follow_up_questions", []),
            "statistics": result.get("statistics", []),
            "public_facts": result.get("public_facts", []),
            "generation_id": result.get("interaction_id"),
            "provider": result.get("provider"),
        }

    @staticmethod
    def export_markdown(db: Session, user: User, research_id: int) -> str:
        full = ResearchStudioService.get_full_workspace(db, user, research_id)
        w = full["workspace"]
        lines = [
            f"# {w['topic']}",
            "",
            f"*Project: {w.get('project_title', '')} · Version {w['content_version']}*",
            "",
            "## Workspace",
            "",
            w["workspace_content"] or "",
            "",
        ]
        if w.get("ai_summary"):
            lines.extend(["## AI Summary", "", w["ai_summary"], ""])
        if full["notes"]:
            lines.append("## Notes")
            lines.append("")
            for n in full["notes"]:
                title = n.get("title") or "Untitled"
                lines.extend([f"### {title}", "", n["content"], ""])
        if full["sources"]:
            lines.append("## References")
            lines.append("")
            for s in full["sources"]:
                url = f" — {s.url}" if s.url else ""
                lines.append(f"- **{s.title}** ({s.source_type}){url}")
            lines.append("")
        if full["fact_checks"]:
            lines.append("## Fact Checks")
            lines.append("")
            for fc in full["fact_checks"]:
                lines.append(f"- [{fc.status.upper()}] {fc.claim}")
            lines.append("")
        if full["timeline"]:
            lines.append("## Timeline")
            lines.append("")
            for t in full["timeline"]:
                lines.append(f"- **{t.title}** ({t.event_date.date()}) — {t.description or ''}")
            lines.append("")
        return "\n".join(lines)

    @staticmethod
    def export_pdf_bytes(db: Session, user: User, research_id: int) -> bytes:
        md = ResearchStudioService.export_markdown(db, user, research_id)
        # Minimal PDF without extra dependencies — text lines as PDF objects
        lines = md.replace("\r", "").split("\n")[:120]
        content_lines = []
        y = 750
        for line in lines:
            safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            if len(safe) > 90:
                safe = safe[:87] + "..."
            content_lines.append(f"BT /F1 10 Tf 50 {y} Td ({safe}) Tj ET")
            y -= 14
            if y < 50:
                break
        stream = "\n".join(content_lines)
        pdf = f"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj
4 0 obj<</Length {len(stream)}>>stream
{stream}
endstream endobj
5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000266 00000 n 
trailer<</Size 6/Root 1 0 R>>
startxref
400
%%EOF"""
        return pdf.encode("latin-1", errors="replace")

    @staticmethod
    def export_word(db: Session, user: User, research_id: int) -> bytes:
        md = ResearchStudioService.export_markdown(db, user, research_id)
        rtf = "{\\rtf1\\ansi " + md.replace("\n", "\\par ") + "}"
        return rtf.encode("utf-8", errors="replace")
