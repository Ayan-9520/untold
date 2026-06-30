"""Script Studio REST API."""

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from sqlalchemy.orm import Session

from app.core.deps import get_current_studio_user
from app.db.session import get_db
from app.models import User
from app.schemas.script_studio import (
    ScriptAIHistoryItem,
    ScriptAIRequest,
    ScriptAIResponse,
    ScriptApprovalRequest,
    ScriptApprovalResponse,
    ScriptCommentCreate,
    ScriptCommentResponse,
    ScriptFullResponse,
    ScriptProviderInfo,
    ScriptVersionResponse,
    ScriptVersionSave,
    ScriptWorkspaceAutoSave,
    ScriptWorkspaceResponse,
)
from app.services.script_studio_service import ScriptStudioService

router = APIRouter(prefix="/studio/platform", tags=["Script Studio"])


@router.get("/projects/{project_id}/scripts/workspace", response_model=ScriptWorkspaceResponse)
def get_project_script_workspace(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    script = ScriptStudioService.get_or_create_workspace(db, user, project_id)
    full = ScriptStudioService.get_full_workspace(db, user, script.id)
    return full["workspace"]


@router.get("/scripts/{script_id}", response_model=ScriptFullResponse)
def get_script_workspace(
    script_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return ScriptStudioService.get_full_workspace(db, user, script_id)


@router.patch("/scripts/{script_id}/autosave", response_model=ScriptWorkspaceResponse)
def autosave_script(
    script_id: int,
    data: ScriptWorkspaceAutoSave,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    ScriptStudioService.auto_save(db, user, script_id, data)
    full = ScriptStudioService.get_full_workspace(db, user, script_id)
    return full["workspace"]


@router.post("/scripts/{script_id}/heartbeat")
def script_heartbeat(
    script_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    collabs = ScriptStudioService.heartbeat(db, user, script_id)
    return {"active_collaborators": collabs}


@router.post("/scripts/{script_id}/versions", response_model=ScriptVersionResponse, status_code=201)
def save_script_version(
    script_id: int,
    data: ScriptVersionSave | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    v = ScriptStudioService.save_version(db, user, script_id, data)
    return {
        "id": v.id,
        "version": v.version,
        "content": v.content,
        "style": v.style,
        "snapshot_label": v.snapshot_label,
        "created_by_id": v.created_by_id,
        "author_name": user.full_name,
        "created_at": v.created_at,
    }


@router.post("/scripts/{script_id}/versions/{version_id}/restore", response_model=ScriptWorkspaceResponse)
def restore_script_version(
    script_id: int,
    version_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    ScriptStudioService.restore_version(db, user, script_id, version_id)
    full = ScriptStudioService.get_full_workspace(db, user, script_id)
    return full["workspace"]


@router.post("/scripts/{script_id}/comments", response_model=ScriptCommentResponse, status_code=201)
def add_script_comment(
    script_id: int,
    data: ScriptCommentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return ScriptStudioService.add_comment(db, user, script_id, data)


@router.post("/scripts/{script_id}/approval/request", response_model=ScriptApprovalResponse, status_code=201)
def request_script_approval(
    script_id: int,
    data: ScriptApprovalRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    approval = ScriptStudioService.request_approval(db, user, script_id, data)
    return {
        "id": approval.id,
        "status": approval.status.value if hasattr(approval.status, "value") else str(approval.status),
        "notes": approval.notes,
        "requested_by_id": approval.requested_by_id,
        "approver_id": approval.approver_id,
        "created_at": approval.created_at,
        "resolved_at": approval.resolved_at,
    }


@router.post("/scripts/{script_id}/approval/approve", response_model=ScriptWorkspaceResponse)
def approve_script(
    script_id: int,
    data: ScriptApprovalRequest | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    ScriptStudioService.approve_script(db, user, script_id, data)
    full = ScriptStudioService.get_full_workspace(db, user, script_id)
    return full["workspace"]


@router.post("/scripts/{script_id}/approval/reject", response_model=ScriptWorkspaceResponse)
def reject_script(
    script_id: int,
    data: ScriptApprovalRequest | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    ScriptStudioService.reject_script(db, user, script_id, data)
    full = ScriptStudioService.get_full_workspace(db, user, script_id)
    return full["workspace"]


@router.post("/scripts/{script_id}/ai", response_model=ScriptAIResponse)
def script_ai(
    script_id: int,
    data: ScriptAIRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return ScriptStudioService.run_ai(db, user, script_id, data)


@router.get("/scripts/{script_id}/ai/history", response_model=list[ScriptAIHistoryItem])
def script_ai_history(
    script_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    from app.services.script_agent_service import ScriptAgentService
    return ScriptAgentService.list_history(db, user, script_id)


@router.get("/scripts/providers", response_model=list[ScriptProviderInfo])
def script_providers(user: User = Depends(get_current_studio_user)):
    from app.services.script_agent_service import ScriptAgentService
    return ScriptAgentService.list_providers()


@router.get("/scripts/{script_id}/export/markdown")
def export_script_markdown(
    script_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    content = ScriptStudioService.export_markdown(db, user, script_id)
    return PlainTextResponse(
        content,
        media_type="text/markdown",
        headers={"Content-Disposition": "attachment; filename=script-export.md"},
    )


@router.get("/scripts/{script_id}/export/pdf")
def export_script_pdf(
    script_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    html_doc = ScriptStudioService.export_html_document(db, user, script_id)
    return HTMLResponse(html_doc, headers={"Content-Disposition": "inline; filename=script-export.html"})


@router.get("/scripts/{script_id}/export/word")
def export_script_word(
    script_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    word_html = ScriptStudioService.export_word_html(db, user, script_id)
    return Response(
        content=word_html,
        media_type="application/msword",
        headers={"Content-Disposition": "attachment; filename=script-export.doc"},
    )
