"""UNTOLD Studio platform REST API."""



from datetime import datetime



from fastapi import APIRouter, Depends, Query

from sqlalchemy.orm import Session



from app.core.deps import get_current_studio_user

from app.db.session import get_db

from app.models import User

from app.schemas.studio_platform import (

    AIGenerationCreate,

    AIGenerationResponse,

    CalendarEventCreate,

    CalendarEventResponse,

    CalendarFeedResponse,

    DashboardResponse,

    NotificationResponse,

    ProjectAttachmentCreate,

    ProjectAttachmentResponse,

    ProjectCommentCreate,

    ProjectCommentResponse,

    ProjectCreate,

    ProjectListResponse,

    ProjectMemberAssign,

    ProjectMemberUpdate,

    ProjectResponse,

    ProjectUpdate,

    PublishJobCreate,

    PublishJobResponse,

    ResearchCreate,

    ResearchSessionResponse,

    ResearchSourceCreate,

    ResearchSourceResponse,

    ScriptCreate,

    ScriptResponse,

    ScriptVersionCreate,

    ScriptVersionResponse,

    TaskCreate,

    TaskResponse,

    TaskUpdate,

    TimelineEntryResponse,

)

from app.services.studio_platform_service import StudioPlatformService



router = APIRouter(prefix="/studio/platform", tags=["UNTOLD Studio Platform"])





@router.get("/dashboard", response_model=DashboardResponse)

def studio_dashboard(

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    return StudioPlatformService.get_dashboard(db, user)





@router.get("/projects", response_model=ProjectListResponse)

def list_projects(

    stage: str | None = None,

    status: str | None = None,

    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    items, total = StudioPlatformService.list_projects(
        db, user, limit=limit, offset=offset, stage=stage, status=status
    )
    return ProjectListResponse(
        items=items,
        total=total,
        offset=offset,
        limit=limit,
        has_more=offset + len(items) < total,
    )





@router.post("/projects", response_model=ProjectResponse, status_code=201)

def create_project(

    data: ProjectCreate,

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    return StudioPlatformService.create_project(db, user, data)





@router.get("/projects/{project_id}", response_model=ProjectResponse)

def get_project(

    project_id: int,

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    return StudioPlatformService.get_project(db, user, project_id)





@router.patch("/projects/{project_id}", response_model=ProjectResponse)

def update_project(

    project_id: int,

    data: ProjectUpdate,

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    return StudioPlatformService.update_project(db, user, project_id, data)





@router.delete("/projects/{project_id}", status_code=204)

def delete_project(

    project_id: int,

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    StudioPlatformService.delete_project(db, user, project_id)





@router.post("/projects/{project_id}/publish", response_model=ProjectResponse)

def publish_project(

    project_id: int,

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    return StudioPlatformService.publish_to_originals(db, user, project_id)





@router.post("/projects/{project_id}/members", response_model=ProjectResponse)

def assign_member(

    project_id: int,

    data: ProjectMemberAssign,

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    return StudioPlatformService.assign_member(db, user, project_id, data)





@router.patch("/projects/{project_id}/members/{member_user_id}", response_model=ProjectResponse)

def update_member(

    project_id: int,

    member_user_id: int,

    data: ProjectMemberUpdate,

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    return StudioPlatformService.update_member(db, user, project_id, member_user_id, data)





@router.delete("/projects/{project_id}/members/{member_user_id}", response_model=ProjectResponse)

def remove_member(

    project_id: int,

    member_user_id: int,

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    return StudioPlatformService.remove_member(db, user, project_id, member_user_id)





@router.get("/projects/{project_id}/comments", response_model=list[ProjectCommentResponse])

def list_comments(

    project_id: int,

    limit: int = Query(50, ge=1, le=200),

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    return StudioPlatformService.list_comments(db, user, project_id, limit=limit)





@router.post("/projects/{project_id}/comments", response_model=ProjectCommentResponse, status_code=201)

def add_comment(

    project_id: int,

    data: ProjectCommentCreate,

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    return StudioPlatformService.add_comment(db, user, project_id, data)





@router.delete("/projects/{project_id}/comments/{comment_id}", status_code=204)

def delete_comment(

    project_id: int,

    comment_id: int,

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    StudioPlatformService.delete_comment(db, user, project_id, comment_id)





@router.get("/projects/{project_id}/attachments", response_model=list[ProjectAttachmentResponse])

def list_attachments(

    project_id: int,

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    assets = StudioPlatformService.list_attachments(db, user, project_id)

    return [

        {

            "id": a.id,

            "project_id": a.project_id,

            "filename": a.filename,

            "url": a.url,

            "asset_type": a.asset_type.value if hasattr(a.asset_type, "value") else str(a.asset_type),

            "size_bytes": a.size_bytes,

            "mime_type": a.mime_type,

            "created_at": a.created_at,

        }

        for a in assets

    ]





@router.post("/projects/{project_id}/attachments", response_model=ProjectAttachmentResponse, status_code=201)

def add_attachment(

    project_id: int,

    data: ProjectAttachmentCreate,

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    asset = StudioPlatformService.add_attachment(db, user, project_id, data)

    return {

        "id": asset.id,

        "project_id": asset.project_id,

        "filename": asset.filename,

        "url": asset.url,

        "asset_type": asset.asset_type.value if hasattr(asset.asset_type, "value") else str(asset.asset_type),

        "size_bytes": asset.size_bytes,

        "mime_type": asset.mime_type,

        "created_at": asset.created_at,

    }





@router.delete("/projects/{project_id}/attachments/{attachment_id}", status_code=204)

def delete_attachment(

    project_id: int,

    attachment_id: int,

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    StudioPlatformService.delete_attachment(db, user, project_id, attachment_id)





@router.get("/projects/{project_id}/timeline", response_model=list[TimelineEntryResponse])

def get_timeline(

    project_id: int,

    limit: int = Query(50, ge=1, le=200),

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    return StudioPlatformService.get_timeline(db, user, project_id, limit=limit)





@router.get("/projects/{project_id}/tasks", response_model=list[TaskResponse])

def list_project_tasks(

    project_id: int,

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    return StudioPlatformService.list_project_tasks(db, user, project_id)





@router.get("/calendar", response_model=CalendarFeedResponse)

def calendar_feed(

    from_date: datetime = Query(..., alias="from"),

    to_date: datetime = Query(..., alias="to"),

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    return StudioPlatformService.get_calendar_feed(db, user, from_date, to_date)





@router.post("/calendar/events", response_model=CalendarEventResponse, status_code=201)

def create_calendar_event(

    data: CalendarEventCreate,

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    event = StudioPlatformService.create_calendar_event(db, user, data)

    return {

        "id": event.id,

        "project_id": event.project_id,

        "project_title": None,

        "title": event.title,

        "start_at": event.start_at,

        "end_at": event.end_at,

        "event_type": event.event_type,

        "created_at": event.created_at,

    }





@router.post("/projects/{project_id}/research", response_model=ResearchSessionResponse, status_code=201)

def create_research(

    project_id: int,

    data: ResearchCreate,

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    return StudioPlatformService.create_research(db, user, project_id, data)





@router.post("/research/{research_id}/sources", response_model=ResearchSourceResponse, status_code=201)

def add_research_source(

    research_id: int,

    data: ResearchSourceCreate,

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    return StudioPlatformService.add_research_source(db, user, research_id, data)





@router.post("/research/{research_id}/approve", response_model=ResearchSessionResponse)

def approve_research(

    research_id: int,

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    return StudioPlatformService.approve_research(db, user, research_id)





@router.post("/projects/{project_id}/scripts", response_model=ScriptResponse, status_code=201)

def create_script(

    project_id: int,

    data: ScriptCreate,

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    return StudioPlatformService.create_script(db, user, project_id, data)





@router.post("/scripts/{script_id}/versions", response_model=ScriptVersionResponse, status_code=201)

def add_script_version(

    script_id: int,

    data: ScriptVersionCreate,

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    return StudioPlatformService.add_script_version(db, user, script_id, data)





@router.post("/ai/generate", response_model=AIGenerationResponse, status_code=201)

def queue_ai_generation(

    data: AIGenerationCreate,

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    return StudioPlatformService.queue_ai_generation(db, user, data)





@router.post("/tasks", response_model=TaskResponse, status_code=201)

def create_task(

    data: TaskCreate,

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    return StudioPlatformService.create_task(db, user, data)





@router.patch("/tasks/{task_id}", response_model=TaskResponse)

def update_task(

    task_id: int,

    data: TaskUpdate,

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    return StudioPlatformService.update_task(db, user, task_id, data)





@router.delete("/tasks/{task_id}", status_code=204)

def delete_task(

    task_id: int,

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    StudioPlatformService.delete_task(db, user, task_id)





@router.post("/projects/{project_id}/publish-jobs", response_model=PublishJobResponse, status_code=201)

def schedule_publish(

    project_id: int,

    data: PublishJobCreate,

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    return StudioPlatformService.schedule_publish(db, user, project_id, data)





@router.get("/notifications", response_model=list[NotificationResponse])

def list_notifications(

    limit: int = Query(50, ge=1, le=200),

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    return StudioPlatformService.list_notifications(db, user, limit=limit)





@router.post("/notifications/{notification_id}/read", response_model=NotificationResponse)

def mark_notification_read(

    notification_id: int,

    db: Session = Depends(get_db),

    user: User = Depends(get_current_studio_user),

):

    return StudioPlatformService.mark_notification_read(db, user, notification_id)

