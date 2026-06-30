"""UNTOLD Studio platform — backward-compatible facade.

Delegates to bounded-context services under ``app.services.studio``.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.domain.studio.enums import StudioRole
from app.domain.studio.permissions import StudioPermissionService
from app.models import User
from app.models.studio import (
    AIGeneration,
    PublishJob,
    ResearchSession,
    ResearchSource,
    Script,
    ScriptVersion,
    StudioNotification,
    StudioTask,
)
from app.schemas.studio_platform import (
    AIGenerationCreate,
    CalendarEventCreate,
    DashboardResponse,
    ProjectAttachmentCreate,
    ProjectCommentCreate,
    ProjectCreate,
    ProjectMemberAssign,
    ProjectMemberUpdate,
    ProjectResponse,
    ProjectUpdate,
    PublishJobCreate,
    ResearchCreate,
    ResearchSourceCreate,
    ScriptCreate,
    ScriptVersionCreate,
    TaskCreate,
    TaskUpdate,
)
from app.services.studio.activity_service import StudioActivityService
from app.services.studio.dashboard_service import StudioDashboardService
from app.services.studio.pipeline_service import StudioPipelineService
from app.services.studio.project_service import StudioProjectService


class StudioPlatformService:
    """Facade preserving the original static API surface."""

    # --- Permissions (domain layer) ---
    _member_role = staticmethod(StudioPermissionService.member_role)
    require_permission = staticmethod(StudioPermissionService.require_permission)

    # --- Activity ---
    log_activity = staticmethod(StudioActivityService.log_activity)
    notify = staticmethod(StudioActivityService.notify)

    # --- Projects ---
    _project_to_response = staticmethod(StudioProjectService.to_response)
    list_projects = staticmethod(StudioProjectService.list_projects)
    get_project = staticmethod(StudioProjectService.get_project)
    create_project = staticmethod(StudioProjectService.create_project)
    update_project = staticmethod(StudioProjectService.update_project)
    publish_to_originals = staticmethod(StudioProjectService.publish_to_originals)
    delete_project = staticmethod(StudioProjectService.delete_project)
    assign_member = staticmethod(StudioProjectService.assign_member)
    update_member = staticmethod(StudioProjectService.update_member)
    remove_member = staticmethod(StudioProjectService.remove_member)
    list_comments = staticmethod(StudioProjectService.list_comments)
    add_comment = staticmethod(StudioProjectService.add_comment)
    delete_comment = staticmethod(StudioProjectService.delete_comment)
    list_attachments = staticmethod(StudioProjectService.list_attachments)
    add_attachment = staticmethod(StudioProjectService.add_attachment)
    delete_attachment = staticmethod(StudioProjectService.delete_attachment)
    get_timeline = staticmethod(StudioProjectService.get_timeline)

    # --- Dashboard ---
    get_dashboard = staticmethod(StudioDashboardService.get_dashboard)

    # --- Pipeline ---
    create_research = staticmethod(StudioPipelineService.create_research)
    add_research_source = staticmethod(StudioPipelineService.add_research_source)
    approve_research = staticmethod(StudioPipelineService.approve_research)
    create_script = staticmethod(StudioPipelineService.create_script)
    add_script_version = staticmethod(StudioPipelineService.add_script_version)
    queue_ai_generation = staticmethod(StudioPipelineService.queue_ai_generation)
    create_task = staticmethod(StudioPipelineService.create_task)
    schedule_publish = staticmethod(StudioPipelineService.schedule_publish)
    list_notifications = staticmethod(StudioPipelineService.list_notifications)
    mark_notification_read = staticmethod(StudioPipelineService.mark_notification_read)
    list_project_tasks = staticmethod(StudioPipelineService.list_project_tasks)
    update_task = staticmethod(StudioPipelineService.update_task)
    delete_task = staticmethod(StudioPipelineService.delete_task)
    get_calendar_feed = staticmethod(StudioPipelineService.get_calendar_feed)
    create_calendar_event = staticmethod(StudioPipelineService.create_calendar_event)
