"""Asset Library REST API."""

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_studio_user
from app.core.exceptions import ForbiddenError, NotFoundError
from app.db.session import get_db
from app.domain.storage.local import LocalStorageProvider
from app.models import User
from app.schemas.asset_library import (
    AssetLibraryOverview,
    AssetListResponse,
    AssetPermissionCreate,
    AssetPermissionResponse,
    AssetResponse,
    AssetUpdate,
    AssetUploadMetadata,
    AssetVersionResponse,
    CollectionCreate,
    CollectionResponse,
)
from app.services.asset_library_service import AssetLibraryService

router = APIRouter(prefix="/studio/platform/assets", tags=["Asset Library"])


@router.get("/overview", response_model=AssetLibraryOverview)
def asset_overview(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    settings = get_settings()
    if settings.is_development and settings.seed_database:
        AssetLibraryService.seed_demo_assets(db)
    return AssetLibraryService.get_overview(db, user)


@router.get("", response_model=AssetListResponse)
def list_assets(
    folder: str | None = None,
    search: str | None = None,
    tags: str | None = None,
    collection_id: int | None = None,
    favorites_only: bool = False,
    trash: bool = False,
    limit: int = Query(60, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None
    return AssetLibraryService.list_assets(
        db,
        user,
        folder=folder,
        search=search,
        tags=tag_list,
        collection_id=collection_id,
        favorites_only=favorites_only,
        include_deleted=trash,
        limit=limit,
        offset=offset,
    )


@router.post("/upload", response_model=AssetResponse, status_code=201)
async def upload_asset(
    file: UploadFile | None = File(None),
    filename: str | None = Form(None),
    folder: str = Form("images"),
    title: str | None = Form(None),
    project_id: int | None = Form(None),
    collection_id: int | None = Form(None),
    tags: str = Form(""),
    url: str | None = Form(None),
    provider: str | None = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    fname = filename or (file.filename if file else "untitled")
    data = None
    if file:
        data = await file.read()
        max_bytes = get_settings().max_upload_bytes
        if len(data) > max_bytes:
            raise HTTPException(status_code=413, detail=f"File exceeds maximum size of {max_bytes} bytes")
    meta = AssetUploadMetadata(
        filename=fname,
        folder=folder,
        title=title,
        project_id=project_id,
        collection_id=collection_id,
        tags=[t.strip() for t in tags.split(",") if t.strip()],
        mime_type=file.content_type if file else None,
        url=url,
        provider=provider,
    )
    asset = AssetLibraryService.upload_asset(db, user, meta, data)
    return AssetLibraryService._asset_dict(asset, user)


@router.get("/collections/list", response_model=list[CollectionResponse])
def list_collections(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return AssetLibraryService.list_collections(db, user)


@router.post("/collections", response_model=CollectionResponse, status_code=201)
def create_collection(
    data: CollectionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    col = AssetLibraryService.create_collection(db, user, data)
    return {
        "id": col.id,
        "name": col.name,
        "description": col.description,
        "project_id": col.project_id,
        "color": col.color,
        "asset_count": 0,
        "created_at": col.created_at,
    }


@router.patch("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: int,
    data: AssetUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    asset = AssetLibraryService.update_asset(db, user, asset_id, data)
    return AssetLibraryService._asset_dict(asset, user)


@router.post("/{asset_id}/favorite", response_model=AssetResponse)
def toggle_favorite(asset_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    asset = AssetLibraryService.toggle_favorite(db, user, asset_id)
    return AssetLibraryService._asset_dict(asset, user)


@router.delete("/{asset_id}", status_code=204)
def delete_asset(asset_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    AssetLibraryService.soft_delete(db, user, asset_id)


@router.post("/{asset_id}/restore", response_model=AssetResponse)
def restore_asset(asset_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    asset = AssetLibraryService.restore_asset(db, user, asset_id)
    return AssetLibraryService._asset_dict(asset, user)


@router.get("/{asset_id}/versions", response_model=list[AssetVersionResponse])
def list_versions(asset_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return AssetLibraryService.list_versions(db, user, asset_id)


@router.post("/{asset_id}/versions/{version_id}/restore", response_model=AssetResponse)
def restore_version(
    asset_id: int,
    version_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    asset = AssetLibraryService.restore_version(db, user, asset_id, version_id)
    return AssetLibraryService._asset_dict(asset, user)


@router.get("/{asset_id}/permissions", response_model=list[AssetPermissionResponse])
def list_permissions(asset_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return AssetLibraryService.list_permissions(db, user, asset_id)


@router.post("/{asset_id}/permissions", response_model=AssetPermissionResponse, status_code=201)
def add_permission(
    asset_id: int,
    data: AssetPermissionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return AssetLibraryService.add_permission(db, user, asset_id, data)


@router.get("/files/{file_path:path}")
def serve_local_file(
    file_path: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    AssetLibraryService.assert_file_access(db, user, file_path)
    local = LocalStorageProvider()
    try:
        path = local.resolve_path(file_path)
    except ForbiddenError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path)
