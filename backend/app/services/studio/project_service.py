"""Studio project aggregate — CRUD, members, comments, attachments."""

from __future__ import annotations

import re
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.domain.gateway.events import emit_gateway_event
from app.domain.studio.enums import AssetType, PublishingStatus, StudioRole
from app.domain.studio.permissions import StudioPermissionService
from app.models import User, Video
from app.models.studio import ProjectComment, StudioAsset, StudioProjectMember
from app.models.studio.core import Production
from app.repositories.member_repository import MemberRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.studio_platform import (
    ProjectAttachmentCreate,
    ProjectCommentCreate,
    ProjectCreate,
    ProjectMemberAssign,
    ProjectMemberUpdate,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.studio.activity_service import StudioActivityService


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:200] or "project"


class StudioProjectService:
    @staticmethod
    def to_response(
        db: Session,
        project: Production,
        *,
        comment_count: int | None = None,
        attachment_count: int | None = None,
        members: list[dict] | None = None,
    ) -> ProjectResponse:
        repo = ProjectRepository(db)
        if members is None:
            members = [
                {
                    "user_id": m.user_id,
                    "full_name": u.full_name,
                    "email": u.email,
                    "role": m.role.value if hasattr(m.role, "value") else m.role,
                }
                for m, u in repo.members_with_users(project.id)
            ]
        return ProjectResponse(
            id=project.id,
            slug=project.slug,
            title=project.title,
            description=project.description,
            category=project.category,
            language=project.language,
            tags=project.tags,
            stage=project.stage,
            status=project.status,
            publishing_status=project.publishing_status.value
            if hasattr(project.publishing_status, "value")
            else str(project.publishing_status),
            assignee=project.assignee,
            owner_id=project.owner_id,
            organization_id=project.organization_id,
            workspace_id=project.workspace_id,
            sources_count=project.sources_count,
            version=project.version,
            video_id=project.video_id,
            seo_title=project.seo_title,
            seo_description=project.seo_description,
            seo_keywords=project.seo_keywords,
            due_date=project.due_date,
            created_at=project.created_at,
            updated_at=project.updated_at,
            comment_count=comment_count if comment_count is not None else repo.comment_count(project.id),
            attachment_count=attachment_count if attachment_count is not None else repo.attachment_count(project.id),
            members=members,
        )

    @staticmethod
    def list_projects(
        db: Session,
        user: User,
        limit: int = 50,
        offset: int = 0,
        stage: str | None = None,
        status: str | None = None,
        organization_id: int | None = None,
        workspace_id: int | None = None,
    ) -> tuple[list[ProjectResponse], int]:
        repo = ProjectRepository(db)
        items, total = repo.list_for_user(
            user,
            limit=limit,
            offset=offset,
            stage=stage,
            status=status,
            organization_id=organization_id,
            workspace_id=workspace_id,
        )
        if not items:
            return [], total

        project_ids = [p.id for p in items]
        comment_counts = repo.batch_comment_counts(project_ids)
        attachment_counts = repo.batch_attachment_counts(project_ids)
        members_map = repo.batch_members_with_users(project_ids)

        responses = []
        for project in items:
            members = [
                {
                    "user_id": m.user_id,
                    "full_name": u.full_name,
                    "email": u.email,
                    "role": m.role.value if hasattr(m.role, "value") else m.role,
                }
                for m, u in members_map.get(project.id, [])
            ]
            responses.append(
                StudioProjectService.to_response(
                    db,
                    project,
                    comment_count=comment_counts.get(project.id, 0),
                    attachment_count=attachment_counts.get(project.id, 0),
                    members=members,
                )
            )
        return responses, total

    @staticmethod
    def get_project(db: Session, user: User, project_id: int) -> ProjectResponse:
        project = ProjectRepository(db).get_by_id(project_id)
        if not project:
            raise NotFoundError("Project")
        StudioPermissionService.require_permission(db, user, project_id, "project.read")
        return StudioProjectService.to_response(db, project)

    @staticmethod
    def create_project(
        db: Session,
        user: User,
        data: ProjectCreate,
        *,
        organization_id: int | None = None,
        workspace_id: int | None = None,
    ) -> ProjectResponse:
        from app.domain.tenancy.context import TenantContextService
        from app.services.tenancy_service import TenancyService

        StudioPermissionService.require_permission(db, user, None, "project.create")

        if organization_id is None:
            organization_id = TenantContextService.resolve_primary_org_id(db, user.id)
        if organization_id is None:
            raise ForbiddenError("Organization context required to create projects")

        TenancyService.enforce_project_limit(db, organization_id)

        if workspace_id is None:
            workspace_id = data.workspace_id or TenancyService.default_workspace_id(db, organization_id)

        repo = ProjectRepository(db)
        slug = data.slug or _slugify(data.title)
        if repo.get_by_slug(slug):
            slug = f"{slug}-{int(datetime.now(timezone.utc).timestamp())}"
        project = Production(
            slug=slug,
            title=data.title,
            description=data.description,
            category=data.category,
            language=data.language,
            tags=data.tags,
            stage=data.stage,
            status="active",
            assignee=data.assignee or user.full_name,
            owner_id=user.id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            publishing_status=PublishingStatus.UNPUBLISHED,
            due_date=data.due_date,
        )
        repo.add(project)
        repo.flush()
        repo.add(StudioProjectMember(project_id=project.id, user_id=user.id, role=StudioRole.PRODUCER))
        StudioActivityService.log_activity(db, user.id, "project.created", project.id, "project", project.id)
        repo.commit()
        repo.refresh(project)
        emit_gateway_event(
            "project.created",
            {"id": project.id, "title": project.title, "slug": project.slug, "stage": project.stage},
            user_id=user.id,
        )
        return StudioProjectService.to_response(db, project)

    @staticmethod
    def update_project(db: Session, user: User, project_id: int, data: ProjectUpdate) -> ProjectResponse:
        repo = ProjectRepository(db)
        project = repo.get_by_id(project_id)
        if not project:
            raise NotFoundError("Project")
        StudioPermissionService.require_permission(db, user, project_id, "project.update")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(project, field, value)
        StudioActivityService.log_activity(db, user.id, "project.updated", project_id, "project", project_id)
        repo.commit()
        repo.refresh(project)
        emit_gateway_event(
            "project.updated",
            {"id": project.id, "title": project.title, "stage": project.stage},
            user_id=user.id,
        )
        return StudioProjectService.to_response(db, project)

    @staticmethod
    def publish_to_originals(db: Session, user: User, project_id: int) -> ProjectResponse:
        repo = ProjectRepository(db)
        project = repo.get_by_id(project_id)
        if not project:
            raise NotFoundError("Project")
        StudioPermissionService.require_permission(db, user, project_id, "publish.schedule")
        if project.video_id:
            video = db.query(Video).filter(Video.id == project.video_id).first()
            if video:
                video.is_active = True
                video.title = project.seo_title or project.title
                video.description = project.seo_description or project.description
        else:
            video = Video(
                title=project.seo_title or project.title,
                slug=project.slug,
                description=project.seo_description or project.description,
                is_featured=False,
                is_trending=False,
                is_active=True,
            )
            db.add(video)
            db.flush()
            project.video_id = video.id
        project.publishing_status = PublishingStatus.PUBLISHED
        project.stage = "publishing"
        StudioActivityService.log_activity(db, user.id, "project.published", project_id, "video", project.video_id)
        StudioActivityService.notify(db, user.id, "publish", f"Published: {project.title}", "Live on UNTOLD Originals")
        repo.commit()
        repo.refresh(project)
        emit_gateway_event(
            "video.published",
            {"id": project.video_id, "project_id": project.id, "title": project.title},
        )
        emit_gateway_event(
            "project.completed",
            {"id": project.id, "title": project.title, "video_id": project.video_id, "stage": project.stage},
            user_id=user.id,
        )
        return StudioProjectService.to_response(db, project)

    @staticmethod
    def delete_project(db: Session, user: User, project_id: int) -> None:
        repo = ProjectRepository(db)
        project = repo.get_by_id(project_id)
        if not project:
            raise NotFoundError("Project")
        StudioPermissionService.require_permission(db, user, project_id, "project.delete")
        StudioActivityService.log_activity(db, user.id, "project.deleted", project_id, "project", project_id)
        repo.delete(project)
        repo.commit()

    @staticmethod
    def assign_member(db: Session, user: User, project_id: int, data: ProjectMemberAssign) -> ProjectResponse:
        repo = ProjectRepository(db)
        if not repo.get_by_id(project_id):
            raise NotFoundError("Project")
        StudioPermissionService.require_permission(db, user, project_id, "team.manage")
        target = db.query(User).filter(User.id == data.user_id).first()
        if not target:
            raise NotFoundError("User")
        members = MemberRepository(db)
        existing = members.get_member(project_id, data.user_id)
        if existing:
            existing.role = data.role
        else:
            members.add(StudioProjectMember(project_id=project_id, user_id=data.user_id, role=data.role))
        StudioActivityService.log_activity(db, user.id, "team.member_assigned", project_id, "member", data.user_id)
        db.commit()
        return StudioProjectService.get_project(db, user, project_id)

    @staticmethod
    def update_member(
        db: Session, user: User, project_id: int, member_user_id: int, data: ProjectMemberUpdate
    ) -> ProjectResponse:
        StudioPermissionService.require_permission(db, user, project_id, "team.manage")
        member = MemberRepository(db).get_member(project_id, member_user_id)
        if not member:
            raise NotFoundError("Team member")
        member.role = data.role
        db.commit()
        return StudioProjectService.get_project(db, user, project_id)

    @staticmethod
    def remove_member(db: Session, user: User, project_id: int, member_user_id: int) -> ProjectResponse:
        StudioPermissionService.require_permission(db, user, project_id, "team.manage")
        members = MemberRepository(db)
        member = members.get_member(project_id, member_user_id)
        if not member:
            raise NotFoundError("Team member")
        project = ProjectRepository(db).get_by_id(project_id)
        if project and project.owner_id == member_user_id:
            raise ForbiddenError("Cannot remove project owner")
        members.delete(member)
        StudioActivityService.log_activity(db, user.id, "team.member_removed", project_id, "member", member_user_id)
        db.commit()
        return StudioProjectService.get_project(db, user, project_id)

    @staticmethod
    def list_comments(db: Session, user: User, project_id: int, limit: int = 50):
        StudioPermissionService.require_permission(db, user, project_id, "project.read")
        rows = (
            db.query(ProjectComment, User)
            .join(User, User.id == ProjectComment.user_id)
            .filter(ProjectComment.project_id == project_id)
            .order_by(ProjectComment.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": c.id,
                "project_id": c.project_id,
                "user_id": c.user_id,
                "author_name": u.full_name,
                "content": c.content,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
            }
            for c, u in rows
        ]

    @staticmethod
    def add_comment(db: Session, user: User, project_id: int, data: ProjectCommentCreate):
        StudioPermissionService.require_permission(db, user, project_id, "project.update")
        comment = ProjectComment(project_id=project_id, user_id=user.id, content=data.content)
        db.add(comment)
        db.flush()
        StudioActivityService.log_activity(db, user.id, "comment.added", project_id, "comment", comment.id)
        db.commit()
        db.refresh(comment)
        return {
            "id": comment.id,
            "project_id": comment.project_id,
            "user_id": comment.user_id,
            "author_name": user.full_name,
            "content": comment.content,
            "created_at": comment.created_at,
            "updated_at": comment.updated_at,
        }

    @staticmethod
    def delete_comment(db: Session, user: User, project_id: int, comment_id: int) -> None:
        comment = (
            db.query(ProjectComment)
            .filter(ProjectComment.id == comment_id, ProjectComment.project_id == project_id)
            .first()
        )
        if not comment:
            raise NotFoundError("Comment")
        if comment.user_id != user.id and not user.is_admin:
            StudioPermissionService.require_permission(db, user, project_id, "project.update")
        db.delete(comment)
        db.commit()

    @staticmethod
    def list_attachments(db: Session, user: User, project_id: int):
        StudioPermissionService.require_permission(db, user, project_id, "project.read")
        return (
            db.query(StudioAsset)
            .filter(StudioAsset.project_id == project_id)
            .order_by(StudioAsset.created_at.desc())
            .all()
        )

    @staticmethod
    def add_attachment(db: Session, user: User, project_id: int, data: ProjectAttachmentCreate):
        StudioPermissionService.require_permission(db, user, project_id, "project.update")
        try:
            asset_type = AssetType(data.asset_type)
        except ValueError:
            asset_type = AssetType.DOCUMENT
        asset = StudioAsset(
            project_id=project_id,
            filename=data.filename,
            r2_key=f"studio/projects/{project_id}/{data.filename}",
            url=data.url,
            asset_type=asset_type,
            size_bytes=data.size_bytes,
            mime_type=data.mime_type,
            uploaded_by_id=user.id,
        )
        db.add(asset)
        db.flush()
        StudioActivityService.log_activity(db, user.id, "attachment.added", project_id, "asset", asset.id)
        db.commit()
        db.refresh(asset)
        return asset

    @staticmethod
    def delete_attachment(db: Session, user: User, project_id: int, attachment_id: int) -> None:
        StudioPermissionService.require_permission(db, user, project_id, "project.update")
        asset = (
            db.query(StudioAsset)
            .filter(StudioAsset.id == attachment_id, StudioAsset.project_id == project_id)
            .first()
        )
        if not asset:
            raise NotFoundError("Attachment")
        db.delete(asset)
        db.commit()

    @staticmethod
    def get_timeline(db: Session, user: User, project_id: int, limit: int = 50):
        from app.repositories.activity_repository import ActivityRepository

        StudioPermissionService.require_permission(db, user, project_id, "project.read")
        rows = ActivityRepository(db).project_timeline(project_id, limit)
        return [
            {
                "id": log.id,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "user_name": u.full_name,
                "created_at": log.created_at,
            }
            for log, u in rows
        ]
