"""AI Image Studio — generation queue, history, favorites, collections, versions."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.domain.image.providers.registry import get_image_registry
from app.domain.image.safety import validate_image_prompt
from app.domain.image.types import IMAGE_TYPES, ImageGenerateRequest
from app.domain.studio.enums import AIGenerationModule, AIGenerationStatus, AssetType
from app.models import User
from app.models.studio_platform import (
    AIGeneration,
    AIImageCollection,
    AIImageCollectionItem,
    AIImageVersion,
    AIPromptLibrary,
    StudioAsset,
    StudioNotification,
)
from app.schemas.image_studio import ImageCollectionCreate, ImageGenerateCreate
from app.services.generation_telemetry_service import apply_failure, finalize_generation_success
from app.services.studio_platform_service import StudioPlatformService

_IMAGE_MODULES = frozenset({AIGenerationModule.IMAGE, AIGenerationModule.THUMBNAIL})

_ASPECT_MAP = {
    "16:9": (1024, 576),
    "9:16": (576, 1024),
    "1:1": (768, 768),
    "4:5": (800, 1000),
}

_FOLDER_BY_TYPE = {
    "poster": "posters",
    "thumbnail": "thumbnails",
    "concept_art": "images",
    "environment": "images",
    "illustration": "images",
    "sports": "images",
    "background": "images",
}

_DEFAULT_IMAGE_PROMPTS = [
    {
        "title": "Documentary poster — hero athlete",
        "module": "image",
        "prompt_template": "Cinematic documentary poster for {topic}. Original composition, dramatic lighting, no copyrighted characters.",
        "description": "Original sports documentary poster concept.",
        "tags": ["poster", "sports"],
        "parameters": {"image_type": "poster"},
    },
    {
        "title": "YouTube thumbnail — high CTR",
        "module": "thumbnail",
        "prompt_template": "Bold YouTube thumbnail for {topic}. Strong focal subject, readable contrast, original artwork.",
        "description": "CTR-focused thumbnail layout.",
        "tags": ["thumbnail", "youtube"],
        "parameters": {"image_type": "thumbnail"},
    },
    {
        "title": "Stadium environment concept",
        "module": "image",
        "prompt_template": "Wide environment concept: historic stadium atmosphere for {topic}. Golden hour, crowd energy, original scene.",
        "description": "Environment design for B-roll planning.",
        "tags": ["environment"],
        "parameters": {"image_type": "environment"},
    },
    {
        "title": "Sports illustration — legacy moment",
        "module": "image",
        "prompt_template": "Editorial sports illustration capturing a defining legacy moment in {topic}. Stylized, respectful, original.",
        "description": "Illustrated key moment.",
        "tags": ["illustration", "sports"],
        "parameters": {"image_type": "sports"},
    },
]


class ImageStudioService:
    @staticmethod
    def _job_dict(gen: AIGeneration, author_name: str | None = None) -> dict:
        params = gen.parameters or {}
        return {
            "id": gen.id,
            "project_id": gen.project_id,
            "module": gen.module,
            "prompt": gen.prompt,
            "parameters": gen.parameters,
            "image_type": params.get("image_type", "illustration"),
            "action": params.get("action", "generate"),
            "provider": gen.provider or "demo",
            "status": gen.status,
            "output_text": gen.output_text,
            "output_meta": gen.output_meta,
            "result_url": gen.result_url,
            "r2_key": gen.r2_key,
            "error": gen.error,
            "is_favorite": gen.is_favorite,
            "parent_generation_id": gen.parent_generation_id,
            "retry_count": gen.retry_count or 0,
            "created_by_id": gen.created_by_id,
            "author_name": author_name,
            "created_at": gen.created_at,
            "started_at": gen.started_at,
            "completed_at": gen.completed_at,
            "cancelled_at": gen.cancelled_at,
        }

    @staticmethod
    def _image_query(db: Session):
        return (
            db.query(AIGeneration, User)
            .outerjoin(User, User.id == AIGeneration.created_by_id)
            .filter(AIGeneration.module.in_(list(_IMAGE_MODULES)))
            .order_by(AIGeneration.created_at.desc())
        )

    @staticmethod
    def get_overview(db: Session, user: User) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        ImageStudioService.seed_image_prompts(db)
        counts = ImageStudioService._status_counts(db)
        return {
            "image_types": [
                {"id": t, "label": t.replace("_", " ").title()} for t in IMAGE_TYPES
            ],
            "providers": get_image_registry().list_providers(),
            "queue_counts": counts,
        }

    @staticmethod
    def _status_counts(db: Session) -> dict[str, int]:
        rows = (
            db.query(AIGeneration.status, func.count(AIGeneration.id))
            .filter(AIGeneration.module.in_(list(_IMAGE_MODULES)))
            .group_by(AIGeneration.status)
            .all()
        )
        base = {s.value: 0 for s in AIGenerationStatus}
        for status, count in rows:
            key = status.value if hasattr(status, "value") else str(status)
            base[key] = count
        return base

    @staticmethod
    def _module_for_type(image_type: str) -> AIGenerationModule:
        return AIGenerationModule.THUMBNAIL if image_type == "thumbnail" else AIGenerationModule.IMAGE

    @staticmethod
    def create_generation(db: Session, user: User, data: ImageGenerateCreate) -> AIGeneration:
        if data.project_id:
            StudioPlatformService.require_permission(db, user, data.project_id, "ai.generate")
        else:
            StudioPlatformService.require_permission(db, user, None, "ai.generate")

        violation = validate_image_prompt(data.prompt)
        if violation:
            raise ConflictError(violation)

        image_type = data.image_type if data.image_type in IMAGE_TYPES else "illustration"
        action = data.action or "generate"
        params = {
            "image_type": image_type,
            "action": action,
            "aspect_ratio": data.aspect_ratio,
            **(data.parameters or {}),
        }

        gen = AIGeneration(
            project_id=data.project_id,
            module=ImageStudioService._module_for_type(image_type),
            prompt=data.prompt,
            parameters=params,
            provider=data.provider or get_image_registry().resolve().id,
            status=AIGenerationStatus.QUEUED,
            parent_generation_id=data.parent_generation_id,
            created_by_id=user.id,
        )
        db.add(gen)
        db.flush()

        from app.workers.studio_tasks import run_ai_generation

        task = run_ai_generation.delay(gen.id)
        gen.celery_task_id = task.id
        StudioPlatformService.log_activity(db, user.id, "image.job_queued", data.project_id, "ai_generation", gen.id)
        db.commit()
        db.refresh(gen)
        return gen

    @staticmethod
    def execute_image_job(db: Session, generation_id: int) -> None:
        gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
        if not gen or gen.status == AIGenerationStatus.CANCELLED:
            return

        violation = validate_image_prompt(gen.prompt)
        if violation:
            gen.status = AIGenerationStatus.FAILED
            gen.error = violation
            apply_failure(gen)
            db.commit()
            return

        gen.status = AIGenerationStatus.RUNNING
        gen.started_at = datetime.now(timezone.utc)
        db.commit()

        params = gen.parameters or {}
        image_type = params.get("image_type", "illustration")
        action = params.get("action", "generate")
        aspect = params.get("aspect_ratio", "16:9")
        width, height = _ASPECT_MAP.get(aspect, (1024, 576))

        source_url = None
        source_prompt = gen.prompt
        if gen.parent_generation_id:
            parent = db.query(AIGeneration).filter(AIGeneration.id == gen.parent_generation_id).first()
            if parent:
                source_url = parent.result_url
                source_prompt = parent.prompt

        try:
            result = get_image_registry().generate(
                ImageGenerateRequest(
                    prompt=gen.prompt,
                    image_type=image_type,
                    action=action,
                    aspect_ratio=aspect,
                    width=width,
                    height=height,
                    source_url=source_url,
                    source_prompt=source_prompt,
                    project_id=gen.project_id,
                ),
                provider_id=gen.provider,
            )
            gen.status = AIGenerationStatus.COMPLETED
            gen.completed_at = datetime.now(timezone.utc)
            gen.output_text = result.output_text
            gen.output_meta = result.meta
            gen.result_url = result.result_url
            gen.r2_key = result.r2_key
            gen.provider = result.provider
            finalize_generation_success(db, gen, started_at=gen.started_at, output_text=result.output_text, meta=result.meta)

            ImageStudioService._save_version(
                db, gen.id, gen.created_by_id, result.result_url, result.r2_key, result.meta,
                label=f"{action} v1",
            )

            if gen.created_by_id:
                db.add(
                    StudioNotification(
                        user_id=gen.created_by_id,
                        notification_type="image_job_complete",
                        title=f"Image ready — {image_type.replace('_', ' ')}",
                        body=gen.prompt[:120],
                        data={"generation_id": gen.id, "image_type": image_type, "result_url": gen.result_url},
                    )
                )
            db.commit()
        except Exception as exc:
            gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
            if gen and gen.status != AIGenerationStatus.CANCELLED:
                gen.status = AIGenerationStatus.FAILED
                gen.error = str(exc)
                apply_failure(gen, started_at=gen.started_at)
                db.commit()
            raise

    @staticmethod
    def _save_version(
        db: Session,
        generation_id: int,
        user_id: int | None,
        result_url: str | None,
        r2_key: str | None,
        meta: dict | None,
        label: str | None = None,
    ) -> AIImageVersion:
        latest = (
            db.query(func.max(AIImageVersion.version))
            .filter(AIImageVersion.generation_id == generation_id)
            .scalar()
            or 0
        )
        row = AIImageVersion(
            generation_id=generation_id,
            version=int(latest) + 1,
            label=label,
            result_url=result_url,
            r2_key=r2_key,
            output_meta=meta,
            created_by_id=user_id,
        )
        db.add(row)
        return row

    @staticmethod
    def get_queue(db: Session, user: User) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        q = ImageStudioService._image_query(db)
        queued = q.filter(AIGeneration.status == AIGenerationStatus.QUEUED).limit(50).all()
        running = q.filter(AIGeneration.status == AIGenerationStatus.RUNNING).limit(20).all()
        return {
            "queued": [ImageStudioService._job_dict(g, u.full_name if u else None) for g, u in queued],
            "running": [ImageStudioService._job_dict(g, u.full_name if u else None) for g, u in running],
            "counts": ImageStudioService._status_counts(db),
        }

    @staticmethod
    def get_history(db: Session, user: User, image_type: str | None = None, limit: int = 50, offset: int = 0) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        q = ImageStudioService._image_query(db)
        if image_type:
            q = q.filter(AIGeneration.parameters.contains({"image_type": image_type}))
        total = q.count()
        rows = q.offset(offset).limit(limit).all()
        return {
            "items": [ImageStudioService._job_dict(g, u.full_name if u else None) for g, u in rows],
            "total": total,
        }

    @staticmethod
    def get_favorites(db: Session, user: User, limit: int = 50) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        rows = (
            ImageStudioService._image_query(db)
            .filter(AIGeneration.is_favorite.is_(True))
            .limit(limit)
            .all()
        )
        return [ImageStudioService._job_dict(g, u.full_name if u else None) for g, u in rows]

    @staticmethod
    def toggle_favorite(db: Session, user: User, generation_id: int) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
        if not gen or gen.module not in _IMAGE_MODULES:
            raise NotFoundError("Image generation")
        gen.is_favorite = not gen.is_favorite
        db.commit()
        return {"id": gen.id, "is_favorite": gen.is_favorite}

    @staticmethod
    def list_collections(db: Session, user: User) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        rows = (
            db.query(AIImageCollection)
            .filter(AIImageCollection.created_by_id == user.id)
            .order_by(AIImageCollection.created_at.desc())
            .all()
        )
        if not rows:
            return []
        collection_ids = [c.id for c in rows]
        count_rows = (
            db.query(AIImageCollectionItem.collection_id, func.count(AIImageCollectionItem.id))
            .filter(AIImageCollectionItem.collection_id.in_(collection_ids))
            .group_by(AIImageCollectionItem.collection_id)
            .all()
        )
        counts = {cid: int(n) for cid, n in count_rows}
        return [
            {
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "project_id": c.project_id,
                "item_count": counts.get(c.id, 0),
                "created_at": c.created_at,
            }
            for c in rows
        ]

    @staticmethod
    def create_collection(db: Session, user: User, data: ImageCollectionCreate) -> AIImageCollection:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        col = AIImageCollection(
            name=data.name,
            description=data.description,
            project_id=data.project_id,
            created_by_id=user.id,
        )
        db.add(col)
        db.commit()
        db.refresh(col)
        return col

    @staticmethod
    def add_to_collection(db: Session, user: User, collection_id: int, generation_id: int) -> None:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        col = db.query(AIImageCollection).filter(
            AIImageCollection.id == collection_id,
            AIImageCollection.created_by_id == user.id,
        ).first()
        if not col:
            raise NotFoundError("Collection")
        gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
        if not gen:
            raise NotFoundError("Image generation")
        exists = (
            db.query(AIImageCollectionItem)
            .filter(
                AIImageCollectionItem.collection_id == collection_id,
                AIImageCollectionItem.generation_id == generation_id,
            )
            .first()
        )
        if exists:
            return
        db.add(AIImageCollectionItem(collection_id=collection_id, generation_id=generation_id))
        db.commit()

    @staticmethod
    def list_versions(db: Session, user: User, generation_id: int) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        rows = (
            db.query(AIImageVersion)
            .filter(AIImageVersion.generation_id == generation_id)
            .order_by(AIImageVersion.version.desc())
            .all()
        )
        return [
            {
                "id": v.id,
                "generation_id": v.generation_id,
                "version": v.version,
                "label": v.label,
                "result_url": v.result_url,
                "created_at": v.created_at,
            }
            for v in rows
        ]

    @staticmethod
    def upscale(db: Session, user: User, generation_id: int) -> AIGeneration:
        gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
        if not gen or gen.status != AIGenerationStatus.COMPLETED:
            raise ConflictError("Only completed images can be upscaled")
        return ImageStudioService.create_generation(
            db,
            user,
            ImageGenerateCreate(
                prompt=gen.prompt,
                image_type=(gen.parameters or {}).get("image_type", "illustration"),
                action="upscale",
                aspect_ratio=(gen.parameters or {}).get("aspect_ratio", "16:9"),
                project_id=gen.project_id,
                parent_generation_id=gen.id,
                provider=gen.provider,
            ),
        )

    @staticmethod
    def create_variation(db: Session, user: User, generation_id: int, prompt: str | None = None) -> AIGeneration:
        gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
        if not gen or gen.status != AIGenerationStatus.COMPLETED:
            raise ConflictError("Only completed images support variations")
        return ImageStudioService.create_generation(
            db,
            user,
            ImageGenerateCreate(
                prompt=prompt or gen.prompt,
                image_type=(gen.parameters or {}).get("image_type", "illustration"),
                action="variation",
                aspect_ratio=(gen.parameters or {}).get("aspect_ratio", "16:9"),
                project_id=gen.project_id,
                parent_generation_id=gen.id,
                provider=gen.provider,
            ),
        )

    @staticmethod
    def save_to_asset_library(db: Session, user: User, generation_id: int) -> dict:
        gen = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
        if not gen or not gen.r2_key:
            raise NotFoundError("Image generation")
        StudioPlatformService.require_permission(db, user, gen.project_id, "asset.upload")
        image_type = (gen.parameters or {}).get("image_type", "illustration")
        folder = _FOLDER_BY_TYPE.get(image_type, "images")
        asset_type = AssetType.POSTER if folder == "posters" else AssetType.THUMBNAIL if folder == "thumbnails" else AssetType.IMAGE
        asset = StudioAsset(
            project_id=gen.project_id,
            title=gen.prompt[:200],
            asset_type=asset_type,
            folder=folder,
            filename=gen.r2_key.rsplit("/", 1)[-1],
            r2_key=gen.r2_key,
            url=gen.result_url,
            preview_url=gen.result_url,
            size_bytes=(gen.output_meta or {}).get("size_bytes", 0),
            mime_type=(gen.output_meta or {}).get("mime_type", "image/svg+xml"),
            tags=["ai-generated", image_type],
            cloud_provider=gen.provider,
            meta={"generation_id": gen.id},
            uploaded_by_id=user.id,
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)
        return {"asset_id": asset.id, "url": asset.url, "folder": asset.folder}

    @staticmethod
    def seed_image_prompts(db: Session) -> None:
        for item in _DEFAULT_IMAGE_PROMPTS:
            exists = (
                db.query(AIPromptLibrary)
                .filter(AIPromptLibrary.title == item["title"], AIPromptLibrary.module == item["module"])
                .first()
            )
            if exists:
                continue
            db.add(
                AIPromptLibrary(
                    title=item["title"],
                    module=item["module"],
                    prompt_template=item["prompt_template"],
                    description=item.get("description"),
                    parameters=item.get("parameters"),
                    tags=item.get("tags", []),
                    is_public=True,
                )
            )
        db.commit()

    @staticmethod
    def list_prompts(db: Session, user: User, image_type: str | None = None) -> list[dict]:
        from app.services.ai_studio_service import AIStudioService

        ImageStudioService.seed_image_prompts(db)
        prompts = AIStudioService.list_prompts(db, user, None)
        filtered = [p for p in prompts if p["module"] in ("image", "thumbnail")]
        if image_type:
            filtered = [p for p in filtered if (p.get("parameters") or {}).get("image_type") == image_type]
        return filtered
