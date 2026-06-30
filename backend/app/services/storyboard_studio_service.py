"""Storyboard Studio — scenes, script import, reorder, revisions."""

from __future__ import annotations

import html
import re
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.domain.studio.enums import ApprovalStatus
from app.models import User
from app.models.studio import Production
from app.models.studio_platform import Script, ScriptVersion, StoryboardRevision, StoryboardScene, StudioApproval
from app.schemas.storyboard_studio import (
    StoryboardApprovalRequest,
    StoryboardImportRequest,
    StoryboardRevisionSave,
    StoryboardSceneCreate,
    StoryboardSceneUpdate,
)
from app.services.studio_platform_service import StudioPlatformService


class StoryboardStudioService:
    @staticmethod
    def _scene_dict(scene: StoryboardScene) -> dict:
        return {
            "id": scene.id,
            "project_id": scene.project_id,
            "scene_number": scene.scene_number,
            "sort_order": scene.sort_order,
            "duration_seconds": scene.duration_seconds,
            "narration": scene.narration,
            "dialogue": scene.dialogue,
            "camera_angle": scene.camera_angle,
            "camera_movement": scene.camera_movement,
            "shot_type": scene.shot_type,
            "visual_prompt": scene.visual_prompt,
            "environment": scene.environment,
            "lighting": scene.lighting,
            "mood": scene.mood,
            "transition": scene.transition,
            "reference_image_url": scene.reference_image_url,
            "status": scene.status,
            "created_at": scene.created_at,
            "updated_at": scene.updated_at,
        }

    @staticmethod
    def _snapshot_scenes(scenes: list[StoryboardScene]) -> list[dict]:
        return [
            {
                "scene_number": s.scene_number,
                "sort_order": s.sort_order,
                "duration_seconds": s.duration_seconds,
                "narration": s.narration,
                "dialogue": s.dialogue,
                "camera_angle": s.camera_angle,
                "camera_movement": s.camera_movement,
                "shot_type": s.shot_type,
                "visual_prompt": s.visual_prompt,
                "environment": s.environment,
                "lighting": s.lighting,
                "mood": s.mood,
                "transition": s.transition,
                "reference_image_url": s.reference_image_url,
                "status": s.status,
            }
            for s in scenes
        ]

    @staticmethod
    def _list_scenes(db: Session, project_id: int) -> list[StoryboardScene]:
        return (
            db.query(StoryboardScene)
            .filter(StoryboardScene.project_id == project_id)
            .order_by(StoryboardScene.sort_order.asc(), StoryboardScene.scene_number.asc())
            .all()
        )

    @staticmethod
    def _renumber_scenes(db: Session, project_id: int) -> None:
        scenes = StoryboardStudioService._list_scenes(db, project_id)
        for idx, scene in enumerate(scenes, start=1):
            scene.scene_number = idx
            scene.sort_order = idx

    @staticmethod
    def _create_revision(
        db: Session,
        user: User,
        project_id: int,
        label: str | None = None,
    ) -> StoryboardRevision:
        scenes = StoryboardStudioService._list_scenes(db, project_id)
        version = (
            db.query(func.max(StoryboardRevision.version))
            .filter(StoryboardRevision.project_id == project_id)
            .scalar()
            or 0
        ) + 1
        revision = StoryboardRevision(
            project_id=project_id,
            version=version,
            label=label,
            scenes_snapshot=StoryboardStudioService._snapshot_scenes(scenes),
            created_by_id=user.id,
        )
        db.add(revision)
        return revision

    @staticmethod
    def get_workspace(db: Session, user: User, project_id: int) -> dict:
        StudioPlatformService.require_permission(db, user, project_id, "project.read")
        project = db.query(Production).filter(Production.id == project_id).first()
        if not project:
            raise NotFoundError("Project")
        scenes = StoryboardStudioService._list_scenes(db, project_id)
        revisions = (
            db.query(StoryboardRevision, User)
            .join(User, User.id == StoryboardRevision.created_by_id)
            .filter(StoryboardRevision.project_id == project_id)
            .order_by(StoryboardRevision.version.desc())
            .limit(30)
            .all()
        )
        total_duration = sum(s.duration_seconds or 0 for s in scenes)
        script_content = StoryboardStudioService._get_script_content(db, project_id)
        approval = (
            db.query(StudioApproval)
            .filter(
                StudioApproval.entity_type == "storyboard",
                StudioApproval.entity_id == project_id,
            )
            .order_by(StudioApproval.created_at.desc())
            .first()
        )
        approval_status = "draft"
        if approval:
            st = approval.status.value if hasattr(approval.status, "value") else str(approval.status)
            approval_status = "pending" if st == "pending" else st

        from app.services.storyboard_agent_service import StoryboardAgentService

        ai_history = StoryboardAgentService.list_history(db, user, project_id, limit=20)
        providers = StoryboardAgentService.list_providers()

        return {
            "project_id": project_id,
            "project_title": project.title,
            "scene_count": len(scenes),
            "total_duration_seconds": total_duration,
            "has_script": bool(script_content.strip()),
            "approval_status": approval_status,
            "scenes": [StoryboardStudioService._scene_dict(s) for s in scenes],
            "revisions": [
                {
                    "id": r.id,
                    "project_id": r.project_id,
                    "version": r.version,
                    "label": r.label,
                    "scene_count": len(r.scenes_snapshot or []),
                    "created_by_id": r.created_by_id,
                    "author_name": u.full_name,
                    "created_at": r.created_at,
                }
                for r, u in revisions
            ],
            "ai_history": ai_history,
            "providers": providers,
            "approval": (
                {
                    "id": approval.id,
                    "status": approval.status.value if hasattr(approval.status, "value") else str(approval.status),
                    "notes": approval.notes,
                    "requested_by_id": approval.requested_by_id,
                    "approver_id": approval.approver_id,
                    "created_at": approval.created_at,
                    "resolved_at": approval.resolved_at,
                }
                if approval
                else None
            ),
        }

    @staticmethod
    def _strip_html(text: str) -> str:
        cleaned = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
        cleaned = re.sub(r"<[^>]+>", " ", cleaned)
        return html.unescape(re.sub(r"\s+", " ", cleaned)).strip()

    @staticmethod
    def _estimate_duration(text: str, default: int) -> int:
        words = len((text or "").split())
        if words == 0:
            return default
        return max(5, min(300, int(words / 2.5)))

    @staticmethod
    def _parse_script_content(content: str, default_duration: int) -> list[dict]:
        if not content or not content.strip():
            return []
        scenes: list[dict] = []
        pattern = re.compile(r"<h([23])[^>]*>(.*?)</h\1>(.*?)(?=<h[23]|$)", re.I | re.S)
        matches = list(pattern.finditer(content))
        if matches:
            for i, match in enumerate(matches, start=1):
                title = StoryboardStudioService._strip_html(match.group(2))
                body = StoryboardStudioService._strip_html(match.group(3))
                narration = body or title
                scenes.append(
                    {
                        "scene_number": i,
                        "sort_order": i,
                        "duration_seconds": StoryboardStudioService._estimate_duration(narration, default_duration),
                        "narration": narration,
                        "visual_prompt": title or f"Scene {i}",
                        "camera_angle": "Medium shot",
                        "camera_movement": "Static",
                        "lighting": "Natural",
                        "environment": "Documentary set",
                        "status": "draft",
                    }
                )
            return scenes

        blocks = [b.strip() for b in re.split(r"</p>|</div>", content, flags=re.I) if b.strip()]
        paragraphs = []
        for block in blocks:
            text = StoryboardStudioService._strip_html(block)
            if text and len(text) > 8:
                paragraphs.append(text)
        if not paragraphs:
            plain = StoryboardStudioService._strip_html(content)
            if plain:
                paragraphs = [p.strip() for p in re.split(r"\n{2,}", plain) if p.strip()]
        for i, para in enumerate(paragraphs, start=1):
            scenes.append(
                {
                    "scene_number": i,
                    "sort_order": i,
                    "duration_seconds": StoryboardStudioService._estimate_duration(para, default_duration),
                    "narration": para,
                    "visual_prompt": para[:120] + ("…" if len(para) > 120 else ""),
                    "camera_angle": "Wide shot",
                    "camera_movement": "Slow pan",
                    "lighting": "Soft key",
                    "environment": "Location",
                    "status": "draft",
                }
            )
        return scenes

    @staticmethod
    def _get_script_content(db: Session, project_id: int) -> str:
        script = (
            db.query(Script)
            .filter(Script.project_id == project_id)
            .order_by(Script.created_at.desc())
            .first()
        )
        if not script:
            return ""
        version = None
        if script.current_version_id:
            version = db.query(ScriptVersion).filter(ScriptVersion.id == script.current_version_id).first()
        if not version:
            version = (
                db.query(ScriptVersion)
                .filter(ScriptVersion.script_id == script.id)
                .order_by(ScriptVersion.version.desc())
                .first()
            )
        return version.content if version else ""

    @staticmethod
    def import_from_script(
        db: Session,
        user: User,
        project_id: int,
        data: StoryboardImportRequest,
    ) -> dict:
        StudioPlatformService.require_permission(db, user, project_id, "storyboard.edit")
        project = db.query(Production).filter(Production.id == project_id).first()
        if not project:
            raise NotFoundError("Project")
        existing = StoryboardStudioService._list_scenes(db, project_id)
        if existing and not data.replace_existing:
            StoryboardStudioService._create_revision(db, user, project_id, "Before script import")
        if data.replace_existing:
            if existing:
                StoryboardStudioService._create_revision(db, user, project_id, "Before replace import")
            for scene in existing:
                db.delete(scene)
            db.flush()

        content = StoryboardStudioService._get_script_content(db, project_id)
        parsed = StoryboardStudioService._parse_script_content(content, data.default_duration_seconds)
        if not parsed:
            parsed = [
                {
                    "scene_number": 1,
                    "sort_order": 1,
                    "duration_seconds": data.default_duration_seconds,
                    "narration": "No script content found. Add narration here.",
                    "visual_prompt": f"Opening — {project.title}",
                    "camera_angle": "Establishing wide",
                    "camera_movement": "Drone rise",
                    "lighting": "Golden hour",
                    "environment": "Exterior",
                    "status": "draft",
                }
            ]

        created: list[StoryboardScene] = []
        for item in parsed:
            scene = StoryboardScene(project_id=project_id, **item)
            db.add(scene)
            created.append(scene)
        db.flush()
        StoryboardStudioService._create_revision(db, user, project_id, "Imported from script")
        StudioPlatformService.log_activity(db, user.id, "storyboard.imported", project_id, "storyboard", project_id)
        db.commit()
        return StoryboardStudioService.get_workspace(db, user, project_id)

    @staticmethod
    def create_scene(db: Session, user: User, project_id: int, data: StoryboardSceneCreate) -> StoryboardScene:
        StudioPlatformService.require_permission(db, user, project_id, "storyboard.edit")
        scenes = StoryboardStudioService._list_scenes(db, project_id)
        next_num = (max((s.scene_number for s in scenes), default=0)) + 1
        scene = StoryboardScene(
            project_id=project_id,
            scene_number=data.scene_number or next_num,
            sort_order=data.scene_number or next_num,
            duration_seconds=data.duration_seconds,
            narration=data.narration,
            dialogue=data.dialogue,
            camera_angle=data.camera_angle,
            camera_movement=data.camera_movement,
            shot_type=data.shot_type,
            visual_prompt=data.visual_prompt,
            environment=data.environment,
            lighting=data.lighting,
            mood=data.mood,
            transition=data.transition,
            reference_image_url=data.reference_image_url,
            status=data.status,
        )
        db.add(scene)
        StoryboardStudioService._renumber_scenes(db, project_id)
        StoryboardStudioService._create_revision(db, user, project_id, f"Added scene {scene.scene_number}")
        db.commit()
        db.refresh(scene)
        return scene

    @staticmethod
    def update_scene(
        db: Session,
        user: User,
        project_id: int,
        scene_id: int,
        data: StoryboardSceneUpdate,
    ) -> StoryboardScene:
        StudioPlatformService.require_permission(db, user, project_id, "storyboard.edit")
        scene = (
            db.query(StoryboardScene)
            .filter(StoryboardScene.id == scene_id, StoryboardScene.project_id == project_id)
            .first()
        )
        if not scene:
            raise NotFoundError("Scene")
        payload = data.model_dump(exclude_unset=True)
        for key, value in payload.items():
            setattr(scene, key, value)
        scene.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(scene)
        return scene

    @staticmethod
    def delete_scene(db: Session, user: User, project_id: int, scene_id: int) -> None:
        StudioPlatformService.require_permission(db, user, project_id, "storyboard.edit")
        scene = (
            db.query(StoryboardScene)
            .filter(StoryboardScene.id == scene_id, StoryboardScene.project_id == project_id)
            .first()
        )
        if not scene:
            raise NotFoundError("Scene")
        StoryboardStudioService._create_revision(db, user, project_id, f"Before delete scene {scene.scene_number}")
        db.delete(scene)
        db.flush()
        StoryboardStudioService._renumber_scenes(db, project_id)
        db.commit()

    @staticmethod
    def reorder_scenes(db: Session, user: User, project_id: int, scene_ids: list[int]) -> dict:
        StudioPlatformService.require_permission(db, user, project_id, "storyboard.edit")
        scenes = {
            s.id: s
            for s in db.query(StoryboardScene).filter(StoryboardScene.project_id == project_id).all()
        }
        if set(scene_ids) != set(scenes.keys()):
            raise NotFoundError("Scene order mismatch")
        StoryboardStudioService._create_revision(db, user, project_id, "Before reorder")
        for idx, scene_id in enumerate(scene_ids, start=1):
            scene = scenes[scene_id]
            scene.sort_order = idx
            scene.scene_number = idx
            scene.updated_at = datetime.now(timezone.utc)
        StoryboardStudioService._create_revision(db, user, project_id, "Reordered scenes")
        StudioPlatformService.log_activity(db, user.id, "storyboard.reordered", project_id, "storyboard", project_id)
        db.commit()
        return StoryboardStudioService.get_workspace(db, user, project_id)

    @staticmethod
    def save_revision(db: Session, user: User, project_id: int, data: StoryboardRevisionSave | None = None) -> StoryboardRevision:
        StudioPlatformService.require_permission(db, user, project_id, "storyboard.edit")
        label = data.label if data else None
        revision = StoryboardStudioService._create_revision(db, user, project_id, label or "Manual save")
        StudioPlatformService.log_activity(db, user.id, "storyboard.revision_saved", project_id, "storyboard", revision.id)
        db.commit()
        db.refresh(revision)
        return revision

    @staticmethod
    def restore_revision(db: Session, user: User, project_id: int, revision_id: int) -> dict:
        StudioPlatformService.require_permission(db, user, project_id, "storyboard.edit")
        revision = (
            db.query(StoryboardRevision)
            .filter(StoryboardRevision.id == revision_id, StoryboardRevision.project_id == project_id)
            .first()
        )
        if not revision:
            raise NotFoundError("Revision")
        StoryboardStudioService._create_revision(db, user, project_id, f"Before restore v{revision.version}")
        existing = StoryboardStudioService._list_scenes(db, project_id)
        for scene in existing:
            db.delete(scene)
        db.flush()
        snapshot = revision.scenes_snapshot or []
        if isinstance(snapshot, dict):
            snapshot = snapshot.get("scenes", [])
        for item in snapshot:
            scene = StoryboardScene(
                project_id=project_id,
                scene_number=item.get("scene_number", 1),
                sort_order=item.get("sort_order", item.get("scene_number", 1)),
                duration_seconds=item.get("duration_seconds", 10),
                narration=item.get("narration"),
                dialogue=item.get("dialogue"),
                camera_angle=item.get("camera_angle"),
                camera_movement=item.get("camera_movement"),
                shot_type=item.get("shot_type"),
                visual_prompt=item.get("visual_prompt"),
                environment=item.get("environment"),
                lighting=item.get("lighting"),
                mood=item.get("mood"),
                transition=item.get("transition"),
                reference_image_url=item.get("reference_image_url"),
                status=item.get("status", "draft"),
            )
            db.add(scene)
        StoryboardStudioService._create_revision(db, user, project_id, f"Restored v{revision.version}")
        db.commit()
        return StoryboardStudioService.get_workspace(db, user, project_id)

    @staticmethod
    def request_approval(db: Session, user: User, project_id: int, data: StoryboardApprovalRequest) -> StudioApproval:
        StudioPlatformService.require_permission(db, user, project_id, "storyboard.edit")
        approval = StudioApproval(
            project_id=project_id,
            entity_type="storyboard",
            entity_id=project_id,
            requested_by_id=user.id,
            status=ApprovalStatus.PENDING,
            notes=data.notes,
        )
        db.add(approval)
        for scene in StoryboardStudioService._list_scenes(db, project_id):
            if scene.status == "draft":
                scene.status = "review"
        StudioPlatformService.log_activity(db, user.id, "storyboard.approval_requested", project_id, "storyboard", project_id)
        db.commit()
        db.refresh(approval)
        return approval

    @staticmethod
    def approve_storyboard(db: Session, user: User, project_id: int, data: StoryboardApprovalRequest | None = None) -> dict:
        StudioPlatformService.require_permission(db, user, project_id, "storyboard.approve")
        approval = (
            db.query(StudioApproval)
            .filter(
                StudioApproval.entity_type == "storyboard",
                StudioApproval.entity_id == project_id,
                StudioApproval.status == ApprovalStatus.PENDING,
            )
            .order_by(StudioApproval.created_at.desc())
            .first()
        )
        if approval:
            approval.status = ApprovalStatus.APPROVED
            approval.approver_id = user.id
            approval.resolved_at = datetime.now(timezone.utc)
            if data and data.notes:
                approval.notes = data.notes
        else:
            db.add(
                StudioApproval(
                    project_id=project_id,
                    entity_type="storyboard",
                    entity_id=project_id,
                    requested_by_id=user.id,
                    approver_id=user.id,
                    status=ApprovalStatus.APPROVED,
                    notes=data.notes if data else None,
                    resolved_at=datetime.now(timezone.utc),
                )
            )
        for scene in StoryboardStudioService._list_scenes(db, project_id):
            if scene.status in ("draft", "review"):
                scene.status = "approved"
        StudioPlatformService.log_activity(db, user.id, "storyboard.approved", project_id, "storyboard", project_id)
        db.commit()
        return StoryboardStudioService.get_workspace(db, user, project_id)

    @staticmethod
    def reject_storyboard(db: Session, user: User, project_id: int, data: StoryboardApprovalRequest | None = None) -> dict:
        StudioPlatformService.require_permission(db, user, project_id, "storyboard.approve")
        approval = (
            db.query(StudioApproval)
            .filter(
                StudioApproval.entity_type == "storyboard",
                StudioApproval.entity_id == project_id,
                StudioApproval.status == ApprovalStatus.PENDING,
            )
            .order_by(StudioApproval.created_at.desc())
            .first()
        )
        if approval:
            approval.status = ApprovalStatus.REJECTED
            approval.approver_id = user.id
            approval.resolved_at = datetime.now(timezone.utc)
            if data and data.notes:
                approval.notes = data.notes
        StudioPlatformService.log_activity(db, user.id, "storyboard.rejected", project_id, "storyboard", project_id)
        db.commit()
        return StoryboardStudioService.get_workspace(db, user, project_id)
