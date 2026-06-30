"""Studio activity logging and notifications."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.studio import StudioNotification
from app.repositories.activity_repository import ActivityRepository
from app.repositories.notification_repository import NotificationRepository


class StudioActivityService:
    @staticmethod
    def log_activity(
        db: Session,
        user_id: int,
        action: str,
        project_id: int | None = None,
        entity_type: str | None = None,
        entity_id: int | None = None,
        metadata: dict | None = None,
    ) -> None:
        ActivityRepository(db).log(
            user_id,
            action,
            project_id=project_id,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata=metadata,
        )

    @staticmethod
    def notify(
        db: Session,
        user_id: int,
        notification_type: str,
        title: str,
        body: str | None = None,
        data: dict | None = None,
    ) -> StudioNotification:
        return NotificationRepository(db).create(user_id, notification_type, title, body, data)
