"""Project membership persistence."""

from __future__ import annotations

from app.models.studio import StudioProjectMember
from app.repositories.base import SqlAlchemyRepository


class MemberRepository(SqlAlchemyRepository[StudioProjectMember]):
    model = StudioProjectMember

    def get_member(self, project_id: int, user_id: int) -> StudioProjectMember | None:
        return (
            self.db.query(StudioProjectMember)
            .filter(
                StudioProjectMember.project_id == project_id,
                StudioProjectMember.user_id == user_id,
            )
            .first()
        )
