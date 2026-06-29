from datetime import datetime

from pydantic import BaseModel, Field

from app.models.live import LiveEventType, LiveProvider, LiveSport, MatchStatus
from app.schemas.common import ORMBase


class LiveScoreSchema(BaseModel):
    home: str | None = None
    away: str | None = None
    display: str | None = None


class LiveMatchResponse(BaseModel):
    id: str
    db_id: int
    event_name: str
    sport: str
    teams_or_players: list[str]
    score: LiveScoreSchema
    status: str
    timer: str | None = None
    thumbnail: str | None = None
    location: str | None = None
    league: str | None = None
    featured: bool = False
    provider: str | None = None


class LiveEventResponse(ORMBase):
    id: int
    match_id: int
    event_type: LiveEventType
    minute_or_over: str | None = None
    raw_text: str
    occurred_at: datetime | None = None


class LiveCommentaryResponse(ORMBase):
    id: int
    match_id: int
    event_id: int | None = None
    minute_or_over: str | None = None
    ai_text: str
    notification_text: str | None = None
    is_breaking: bool
    created_at: datetime


class MatchStatsResponse(BaseModel):
    match_id: int
    stats: dict


class LiveOverviewResponse(BaseModel):
    featured: LiveMatchResponse | None = None
    matches: list[LiveMatchResponse]
    total: int


class WebhookEventPayload(BaseModel):
    event: dict
    match_external_id: str | None = None


class CommentaryGenerateRequest(BaseModel):
    type: str = "default"
    raw: str = ""
    text: str = ""
    sport: str = "Football"
