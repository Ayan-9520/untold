"""Timeline Editor REST API."""

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.deps import get_current_studio_user
from app.db.session import get_db
from app.models import User
from app.schemas.timeline_editor import (
    TimelineExportCreate,
    TimelineExportResponse,
    TimelineSaveRequest,
    TimelineSaveResponse,
    TimelineSnapshotResponse,
    TimelineWorkspaceResponse,
)
from app.services.timeline_editor_service import TimelineEditorService

router = APIRouter(prefix="/studio/platform", tags=["Timeline Editor"])


@router.get("/projects/{project_id}/timeline-editor", response_model=TimelineWorkspaceResponse)
def get_timeline_workspace(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return TimelineEditorService.get_workspace(db, user, project_id)


@router.put("/projects/{project_id}/timeline-editor", response_model=TimelineSaveResponse)
def save_timeline(
    project_id: int,
    data: TimelineSaveRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return TimelineEditorService.save_timeline(db, user, project_id, data)


@router.post("/projects/{project_id}/timeline-editor/snapshots", response_model=TimelineSnapshotResponse, status_code=201)
def create_timeline_snapshot(
    project_id: int,
    label: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    snap = TimelineEditorService.create_snapshot(db, user, project_id, label)
    return snap


@router.get("/projects/{project_id}/timeline-editor/snapshots", response_model=list[TimelineSnapshotResponse])
def list_timeline_snapshots(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return TimelineEditorService.list_snapshots(db, user, project_id)


@router.get("/projects/{project_id}/timeline-editor/exports", response_model=list[TimelineExportResponse])
def list_timeline_exports(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return TimelineEditorService.list_exports(db, user, project_id)


@router.post("/projects/{project_id}/timeline-editor/exports", response_model=TimelineExportResponse, status_code=201)
def create_timeline_export(
    project_id: int,
    data: TimelineExportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return TimelineEditorService.create_export(db, user, project_id, data)


@router.get("/timeline/exports/{job_id}/demo.{ext}")
def demo_export_file(job_id: int, ext: str):
    """Placeholder export file for demo renders."""
    return Response(
        content=b"UNTOLD Timeline Editor demo export placeholder",
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="export-{job_id}.{ext}"'},
    )
