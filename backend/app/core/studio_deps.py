"""FastAPI dependencies for Studio repositories and domain services."""

from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.studio.permissions import StudioPermissionService
from app.repositories.activity_repository import ActivityRepository
from app.repositories.member_repository import MemberRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.project_repository import ProjectRepository


def get_project_repository(db: Session = Depends(get_db)) -> ProjectRepository:
    return ProjectRepository(db)


def get_member_repository(db: Session = Depends(get_db)) -> MemberRepository:
    return MemberRepository(db)


def get_activity_repository(db: Session = Depends(get_db)) -> ActivityRepository:
    return ActivityRepository(db)


def get_notification_repository(db: Session = Depends(get_db)) -> NotificationRepository:
    return NotificationRepository(db)


def get_studio_permissions() -> type[StudioPermissionService]:
    return StudioPermissionService
