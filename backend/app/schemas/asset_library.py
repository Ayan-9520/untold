"""Asset Library Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase

ASSET_FOLDERS = ("images", "videos", "audio", "documents", "thumbnails", "posters")


class AssetResponse(ORMBase):
    id: int
    project_id: int | None
    title: str | None
    filename: str
    asset_type: str
    folder: str
    url: str | None
    preview_url: str | None
    size_bytes: int
    mime_type: str | None
    tags: list[str]
    is_favorite: bool
    is_deleted: bool
    version: int
    cloud_provider: str
    collection_id: int | None
    collection_name: str | None = None
    uploaded_by_id: int | None
    uploader_name: str | None = None
    created_at: datetime
    updated_at: datetime | None


class AssetListResponse(BaseModel):
    items: list[AssetResponse]
    total: int
    folder_counts: dict[str, int]


class AssetUploadMetadata(BaseModel):
    filename: str = Field(min_length=1, max_length=500)
    folder: str = "images"
    title: str | None = Field(default=None, max_length=500)
    project_id: int | None = None
    collection_id: int | None = None
    tags: list[str] = Field(default_factory=list)
    mime_type: str | None = None
    url: str | None = None
    provider: str | None = None


class AssetUpdate(BaseModel):
    title: str | None = None
    folder: str | None = None
    tags: list[str] | None = None
    is_favorite: bool | None = None
    collection_id: int | None = None
    project_id: int | None = None


class CollectionResponse(ORMBase):
    id: int
    name: str
    description: str | None
    project_id: int | None
    color: str
    asset_count: int = 0
    created_at: datetime


class CollectionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=300)
    description: str | None = None
    project_id: int | None = None
    color: str = "gold"


class AssetVersionResponse(ORMBase):
    id: int
    asset_id: int
    version: int
    filename: str
    url: str | None
    size_bytes: int
    mime_type: str | None
    created_by_id: int | None
    author_name: str | None = None
    created_at: datetime


class AssetPermissionResponse(ORMBase):
    id: int
    asset_id: int
    user_id: int | None
    role: str | None
    permission: str
    created_at: datetime


class AssetPermissionCreate(BaseModel):
    user_id: int | None = None
    role: str | None = None
    permission: str = "read"


class AssetLibraryOverview(BaseModel):
    total_assets: int
    total_bytes: int
    folder_counts: dict[str, int]
    favorites_count: int
    trash_count: int
    collections_count: int
    storage_providers: list[dict]
