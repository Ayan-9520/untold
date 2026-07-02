from datetime import datetime

from pydantic import BaseModel, Field


class ViewerProfileResponse(BaseModel):
    id: int
    name: str
    avatar: str
    is_kids: bool
    is_primary: bool
    requires_pin: bool = False


class ViewerProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    avatar: str = Field(default="🎬", max_length=20)
    is_kids: bool = False
    pin: str | None = Field(default=None, min_length=4, max_length=6)


class ViewerPinVerify(BaseModel):
    pin: str


class UserPreferencesResponse(BaseModel):
    autoplay_next: bool = True
    default_quality: str = "auto"
    subtitle_language: str = "en"
    email_live_reminders: bool = True


class UserPreferencesUpdate(BaseModel):
    autoplay_next: bool | None = None
    default_quality: str | None = None
    subtitle_language: str | None = None
    email_live_reminders: bool | None = None


class LiveReminderResponse(BaseModel):
    id: int
    match_id: str
    match_title: str
    starts_at: datetime | None = None


class LiveReminderCreate(BaseModel):
    match_id: str
    match_title: str
    starts_at: datetime | None = None
