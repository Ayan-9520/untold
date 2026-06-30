"""Enterprise Collaboration REST API."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.deps import get_current_studio_user
from app.db.session import get_db
from app.models import User
from app.schemas.collaboration import (
    CollabCommentCreate,
    CollabConflictResolve,
    CollabDocumentSave,
    CollabOverviewResponse,
    CollabPresenceUpdate,
    CollabSharedFileCreate,
)
from app.services.enterprise_collaboration_service import EnterpriseCollaborationService

router = APIRouter(prefix="/studio/platform/collaboration", tags=["Enterprise Collaboration"])


@router.get("/projects/{project_id}/overview", response_model=CollabOverviewResponse)
def collaboration_overview(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return EnterpriseCollaborationService.overview(db, user, project_id)


@router.post("/projects/{project_id}/documents")
def get_or_create_document(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    resource_type: str = Query("script"),
    resource_id: int | None = Query(None),
    title: str = Query("Collaboration Document"),
):
    return EnterpriseCollaborationService.get_or_create_document(
        db, user, project_id, resource_type=resource_type, resource_id=resource_id, title=title
    )


@router.get("/documents/{document_id}")
def get_document(document_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return EnterpriseCollaborationService.get_document(db, user, document_id)


@router.put("/documents/{document_id}")
def save_document(
    document_id: int,
    data: CollabDocumentSave,
    response: Response,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    result = EnterpriseCollaborationService.save_document(db, user, document_id, data)
    if result.get("conflict"):
        if response is not None:
            response.status_code = 409
        return result
    return result


@router.post("/conflicts/{conflict_id}/resolve")
def resolve_conflict(
    conflict_id: int,
    data: CollabConflictResolve,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return EnterpriseCollaborationService.resolve_conflict(db, user, conflict_id, data)


@router.get("/documents/{document_id}/versions")
def list_document_versions(
    document_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return EnterpriseCollaborationService.list_versions(db, user, document_id)


@router.post("/documents/{document_id}/versions/{version}/restore")
def restore_document_version(
    document_id: int,
    version: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return EnterpriseCollaborationService.restore_version(db, user, document_id, version)


@router.post("/projects/{project_id}/presence")
def update_presence(
    project_id: int,
    data: CollabPresenceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return EnterpriseCollaborationService.heartbeat_presence(db, user, project_id, data)


@router.get("/projects/{project_id}/presence")
def list_presence(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return EnterpriseCollaborationService.list_presence(db, user, project_id)


@router.get("/projects/{project_id}/comments")
def list_comments(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    resource_type: str | None = Query(None),
    resource_id: int | None = Query(None),
):
    return EnterpriseCollaborationService.list_comments(
        db, user, project_id, resource_type=resource_type, resource_id=resource_id
    )


@router.post("/projects/{project_id}/comments", status_code=201)
def add_comment(
    project_id: int,
    data: CollabCommentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return EnterpriseCollaborationService.add_comment(db, user, project_id, data)


@router.post("/comments/{comment_id}/resolve")
def resolve_comment(comment_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return EnterpriseCollaborationService.resolve_comment(db, user, comment_id)


@router.get("/projects/{project_id}/files")
def list_shared_files(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return EnterpriseCollaborationService.list_shared_files(db, user, project_id)


@router.post("/projects/{project_id}/files", status_code=201)
def share_file(
    project_id: int,
    data: CollabSharedFileCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return EnterpriseCollaborationService.share_file(db, user, project_id, data)


@router.get("/projects/{project_id}/tasks")
def list_collab_tasks(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return EnterpriseCollaborationService.list_tasks(db, user, project_id)


@router.get("/projects/{project_id}/approvals")
def list_collab_approvals(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return EnterpriseCollaborationService.list_approvals(db, user, project_id)


@router.get("/projects/{project_id}/activity")
def activity_feed(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    limit: int = Query(50, ge=1, le=200),
):
    return EnterpriseCollaborationService.activity_feed(db, user, project_id, limit=limit)


@router.get("/notifications")
def list_collab_notifications(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    limit: int = Query(30, ge=1, le=100),
):
    return EnterpriseCollaborationService.list_notifications(db, user, limit=limit)


@router.post("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return EnterpriseCollaborationService.mark_notification_read(db, user, notification_id)
