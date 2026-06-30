"""Studio notification persistence."""

from __future__ import annotations

from app.models.studio import StudioNotification
from app.repositories.base import SqlAlchemyRepository


class NotificationRepository(SqlAlchemyRepository[StudioNotification]):
    model = StudioNotification

    def create(
        self,
        user_id: int,
        notification_type: str,
        title: str,
        body: str | None = None,
        data: dict | None = None,
    ) -> StudioNotification:
        note = StudioNotification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            body=body,
            data=data,
        )
        self.db.add(note)
        return note

    def list_for_user(self, user_id: int, limit: int = 50) -> list[StudioNotification]:
        return (
            self.db.query(StudioNotification)
            .filter(StudioNotification.user_id == user_id)
            .order_by(StudioNotification.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_for_user(self, user_id: int, notification_id: int) -> StudioNotification | None:
        return (
            self.db.query(StudioNotification)
            .filter(
                StudioNotification.id == notification_id,
                StudioNotification.user_id == user_id,
            )
            .first()
        )
