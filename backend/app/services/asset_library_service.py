"""Asset Library — upload, folders, collections, versions, trash, permissions."""

from __future__ import annotations

import mimetypes
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.domain.studio.enums import ASSET_FOLDERS, AssetType
from app.domain.storage.local import LocalStorageProvider
from app.domain.storage.registry import get_storage_registry, resolve_storage_provider, upload_bytes
from app.models import User
from app.models.studio_platform import AssetCollection, AssetPermission, AssetVersion, StudioAsset
from app.schemas.asset_library import AssetPermissionCreate, AssetUpdate, AssetUploadMetadata, CollectionCreate
from app.services.studio_platform_service import StudioPlatformService

_FOLDER_TO_TYPE: dict[str, AssetType] = {
    "images": AssetType.IMAGE,
    "videos": AssetType.VIDEO,
    "audio": AssetType.AUDIO,
    "documents": AssetType.DOCUMENT,
    "thumbnails": AssetType.THUMBNAIL,
    "posters": AssetType.POSTER,
}


class AssetLibraryService:
    @staticmethod
    def _asset_dict(asset: StudioAsset, uploader: User | None = None, collection: AssetCollection | None = None) -> dict:
        return {
            "id": asset.id,
            "project_id": asset.project_id,
            "title": asset.title or asset.filename,
            "filename": asset.filename,
            "asset_type": asset.asset_type.value if hasattr(asset.asset_type, "value") else str(asset.asset_type),
            "folder": asset.folder,
            "url": asset.url,
            "preview_url": asset.preview_url or asset.url,
            "size_bytes": asset.size_bytes,
            "mime_type": asset.mime_type,
            "tags": asset.tags or [],
            "is_favorite": asset.is_favorite,
            "is_deleted": asset.is_deleted,
            "version": asset.version,
            "cloud_provider": asset.cloud_provider,
            "collection_id": asset.collection_id,
            "collection_name": collection.name if collection else None,
            "uploaded_by_id": asset.uploaded_by_id,
            "uploader_name": uploader.full_name if uploader else None,
            "created_at": asset.created_at,
            "updated_at": asset.updated_at,
        }

    @staticmethod
    def _guess_folder(mime: str | None, filename: str) -> str:
        if mime:
            if mime.startswith("image/"):
                return "images"
            if mime.startswith("video/"):
                return "videos"
            if mime.startswith("audio/"):
                return "audio"
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext in {"jpg", "jpeg", "png", "gif", "webp", "svg"}:
            return "images"
        if ext in {"mp4", "mov", "webm", "mkv"}:
            return "videos"
        if ext in {"mp3", "wav", "aac", "flac"}:
            return "audio"
        if ext in {"pdf", "doc", "docx", "txt"}:
            return "documents"
        return "documents"

    @staticmethod
    def get_overview(db: Session, user: User) -> dict:
        StudioPlatformService.require_permission(db, user, None, "asset.read")
        total = db.query(func.count(StudioAsset.id)).filter(StudioAsset.is_deleted.is_(False)).scalar() or 0
        total_bytes = (
            db.query(func.coalesce(func.sum(StudioAsset.size_bytes), 0))
            .filter(StudioAsset.is_deleted.is_(False))
            .scalar()
            or 0
        )
        folder_counts = {f: 0 for f in ASSET_FOLDERS}
        rows = (
            db.query(StudioAsset.folder, func.count(StudioAsset.id))
            .filter(StudioAsset.is_deleted.is_(False))
            .group_by(StudioAsset.folder)
            .all()
        )
        for folder, count in rows:
            folder_counts[folder] = count
        favorites = (
            db.query(func.count(StudioAsset.id))
            .filter(StudioAsset.is_favorite.is_(True), StudioAsset.is_deleted.is_(False))
            .scalar()
            or 0
        )
        trash = db.query(func.count(StudioAsset.id)).filter(StudioAsset.is_deleted.is_(True)).scalar() or 0
        collections = db.query(func.count(AssetCollection.id)).scalar() or 0
        providers = [
            {"id": p.id, "label": p.label, "available": p.is_available()}
            for p in get_storage_registry().values()
        ]
        return {
            "total_assets": total,
            "total_bytes": int(total_bytes),
            "folder_counts": folder_counts,
            "favorites_count": favorites,
            "trash_count": trash,
            "collections_count": collections,
            "storage_providers": providers,
        }

    @staticmethod
    def assert_file_access(db: Session, user: User, file_path: str) -> None:
        """Ensure the studio user may download a local storage object by key."""
        StudioPlatformService.require_permission(db, user, None, "asset.read")
        normalized = file_path.replace("\\", "/").lstrip("/")
        asset = (
            db.query(StudioAsset)
            .filter(
                StudioAsset.is_deleted.is_(False),
                or_(StudioAsset.r2_key == normalized, StudioAsset.url.endswith(normalized)),
            )
            .first()
        )
        if not asset:
            raise NotFoundError("Asset file")
        if asset.project_id:
            StudioPlatformService.require_permission(db, user, asset.project_id, "asset.read")
        elif asset.uploaded_by_id != user.id and not user.is_admin:
            raise ForbiddenError("Asset access denied")

    @staticmethod
    def list_assets(
        db: Session,
        user: User,
        *,
        folder: str | None = None,
        search: str | None = None,
        tags: list[str] | None = None,
        collection_id: int | None = None,
        favorites_only: bool = False,
        include_deleted: bool = False,
        limit: int = 60,
        offset: int = 0,
    ) -> dict:
        StudioPlatformService.require_permission(db, user, None, "asset.read")
        q = (
            db.query(StudioAsset, User, AssetCollection)
            .outerjoin(User, User.id == StudioAsset.uploaded_by_id)
            .outerjoin(AssetCollection, AssetCollection.id == StudioAsset.collection_id)
        )
        if include_deleted:
            q = q.filter(StudioAsset.is_deleted.is_(True))
        else:
            q = q.filter(StudioAsset.is_deleted.is_(False))
        if folder and folder != "all":
            q = q.filter(StudioAsset.folder == folder)
        if collection_id:
            q = q.filter(StudioAsset.collection_id == collection_id)
        if favorites_only:
            q = q.filter(StudioAsset.is_favorite.is_(True))
        if search:
            like = f"%{search}%"
            q = q.filter(
                or_(
                    StudioAsset.filename.ilike(like),
                    StudioAsset.title.ilike(like),
                )
            )
        if tags:
            for tag in tags:
                q = q.filter(StudioAsset.tags.contains([tag]))
        total = q.count()
        rows = q.order_by(StudioAsset.created_at.desc()).offset(offset).limit(limit).all()
        folder_counts = {f: 0 for f in ASSET_FOLDERS}
        count_rows = (
            db.query(StudioAsset.folder, func.count(StudioAsset.id))
            .filter(StudioAsset.is_deleted.is_(False))
            .group_by(StudioAsset.folder)
            .all()
        )
        for f, c in count_rows:
            folder_counts[f] = c
        return {
            "items": [AssetLibraryService._asset_dict(a, u, c) for a, u, c in rows],
            "total": total,
            "folder_counts": folder_counts,
        }

    @staticmethod
    def _create_version_snapshot(db: Session, asset: StudioAsset, user_id: int) -> AssetVersion:
        snap = AssetVersion(
            asset_id=asset.id,
            version=asset.version,
            filename=asset.filename,
            r2_key=asset.r2_key,
            url=asset.url,
            size_bytes=asset.size_bytes,
            mime_type=asset.mime_type,
            meta=asset.meta,
            created_by_id=user_id,
        )
        db.add(snap)
        return snap

    @staticmethod
    def upload_asset(
        db: Session,
        user: User,
        meta: AssetUploadMetadata,
        file_data: bytes | None = None,
    ) -> StudioAsset:
        StudioPlatformService.require_permission(db, user, meta.project_id, "asset.upload")
        folder = meta.folder if meta.folder in ASSET_FOLDERS else AssetLibraryService._guess_folder(meta.mime_type, meta.filename)
        mime = meta.mime_type or mimetypes.guess_type(meta.filename)[0]
        asset_type = _FOLDER_TO_TYPE.get(folder, AssetType.DOCUMENT)

        if file_data:
            key = LocalStorageProvider.make_key(folder, meta.filename)
            result = upload_bytes(key, file_data, mime, meta.provider)
            url = result.url
            r2_key = result.key
            size = result.size_bytes
            provider = result.provider
        else:
            r2_key = f"studio/assets/{folder}/{uuid.uuid4().hex}_{meta.filename}"
            url = meta.url
            size = len(file_data) if file_data else 0
            provider = meta.provider or resolve_storage_provider().id

        asset = StudioAsset(
            project_id=meta.project_id,
            title=meta.title or meta.filename,
            filename=meta.filename,
            asset_type=asset_type,
            folder=folder,
            r2_key=r2_key,
            url=url,
            preview_url=url if mime and mime.startswith("image/") else None,
            size_bytes=size,
            mime_type=mime,
            tags=meta.tags,
            collection_id=meta.collection_id,
            cloud_provider=provider,
            uploaded_by_id=user.id,
            version=1,
        )
        db.add(asset)
        db.flush()
        AssetLibraryService._create_version_snapshot(db, asset, user.id)
        StudioPlatformService.log_activity(db, user.id, "asset.uploaded", meta.project_id, "asset", asset.id)
        db.commit()
        db.refresh(asset)
        return asset

    @staticmethod
    def update_asset(db: Session, user: User, asset_id: int, data: AssetUpdate) -> StudioAsset:
        asset = db.query(StudioAsset).filter(StudioAsset.id == asset_id).first()
        if not asset:
            raise NotFoundError("Asset")
        StudioPlatformService.require_permission(db, user, asset.project_id, "asset.upload")
        payload = data.model_dump(exclude_unset=True)
        if "folder" in payload and payload["folder"] in ASSET_FOLDERS:
            asset.asset_type = _FOLDER_TO_TYPE.get(payload["folder"], asset.asset_type)
        for key, value in payload.items():
            setattr(asset, key, value)
        asset.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(asset)
        return asset

    @staticmethod
    def toggle_favorite(db: Session, user: User, asset_id: int) -> StudioAsset:
        asset = db.query(StudioAsset).filter(StudioAsset.id == asset_id).first()
        if not asset:
            raise NotFoundError("Asset")
        StudioPlatformService.require_permission(db, user, asset.project_id, "asset.upload")
        asset.is_favorite = not asset.is_favorite
        db.commit()
        db.refresh(asset)
        return asset

    @staticmethod
    def soft_delete(db: Session, user: User, asset_id: int) -> None:
        asset = db.query(StudioAsset).filter(StudioAsset.id == asset_id).first()
        if not asset:
            raise NotFoundError("Asset")
        StudioPlatformService.require_permission(db, user, asset.project_id, "asset.manage")
        asset.is_deleted = True
        asset.deleted_at = datetime.now(timezone.utc)
        AssetLibraryService._create_version_snapshot(db, asset, user.id)
        db.commit()

    @staticmethod
    def restore_asset(db: Session, user: User, asset_id: int) -> StudioAsset:
        asset = db.query(StudioAsset).filter(StudioAsset.id == asset_id).first()
        if not asset:
            raise NotFoundError("Asset")
        StudioPlatformService.require_permission(db, user, asset.project_id, "asset.manage")
        asset.is_deleted = False
        asset.deleted_at = None
        db.commit()
        db.refresh(asset)
        return asset

    @staticmethod
    def list_versions(db: Session, user: User, asset_id: int) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "asset.read")
        rows = (
            db.query(AssetVersion, User)
            .outerjoin(User, User.id == AssetVersion.created_by_id)
            .filter(AssetVersion.asset_id == asset_id)
            .order_by(AssetVersion.version.desc())
            .all()
        )
        return [
            {
                "id": v.id,
                "asset_id": v.asset_id,
                "version": v.version,
                "filename": v.filename,
                "url": v.url,
                "size_bytes": v.size_bytes,
                "mime_type": v.mime_type,
                "created_by_id": v.created_by_id,
                "author_name": u.full_name if u else None,
                "created_at": v.created_at,
            }
            for v, u in rows
        ]

    @staticmethod
    def restore_version(db: Session, user: User, asset_id: int, version_id: int) -> StudioAsset:
        asset = db.query(StudioAsset).filter(StudioAsset.id == asset_id).first()
        if not asset:
            raise NotFoundError("Asset")
        StudioPlatformService.require_permission(db, user, asset.project_id, "asset.manage")
        version = db.query(AssetVersion).filter(AssetVersion.id == version_id, AssetVersion.asset_id == asset_id).first()
        if not version:
            raise NotFoundError("Version")
        AssetLibraryService._create_version_snapshot(db, asset, user.id)
        asset.filename = version.filename
        asset.r2_key = version.r2_key
        asset.url = version.url
        asset.size_bytes = version.size_bytes
        asset.mime_type = version.mime_type
        asset.version = (asset.version or 0) + 1
        asset.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(asset)
        return asset

    @staticmethod
    def list_collections(db: Session, user: User) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "asset.read")
        rows = db.query(AssetCollection).order_by(AssetCollection.name).all()
        result = []
        for col in rows:
            count = db.query(func.count(StudioAsset.id)).filter(
                StudioAsset.collection_id == col.id, StudioAsset.is_deleted.is_(False)
            ).scalar() or 0
            result.append({
                "id": col.id,
                "name": col.name,
                "description": col.description,
                "project_id": col.project_id,
                "color": col.color,
                "asset_count": count,
                "created_at": col.created_at,
            })
        return result

    @staticmethod
    def create_collection(db: Session, user: User, data: CollectionCreate) -> AssetCollection:
        StudioPlatformService.require_permission(db, user, data.project_id, "asset.upload")
        col = AssetCollection(
            name=data.name,
            description=data.description,
            project_id=data.project_id,
            color=data.color,
            created_by_id=user.id,
        )
        db.add(col)
        db.commit()
        db.refresh(col)
        return col

    @staticmethod
    def list_permissions(db: Session, user: User, asset_id: int) -> list[AssetPermission]:
        StudioPlatformService.require_permission(db, user, None, "asset.read")
        return db.query(AssetPermission).filter(AssetPermission.asset_id == asset_id).all()

    @staticmethod
    def add_permission(db: Session, user: User, asset_id: int, data: AssetPermissionCreate) -> AssetPermission:
        asset = db.query(StudioAsset).filter(StudioAsset.id == asset_id).first()
        if not asset:
            raise NotFoundError("Asset")
        StudioPlatformService.require_permission(db, user, asset.project_id, "asset.manage")
        perm = AssetPermission(
            asset_id=asset_id,
            user_id=data.user_id,
            role=data.role,
            permission=data.permission,
        )
        db.add(perm)
        db.commit()
        db.refresh(perm)
        return perm

    @staticmethod
    def seed_demo_assets(db: Session) -> None:
        if db.query(StudioAsset).count() > 0:
            return
        demos = [
            ("hero-poster.jpg", "images", AssetType.IMAGE, "https://picsum.photos/800/450?random=1", ["hero", "poster"]),
            ("drone-footage.mp4", "videos", AssetType.VIDEO, None, ["b-roll", "drone"]),
            ("narration-take.wav", "audio", AssetType.AUDIO, None, ["voice"]),
            ("script-final.pdf", "documents", AssetType.DOCUMENT, None, ["script"]),
            ("thumb-v1.jpg", "thumbnails", AssetType.THUMBNAIL, "https://picsum.photos/400/225?random=2", ["youtube"]),
            ("netflix-poster.jpg", "posters", AssetType.POSTER, "https://picsum.photos/600/900?random=3", ["key-art"]),
        ]
        for filename, folder, atype, url, tags in demos:
            db.add(
                StudioAsset(
                    filename=filename,
                    title=filename,
                    folder=folder,
                    asset_type=atype,
                    r2_key=f"demo/{folder}/{filename}",
                    url=url,
                    preview_url=url,
                    size_bytes=1024 * 512,
                    mime_type=mimetypes.guess_type(filename)[0],
                    tags=tags,
                    cloud_provider="local",
                )
            )
        db.commit()
