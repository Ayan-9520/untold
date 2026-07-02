"""Viewer profiles and user preferences."""

import json
from datetime import datetime

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError
from app.models import User
from app.models.viewer import LiveEventReminder, ViewerProfile

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MAX_PROFILES = 5
DEVICE_LIMITS = {"free": 1, "premium": 2, "vip": 4}


class ViewerProfileService:
    @staticmethod
    def ensure_primary(db: Session, user: User) -> ViewerProfile:
        primary = (
            db.query(ViewerProfile)
            .filter(ViewerProfile.user_id == user.id, ViewerProfile.is_primary.is_(True))
            .first()
        )
        if primary:
            return primary
        row = ViewerProfile(
            user_id=user.id,
            name=user.full_name.split()[0] if user.full_name else "Me",
            avatar="🎬",
            is_primary=True,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

    @staticmethod
    def list_profiles(db: Session, user: User) -> list[ViewerProfile]:
        rows = db.query(ViewerProfile).filter(ViewerProfile.user_id == user.id).order_by(ViewerProfile.id.asc()).all()
        if not rows:
            return [ViewerProfileService.ensure_primary(db, user)]
        return rows

    @staticmethod
    def create_profile(
        db: Session, user: User, name: str, avatar: str = "🎬", is_kids: bool = False, pin: str | None = None
    ) -> ViewerProfile:
        count = db.query(ViewerProfile).filter(ViewerProfile.user_id == user.id).count()
        if count >= MAX_PROFILES:
            raise BadRequestError(f"Maximum {MAX_PROFILES} profiles per account")
        pin_hash = pwd_context.hash(pin) if pin and is_kids else None
        row = ViewerProfile(user_id=user.id, name=name, avatar=avatar, is_kids=is_kids, pin_hash=pin_hash)
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

    @staticmethod
    def verify_pin(db: Session, profile_id: int, user: User, pin: str) -> bool:
        row = db.query(ViewerProfile).filter(ViewerProfile.id == profile_id, ViewerProfile.user_id == user.id).first()
        if not row or not row.pin_hash:
            return True
        return pwd_context.verify(pin, row.pin_hash)

    @staticmethod
    def delete_profile(db: Session, user: User, profile_id: int) -> None:
        row = db.query(ViewerProfile).filter(ViewerProfile.id == profile_id, ViewerProfile.user_id == user.id).first()
        if not row:
            raise NotFoundError("Profile")
        if row.is_primary:
            raise BadRequestError("Cannot delete primary profile")
        db.delete(row)
        db.commit()

    @staticmethod
    def get_preferences(db: Session, user: User) -> dict:
        try:
            return json.loads(user.preferences_json or "{}")
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def update_preferences(db: Session, user: User, prefs: dict) -> dict:
        current = ViewerProfileService.get_preferences(db, user)
        current.update(prefs)
        user.preferences_json = json.dumps(current)
        db.commit()
        return current


class LiveReminderService:
    @staticmethod
    def list_reminders(db: Session, user: User) -> list[LiveEventReminder]:
        return (
            db.query(LiveEventReminder)
            .filter(LiveEventReminder.user_id == user.id)
            .order_by(LiveEventReminder.created_at.desc())
            .all()
        )

    @staticmethod
    def set_reminder(
        db: Session, user: User, match_id: str, match_title: str, starts_at: datetime | None = None
    ) -> LiveEventReminder:
        row = (
            db.query(LiveEventReminder)
            .filter(LiveEventReminder.user_id == user.id, LiveEventReminder.match_id == match_id)
            .first()
        )
        if row:
            return row
        row = LiveEventReminder(
            user_id=user.id, match_id=match_id, match_title=match_title, starts_at=starts_at
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

    @staticmethod
    def remove_reminder(db: Session, user: User, match_id: str) -> None:
        row = (
            db.query(LiveEventReminder)
            .filter(LiveEventReminder.user_id == user.id, LiveEventReminder.match_id == match_id)
            .first()
        )
        if row:
            db.delete(row)
            db.commit()
