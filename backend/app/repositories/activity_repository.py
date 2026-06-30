"""Studio activity log persistence."""

from __future__ import annotations

from app.models import User
from app.models.studio import StudioActivityLog
from app.repositories.base import SqlAlchemyRepository


class ActivityRepository(SqlAlchemyRepository[StudioActivityLog]):
    model = StudioActivityLog

    def log(
        self,
        user_id: int,
        action: str,
        *,
        project_id: int | None = None,
        entity_type: str | None = None,
        entity_id: int | None = None,
        metadata: dict | None = None,
    ) -> StudioActivityLog:
        entry = StudioActivityLog(
            user_id=user_id,
            project_id=project_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            meta=metadata,
        )
        self.db.add(entry)
        return entry

    def recent(self, limit: int = 12) -> list[StudioActivityLog]:
        return (
            self.db.query(StudioActivityLog)
            .order_by(StudioActivityLog.created_at.desc())
            .limit(limit)
            .all()
        )

    def project_timeline(self, project_id: int, limit: int = 50) -> list[tuple[StudioActivityLog, User]]:
        return (
            self.db.query(StudioActivityLog, User)
            .join(User, User.id == StudioActivityLog.user_id)
            .filter(StudioActivityLog.project_id == project_id)
            .order_by(StudioActivityLog.created_at.desc())
            .limit(limit)
            .all()
        )
