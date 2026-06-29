from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase
from app.schemas.video import VideoResponse


class WatchlistCreateRequest(BaseModel):
    video_id: int = Field(gt=0)


class WatchlistResponse(ORMBase):
    id: int
    user_id: int
    video_id: int
    added_at: datetime
    video: VideoResponse | None = None


class WatchlistToggleResponse(BaseModel):
    message: str
    in_watchlist: bool
    item: WatchlistResponse | None = None
