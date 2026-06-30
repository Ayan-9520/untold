"""Research Studio REST API."""

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from sqlalchemy.orm import Session

from app.core.deps import get_current_studio_user, require_project_permission
from app.db.session import get_db
from app.models import User
from app.schemas.research_studio import (
    ResearchAIHistoryItem,
    ResearchAIRequest,
    ResearchAIResponse,
    ResearchApprovalReject,
    ResearchProviderInfo,
    ResearchTopicUpdate,
    ResearchBookmarkCreate,
    ResearchBookmarkResponse,
    ResearchCommentCreate,
    ResearchCommentResponse,
    ResearchFactCheckCreate,
    ResearchFactCheckResponse,
    ResearchFactCheckUpdate,
    ResearchFullResponse,
    ResearchNoteCreate,
    ResearchNoteResponse,
    ResearchNoteUpdate,
    ResearchSourceCreate,
    ResearchSourceResponse,
    ResearchSourceUpdate,
    ResearchTimelineEventCreate,
    ResearchTimelineEventResponse,
    ResearchVersionResponse,
    ResearchWorkspaceAutoSave,
    ResearchWorkspaceResponse,
)
from app.services.research_studio_service import ResearchStudioService

router = APIRouter(prefix="/studio/platform", tags=["Research Studio"])


@router.get("/projects/{project_id}/research/workspace", response_model=ResearchWorkspaceResponse)
def get_project_research_workspace(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_project_permission("project.read")),
):
    session = ResearchStudioService.get_or_create_workspace(db, user, project_id)
    full = ResearchStudioService.get_full_workspace(db, user, session.id)
    return full["workspace"]


@router.get("/research/{research_id}", response_model=ResearchFullResponse)
def get_research_workspace(
    research_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return ResearchStudioService.get_full_workspace(db, user, research_id)


@router.patch("/research/{research_id}/autosave", response_model=ResearchWorkspaceResponse)
def autosave_research(
    research_id: int,
    data: ResearchWorkspaceAutoSave,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    session = ResearchStudioService.auto_save(db, user, research_id, data)
    full = ResearchStudioService.get_full_workspace(db, user, research_id)
    return full["workspace"]


@router.post("/research/{research_id}/notes", response_model=ResearchNoteResponse, status_code=201)
def create_note(research_id: int, data: ResearchNoteCreate, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    note = ResearchStudioService.create_note(db, user, research_id, data)
    return {
        "id": note.id,
        "author_id": note.author_id,
        "author_name": user.full_name,
        "title": note.title,
        "content": note.content,
        "is_pinned": note.is_pinned,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
    }


@router.patch("/research/{research_id}/notes/{note_id}", response_model=ResearchNoteResponse)
def update_note(research_id: int, note_id: int, data: ResearchNoteUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    note = ResearchStudioService.update_note(db, user, research_id, note_id, data)
    return {
        "id": note.id,
        "author_id": note.author_id,
        "author_name": user.full_name,
        "title": note.title,
        "content": note.content,
        "is_pinned": note.is_pinned,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
    }


@router.delete("/research/{research_id}/notes/{note_id}", status_code=204)
def delete_note(research_id: int, note_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    ResearchStudioService.delete_note(db, user, research_id, note_id)


@router.post("/research/{research_id}/sources", response_model=ResearchSourceResponse, status_code=201)
def add_source(research_id: int, data: ResearchSourceCreate, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return ResearchStudioService.add_source(db, user, research_id, data)


@router.patch("/research/{research_id}/sources/{source_id}", response_model=ResearchSourceResponse)
def update_source(research_id: int, source_id: int, data: ResearchSourceUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return ResearchStudioService.update_source(db, user, research_id, source_id, data)


@router.delete("/research/{research_id}/sources/{source_id}", status_code=204)
def delete_source(research_id: int, source_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    ResearchStudioService.delete_source(db, user, research_id, source_id)


@router.post("/research/{research_id}/bookmarks", response_model=ResearchBookmarkResponse, status_code=201)
def add_bookmark(research_id: int, data: ResearchBookmarkCreate, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return ResearchStudioService.add_bookmark(db, user, research_id, data)


@router.delete("/research/{research_id}/bookmarks/{bookmark_id}", status_code=204)
def delete_bookmark(research_id: int, bookmark_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    ResearchStudioService.delete_bookmark(db, user, research_id, bookmark_id)


@router.post("/research/{research_id}/fact-checks", response_model=ResearchFactCheckResponse, status_code=201)
def add_fact_check(research_id: int, data: ResearchFactCheckCreate, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return ResearchStudioService.add_fact_check(db, user, research_id, data)


@router.patch("/research/{research_id}/fact-checks/{fc_id}", response_model=ResearchFactCheckResponse)
def update_fact_check(research_id: int, fc_id: int, data: ResearchFactCheckUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return ResearchStudioService.update_fact_check(db, user, research_id, fc_id, data)


@router.post("/research/{research_id}/comments", response_model=ResearchCommentResponse, status_code=201)
def add_comment(research_id: int, data: ResearchCommentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return ResearchStudioService.add_comment(db, user, research_id, data)


@router.post("/research/{research_id}/timeline", response_model=ResearchTimelineEventResponse, status_code=201)
def add_timeline(research_id: int, data: ResearchTimelineEventCreate, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return ResearchStudioService.add_timeline_event(db, user, research_id, data)


@router.delete("/research/{research_id}/timeline/{event_id}", status_code=204)
def delete_timeline(research_id: int, event_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    ResearchStudioService.delete_timeline_event(db, user, research_id, event_id)


@router.post("/research/{research_id}/versions", response_model=ResearchVersionResponse, status_code=201)
def save_version(research_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    v = ResearchStudioService.save_version(db, user, research_id)
    return {
        "id": v.id,
        "version": v.version,
        "workspace_content": v.workspace_content,
        "created_by_id": v.created_by_id,
        "author_name": user.full_name,
        "created_at": v.created_at,
    }


@router.post("/research/{research_id}/versions/{version_id}/restore", response_model=ResearchWorkspaceResponse)
def restore_version(research_id: int, version_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    ResearchStudioService.restore_version(db, user, research_id, version_id)
    full = ResearchStudioService.get_full_workspace(db, user, research_id)
    return full["workspace"]


@router.post("/research/{research_id}/ai", response_model=ResearchAIResponse)
def ai_assistant(research_id: int, data: ResearchAIRequest, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return ResearchStudioService.run_ai_assistant(db, user, research_id, data)


@router.get("/research/{research_id}/ai/history", response_model=list[ResearchAIHistoryItem])
def ai_history(research_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    from app.services.research_agent_service import ResearchAgentService
    return ResearchAgentService.list_history(db, user, research_id)


@router.get("/research/providers", response_model=list[ResearchProviderInfo])
def research_providers(user: User = Depends(get_current_studio_user)):
    from app.services.research_agent_service import ResearchAgentService
    return ResearchAgentService.list_providers()


@router.patch("/research/{research_id}/topic", response_model=ResearchWorkspaceResponse)
def update_topic(research_id: int, data: ResearchTopicUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    from app.services.research_agent_service import ResearchAgentService
    ResearchAgentService.update_topic(db, user, research_id, data.topic)
    full = ResearchStudioService.get_full_workspace(db, user, research_id)
    return full["workspace"]


@router.post("/research/{research_id}/approval/request", response_model=ResearchWorkspaceResponse)
def request_approval(research_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    from app.services.research_agent_service import ResearchAgentService
    ResearchAgentService.request_approval(db, user, research_id)
    full = ResearchStudioService.get_full_workspace(db, user, research_id)
    return full["workspace"]


@router.post("/research/{research_id}/approval/approve", response_model=ResearchWorkspaceResponse)
def approve_research(research_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    from app.services.research_agent_service import ResearchAgentService
    ResearchAgentService.approve(db, user, research_id)
    full = ResearchStudioService.get_full_workspace(db, user, research_id)
    return full["workspace"]


@router.post("/research/{research_id}/approval/reject", response_model=ResearchWorkspaceResponse)
def reject_research(
    research_id: int,
    data: ResearchApprovalReject | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    from app.services.research_agent_service import ResearchAgentService
    ResearchAgentService.reject(db, user, research_id, data.notes if data else None)
    full = ResearchStudioService.get_full_workspace(db, user, research_id)
    return full["workspace"]


@router.get("/research/{research_id}/sources")
def list_sources_filtered(
    research_id: int,
    search: str | None = None,
    source_type: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    from app.services.research_agent_service import ResearchAgentService
    full = ResearchStudioService.get_full_workspace(db, user, research_id)
    return ResearchAgentService.filter_sources(full["sources"], search=search, source_type=source_type)


@router.get("/research/{research_id}/export/markdown")
def export_markdown(research_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    content = ResearchStudioService.export_markdown(db, user, research_id)
    return PlainTextResponse(content, media_type="text/markdown", headers={"Content-Disposition": "attachment; filename=research-export.md"})


@router.get("/research/{research_id}/export/pdf")
def export_pdf(research_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    md = ResearchStudioService.export_markdown(db, user, research_id)
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Research Export</title>
    <style>body{{font-family:Georgia,serif;max-width:800px;margin:40px auto;padding:0 20px;line-height:1.6}}
    pre{{white-space:pre-wrap;font-family:inherit}}</style></head>
    <body><pre>{md.replace('<', '&lt;').replace('>', '&gt;')}</pre></body></html>"""
    return HTMLResponse(html, headers={"Content-Disposition": "inline; filename=research-export.html"})


@router.get("/research/{research_id}/export/word")
def export_word(research_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    content = ResearchStudioService.export_word(db, user, research_id)
    return Response(
        content=content,
        media_type="application/msword",
        headers={"Content-Disposition": "attachment; filename=research-export.doc"},
    )
