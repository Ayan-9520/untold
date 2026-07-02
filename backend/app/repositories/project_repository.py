"""Production (project) persistence."""

from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import User
from app.models.studio import ProjectComment, StudioAsset, StudioProjectMember
from app.models.studio.core import Production
from app.repositories.base import SqlAlchemyRepository


class ProjectRepository(SqlAlchemyRepository[Production]):
    model = Production

    def get_by_id(self, project_id: int) -> Production | None:
        return self.db.query(Production).filter(Production.id == project_id).first()

    def get_by_slug(self, slug: str) -> Production | None:
        return self.db.query(Production).filter(Production.slug == slug).first()

    def list_for_user(
        self,
        user: User,
        *,
        limit: int = 50,
        offset: int = 0,
        stage: str | None = None,
        status: str | None = None,
        organization_id: int | None = None,
        workspace_id: int | None = None,
    ) -> tuple[list[Production], int]:
        q = self.db.query(Production)
        if organization_id is not None:
            q = q.filter(Production.organization_id == organization_id)
        if workspace_id is not None:
            q = q.filter(Production.workspace_id == workspace_id)
        if not user.is_admin:
            q = q.join(StudioProjectMember).filter(StudioProjectMember.user_id == user.id)
        if stage:
            q = q.filter(Production.stage == stage)
        if status:
            q = q.filter(Production.status == status)
        total = q.count()
        items = q.order_by(Production.updated_at.desc()).offset(offset).limit(limit).all()
        return items, total

    def batch_comment_counts(self, project_ids: list[int]) -> dict[int, int]:
        if not project_ids:
            return {}
        rows = (
            self.db.query(ProjectComment.project_id, func.count(ProjectComment.id))
            .filter(ProjectComment.project_id.in_(project_ids))
            .group_by(ProjectComment.project_id)
            .all()
        )
        return {pid: int(count) for pid, count in rows}

    def batch_attachment_counts(self, project_ids: list[int]) -> dict[int, int]:
        if not project_ids:
            return {}
        rows = (
            self.db.query(StudioAsset.project_id, func.count(StudioAsset.id))
            .filter(StudioAsset.project_id.in_(project_ids))
            .group_by(StudioAsset.project_id)
            .all()
        )
        return {pid: int(count) for pid, count in rows}

    def batch_members_with_users(self, project_ids: list[int]) -> dict[int, list[tuple[StudioProjectMember, User]]]:
        if not project_ids:
            return {}
        rows = (
            self.db.query(StudioProjectMember, User)
            .join(User, User.id == StudioProjectMember.user_id)
            .filter(StudioProjectMember.project_id.in_(project_ids))
            .all()
        )
        grouped: dict[int, list[tuple[StudioProjectMember, User]]] = {pid: [] for pid in project_ids}
        for member, user in rows:
            grouped.setdefault(member.project_id, []).append((member, user))
        return grouped

    def list_due_between(self, user: User, from_dt, to_dt) -> list[Production]:
        q = self.db.query(Production)
        if not user.is_admin:
            q = q.join(StudioProjectMember).filter(StudioProjectMember.user_id == user.id)
        return (
            q.filter(
                Production.due_date.isnot(None),
                Production.due_date >= from_dt,
                Production.due_date <= to_dt,
            )
            .order_by(Production.due_date.asc())
            .all()
        )

    def count_active(self) -> int:
        return self.db.query(func.count(Production.id)).filter(Production.status == "active").scalar() or 0

    def count_by_stage(self) -> list[tuple[str, int]]:
        return (
            self.db.query(Production.stage, func.count(Production.id))
            .filter(Production.status == "active")
            .group_by(Production.stage)
            .all()
        )

    def count_by_status(self) -> list[tuple[str, int]]:
        return self.db.query(Production.status, func.count(Production.id)).group_by(Production.status).all()

    def comment_count(self, project_id: int) -> int:
        return self.db.query(func.count(ProjectComment.id)).filter(ProjectComment.project_id == project_id).scalar() or 0

    def attachment_count(self, project_id: int) -> int:
        return self.db.query(func.count(StudioAsset.id)).filter(StudioAsset.project_id == project_id).scalar() or 0

    def members_with_users(self, project_id: int) -> list[tuple[StudioProjectMember, User]]:
        return (
            self.db.query(StudioProjectMember, User)
            .join(User, User.id == StudioProjectMember.user_id)
            .filter(StudioProjectMember.project_id == project_id)
            .all()
        )
