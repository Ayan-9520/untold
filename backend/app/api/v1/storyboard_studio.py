"""Storyboard Studio REST API."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_studio_user
from app.db.session import get_db
from app.models import User
from app.schemas.storyboard_studio import (
    StoryboardAIGenerateRequest,
    StoryboardAIGenerateResponse,
    StoryboardAIHistoryItem,
    StoryboardApprovalRequest,
    StoryboardApprovalResponse,
    StoryboardImportRequest,
    StoryboardProviderInfo,
    StoryboardReorderRequest,
    StoryboardRevisionResponse,
    StoryboardRevisionSave,
    StoryboardSceneCreate,
    StoryboardSceneResponse,
    StoryboardSceneUpdate,
    StoryboardWorkspaceResponse,
)
from app.services.storyboard_studio_service import StoryboardStudioService

router = APIRouter(prefix="/studio/platform", tags=["Storyboard Studio"])


@router.get("/projects/{project_id}/storyboard", response_model=StoryboardWorkspaceResponse)
def get_storyboard_workspace(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return StoryboardStudioService.get_workspace(db, user, project_id)


@router.post("/projects/{project_id}/storyboard/import-script", response_model=StoryboardWorkspaceResponse)
def import_storyboard_from_script(
    project_id: int,
    data: StoryboardImportRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return StoryboardStudioService.import_from_script(db, user, project_id, data)


@router.post("/projects/{project_id}/storyboard/ai/generate", response_model=StoryboardAIGenerateResponse)
def ai_generate_storyboard(
    project_id: int,
    data: StoryboardAIGenerateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    from app.services.storyboard_agent_service import StoryboardAgentService

    return StoryboardAgentService.generate_from_script(
        db,
        user,
        project_id,
        replace_existing=data.replace_existing,
        default_duration_seconds=data.default_duration_seconds,
        prompt=data.prompt,
        provider_id=data.provider,
    )


@router.get("/projects/{project_id}/storyboard/ai/history", response_model=list[StoryboardAIHistoryItem])
def storyboard_ai_history(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    from app.services.storyboard_agent_service import StoryboardAgentService

    return StoryboardAgentService.list_history(db, user, project_id)


@router.get("/storyboard/providers", response_model=list[StoryboardProviderInfo])
def storyboard_providers(user: User = Depends(get_current_studio_user)):
    from app.services.storyboard_agent_service import StoryboardAgentService

    return StoryboardAgentService.list_providers()


@router.post("/projects/{project_id}/storyboard/scenes", response_model=StoryboardSceneResponse, status_code=201)
def create_storyboard_scene(
    project_id: int,
    data: StoryboardSceneCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    scene = StoryboardStudioService.create_scene(db, user, project_id, data)
    return StoryboardStudioService._scene_dict(scene)


@router.patch("/projects/{project_id}/storyboard/scenes/{scene_id}", response_model=StoryboardSceneResponse)
def update_storyboard_scene(
    project_id: int,
    scene_id: int,
    data: StoryboardSceneUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    scene = StoryboardStudioService.update_scene(db, user, project_id, scene_id, data)
    return StoryboardStudioService._scene_dict(scene)


@router.delete("/projects/{project_id}/storyboard/scenes/{scene_id}", status_code=204)
def delete_storyboard_scene(
    project_id: int,
    scene_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    StoryboardStudioService.delete_scene(db, user, project_id, scene_id)


@router.post("/projects/{project_id}/storyboard/reorder", response_model=StoryboardWorkspaceResponse)
def reorder_storyboard_scenes(
    project_id: int,
    data: StoryboardReorderRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return StoryboardStudioService.reorder_scenes(db, user, project_id, data.scene_ids)


@router.post("/projects/{project_id}/storyboard/revisions", response_model=StoryboardRevisionResponse, status_code=201)
def save_storyboard_revision(
    project_id: int,
    data: StoryboardRevisionSave | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    revision = StoryboardStudioService.save_revision(db, user, project_id, data)
    return {
        "id": revision.id,
        "project_id": revision.project_id,
        "version": revision.version,
        "label": revision.label,
        "scene_count": len(revision.scenes_snapshot or []),
        "created_by_id": revision.created_by_id,
        "author_name": user.full_name,
        "created_at": revision.created_at,
    }


@router.post("/projects/{project_id}/storyboard/revisions/{revision_id}/restore", response_model=StoryboardWorkspaceResponse)
def restore_storyboard_revision(
    project_id: int,
    revision_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return StoryboardStudioService.restore_revision(db, user, project_id, revision_id)


@router.post("/projects/{project_id}/storyboard/approval/request", response_model=StoryboardApprovalResponse, status_code=201)
def request_storyboard_approval(
    project_id: int,
    data: StoryboardApprovalRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    approval = StoryboardStudioService.request_approval(db, user, project_id, data)
    return {
        "id": approval.id,
        "status": approval.status.value if hasattr(approval.status, "value") else str(approval.status),
        "notes": approval.notes,
        "requested_by_id": approval.requested_by_id,
        "approver_id": approval.approver_id,
        "created_at": approval.created_at,
        "resolved_at": approval.resolved_at,
    }


@router.post("/projects/{project_id}/storyboard/approval/approve", response_model=StoryboardWorkspaceResponse)
def approve_storyboard(
    project_id: int,
    data: StoryboardApprovalRequest | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return StoryboardStudioService.approve_storyboard(db, user, project_id, data)


@router.post("/projects/{project_id}/storyboard/approval/reject", response_model=StoryboardWorkspaceResponse)
def reject_storyboard(
    project_id: int,
    data: StoryboardApprovalRequest | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return StoryboardStudioService.reject_storyboard(db, user, project_id, data)
