"""Studio content pipeline — research, script, AI jobs, tasks, publishing, calendar."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import NotFoundError
from app.domain.studio.enums import AIGenerationStatus, ApprovalStatus
from app.domain.studio.permissions import StudioPermissionService
from app.models import User
from app.models.studio import (
    AIGeneration,
    CalendarEvent,
    PublishJob,
    ResearchSession,
    ResearchSource,
    Script,
    ScriptVersion,
    StudioApproval,
    StudioNotification,
    StudioProjectMember,
    StudioTask,
)
from app.models.studio.core import Production
from app.repositories.notification_repository import NotificationRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.studio_platform import (
    AIGenerationCreate,
    CalendarEventCreate,
    PublishJobCreate,
    ResearchCreate,
    ResearchSourceCreate,
    ScriptCreate,
    ScriptVersionCreate,
    TaskCreate,
    TaskUpdate,
)
from app.services.studio.activity_service import StudioActivityService
from app.services.studio.project_service import StudioProjectService


class StudioPipelineService:
    @staticmethod
    def create_research(db: Session, user: User, project_id: int, data: ResearchCreate) -> ResearchSession:
        StudioPermissionService.require_permission(db, user, project_id, "research.edit")
        session = ResearchSession(project_id=project_id, topic=data.topic)
        db.add(session)
        db.flush()
        StudioActivityService.log_activity(db, user.id, "research.created", project_id, "research", session.id)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def add_research_source(db: Session, user: User, research_id: int, data: ResearchSourceCreate) -> ResearchSource:
        research = db.query(ResearchSession).filter(ResearchSession.id == research_id).first()
        if not research:
            raise NotFoundError("Research session")
        StudioPermissionService.require_permission(db, user, research.project_id, "research.edit")
        source = ResearchSource(
            research_id=research_id,
            title=data.title,
            url=data.url,
            source_type=data.source_type,
            credibility_score=data.credibility_score,
            notes=data.notes,
        )
        db.add(source)
        project = ProjectRepository(db).get_by_id(research.project_id)
        if project:
            project.sources_count = (project.sources_count or 0) + 1
        db.commit()
        db.refresh(source)
        return source

    @staticmethod
    def approve_research(db: Session, user: User, research_id: int) -> ResearchSession:
        research = (
            db.query(ResearchSession)
            .options(joinedload(ResearchSession.sources))
            .filter(ResearchSession.id == research_id)
            .first()
        )
        if not research:
            raise NotFoundError("Research session")
        StudioPermissionService.require_permission(db, user, research.project_id, "research.approve")
        research.status = "approved"
        research.approved_at = datetime.now(timezone.utc)
        research.approved_by_id = user.id
        db.add(
            StudioApproval(
                project_id=research.project_id,
                entity_type="research",
                entity_id=research.id,
                requested_by_id=user.id,
                approver_id=user.id,
                status=ApprovalStatus.APPROVED,
                resolved_at=datetime.now(timezone.utc),
            )
        )
        db.commit()
        db.refresh(research)
        return research

    @staticmethod
    def create_script(db: Session, user: User, project_id: int, data: ScriptCreate) -> Script:
        StudioPermissionService.require_permission(db, user, project_id, "script.edit")
        script = Script(project_id=project_id, title=data.title)
        db.add(script)
        db.flush()
        version = ScriptVersion(script_id=script.id, version=1, content="", created_by_id=user.id)
        db.add(version)
        db.flush()
        script.current_version_id = version.id
        StudioActivityService.log_activity(db, user.id, "script.created", project_id, "script", script.id)
        db.commit()
        db.refresh(script)
        return script

    @staticmethod
    def add_script_version(db: Session, user: User, script_id: int, data: ScriptVersionCreate) -> ScriptVersion:
        script = db.query(Script).filter(Script.id == script_id).first()
        if not script:
            raise NotFoundError("Script")
        StudioPermissionService.require_permission(db, user, script.project_id, "script.edit")
        latest = db.query(func.max(ScriptVersion.version)).filter(ScriptVersion.script_id == script_id).scalar() or 0
        version = ScriptVersion(
            script_id=script_id,
            version=int(latest) + 1,
            content=data.content,
            style=data.style,
            created_by_id=user.id,
        )
        db.add(version)
        db.flush()
        script.current_version_id = version.id
        project = ProjectRepository(db).get_by_id(script.project_id)
        if project:
            project.version = version.version
        db.commit()
        db.refresh(version)
        return version

    @staticmethod
    def queue_ai_generation(db: Session, user: User, data: AIGenerationCreate) -> AIGeneration:
        perm_project = data.project_id
        StudioPermissionService.require_permission(db, user, perm_project, "ai.generate")
        gen = AIGeneration(
            project_id=data.project_id,
            module=data.module,
            prompt=data.prompt,
            parameters=data.parameters,
            status=AIGenerationStatus.QUEUED,
            created_by_id=user.id,
        )
        db.add(gen)
        db.flush()
        from app.workers.studio_tasks import run_ai_generation

        task = run_ai_generation.delay(gen.id)
        gen.celery_task_id = task.id
        db.commit()
        db.refresh(gen)
        return gen

    @staticmethod
    def create_task(db: Session, user: User, data: TaskCreate) -> StudioTask:
        if data.project_id:
            StudioPermissionService.require_permission(db, user, data.project_id, "project.update")
        task = StudioTask(
            project_id=data.project_id,
            title=data.title,
            description=data.description,
            assignee_id=data.assignee_id,
            due_date=data.due_date,
            priority=data.priority,
            created_by_id=user.id,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def schedule_publish(db: Session, user: User, project_id: int, data: PublishJobCreate) -> PublishJob:
        StudioPermissionService.require_permission(db, user, project_id, "publish.schedule")
        job = PublishJob(
            project_id=project_id,
            platform=data.platform,
            scheduled_at=data.scheduled_at,
            requires_approval=data.requires_approval,
            meta=data.meta,
            created_by_id=user.id,
        )
        db.add(job)
        if data.platform.value == "originals" and not data.requires_approval:
            StudioProjectService.publish_to_originals(db, user, project_id)
            job.status = "published"
            job.published_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def list_notifications(db: Session, user: User, limit: int = 50) -> list[StudioNotification]:
        return NotificationRepository(db).list_for_user(user.id, limit)

    @staticmethod
    def mark_notification_read(db: Session, user: User, notification_id: int) -> StudioNotification:
        note = NotificationRepository(db).get_for_user(user.id, notification_id)
        if not note:
            raise NotFoundError("Notification")
        note.is_read = True
        db.commit()
        db.refresh(note)
        return note

    @staticmethod
    def list_project_tasks(db: Session, user: User, project_id: int):
        StudioPermissionService.require_permission(db, user, project_id, "project.read")
        return (
            db.query(StudioTask)
            .filter(StudioTask.project_id == project_id)
            .order_by(StudioTask.due_date.asc().nullslast())
            .all()
        )

    @staticmethod
    def update_task(db: Session, user: User, task_id: int, data: TaskUpdate):
        task = db.query(StudioTask).filter(StudioTask.id == task_id).first()
        if not task:
            raise NotFoundError("Task")
        if task.project_id:
            StudioPermissionService.require_permission(db, user, task.project_id, "project.update")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(task, field, value)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def delete_task(db: Session, user: User, task_id: int) -> None:
        task = db.query(StudioTask).filter(StudioTask.id == task_id).first()
        if not task:
            raise NotFoundError("Task")
        if task.project_id:
            StudioPermissionService.require_permission(db, user, task.project_id, "project.update")
        db.delete(task)
        db.commit()

    @staticmethod
    def get_calendar_feed(db: Session, user: User, from_dt: datetime, to_dt: datetime):
        projects = ProjectRepository(db).list_due_between(user, from_dt, to_dt)
        events = (
            db.query(CalendarEvent, Production.title)
            .outerjoin(Production, Production.id == CalendarEvent.project_id)
            .filter(CalendarEvent.start_at >= from_dt, CalendarEvent.start_at <= to_dt)
            .order_by(CalendarEvent.start_at.asc())
            .all()
        )
        tasks = (
            db.query(StudioTask)
            .filter(
                StudioTask.due_date.isnot(None),
                StudioTask.due_date >= from_dt,
                StudioTask.due_date <= to_dt,
            )
            .order_by(StudioTask.due_date.asc())
            .all()
        )
        return {
            "projects": [StudioProjectService.to_response(db, p) for p in projects],
            "events": [
                {
                    "id": e.id,
                    "project_id": e.project_id,
                    "project_title": title,
                    "title": e.title,
                    "start_at": e.start_at,
                    "end_at": e.end_at,
                    "event_type": e.event_type,
                    "created_at": e.created_at,
                }
                for e, title in events
            ],
            "tasks": tasks,
        }

    @staticmethod
    def create_calendar_event(db: Session, user: User, data: CalendarEventCreate):
        if data.project_id:
            StudioPermissionService.require_permission(db, user, data.project_id, "project.update")
        event = CalendarEvent(
            project_id=data.project_id,
            title=data.title,
            start_at=data.start_at,
            end_at=data.end_at,
            event_type=data.event_type,
            created_by_id=user.id,
        )
        db.add(event)
        db.flush()
        if data.project_id:
            StudioActivityService.log_activity(
                db, user.id, "calendar.event_created", data.project_id, "calendar", event.id
            )
        db.commit()
        db.refresh(event)
        return event
