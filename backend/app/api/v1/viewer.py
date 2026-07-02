"""Viewer profiles, preferences, live reminders."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user
from app.db.session import get_db
from app.models import User
from app.schemas.viewer import (
    LiveReminderCreate,
    LiveReminderResponse,
    UserPreferencesResponse,
    UserPreferencesUpdate,
    ViewerPinVerify,
    ViewerProfileCreate,
    ViewerProfileResponse,
)
from app.services.viewer_profile_service import LiveReminderService, ViewerProfileService

router = APIRouter(prefix="/viewer", tags=["Viewer Profiles"])


def _profile_response(p) -> ViewerProfileResponse:
    return ViewerProfileResponse(
        id=p.id,
        name=p.name,
        avatar=p.avatar,
        is_kids=p.is_kids,
        is_primary=p.is_primary,
        requires_pin=bool(p.pin_hash),
    )


@router.get("/profiles", response_model=list[ViewerProfileResponse])
def list_profiles(db: Session = Depends(get_db), user: User = Depends(get_current_active_user)):
    return [_profile_response(p) for p in ViewerProfileService.list_profiles(db, user)]


@router.post("/profiles", response_model=ViewerProfileResponse, status_code=201)
def create_profile(
    data: ViewerProfileCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    p = ViewerProfileService.create_profile(db, user, data.name, data.avatar, data.is_kids, data.pin)
    return _profile_response(p)


@router.post("/profiles/{profile_id}/verify-pin")
def verify_pin(
    profile_id: int,
    data: ViewerPinVerify,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    ok = ViewerProfileService.verify_pin(db, profile_id, user, data.pin)
    if not ok:
        from app.core.exceptions import UnauthorizedError

        raise UnauthorizedError("Invalid PIN")
    return {"verified": True}


@router.delete("/profiles/{profile_id}", status_code=204)
def delete_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    ViewerProfileService.delete_profile(db, user, profile_id)


@router.get("/preferences", response_model=UserPreferencesResponse)
def get_preferences(db: Session = Depends(get_db), user: User = Depends(get_current_active_user)):
    prefs = ViewerProfileService.get_preferences(db, user)
    return UserPreferencesResponse(**{**UserPreferencesResponse().model_dump(), **prefs})


@router.patch("/preferences", response_model=UserPreferencesResponse)
def update_preferences(
    data: UserPreferencesUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    prefs = ViewerProfileService.update_preferences(db, user, data.model_dump(exclude_none=True))
    return UserPreferencesResponse(**{**UserPreferencesResponse().model_dump(), **prefs})


@router.get("/reminders", response_model=list[LiveReminderResponse])
def list_reminders(db: Session = Depends(get_db), user: User = Depends(get_current_active_user)):
    rows = LiveReminderService.list_reminders(db, user)
    return [
        LiveReminderResponse(id=r.id, match_id=r.match_id, match_title=r.match_title, starts_at=r.starts_at)
        for r in rows
    ]


@router.post("/reminders", response_model=LiveReminderResponse, status_code=201)
def create_reminder(
    data: LiveReminderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    r = LiveReminderService.set_reminder(db, user, data.match_id, data.match_title, data.starts_at)
    return LiveReminderResponse(id=r.id, match_id=r.match_id, match_title=r.match_title, starts_at=r.starts_at)


@router.delete("/reminders/{match_id}", status_code=204)
def delete_reminder(
    match_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    LiveReminderService.remove_reminder(db, user, match_id)
