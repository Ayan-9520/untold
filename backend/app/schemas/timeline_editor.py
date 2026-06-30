"""Timeline Editor Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase

TRACK_TYPES = ("video", "audio", "image", "text", "transition", "caption")
EXPORT_FORMATS = ("mp4", "webm", "mov", "mp3", "wav")


class TimelineClipSchema(BaseModel):
    id: str
    type: str
    start: float = 0
    duration: float = 5
    trim_in: float = Field(0, alias="trimIn")
    trim_out: float | None = Field(None, alias="trimOut")
    label: str = ""
    asset_url: str | None = Field(None, alias="assetUrl")
    color: str | None = None
    transition_in: dict | None = Field(None, alias="transitionIn")
    transition_out: dict | None = Field(None, alias="transitionOut")
    caption: str | None = None
    waveform_peaks: list[float] | None = Field(None, alias="waveformPeaks")

    model_config = {"populate_by_name": True}


class TimelineTrackSchema(BaseModel):
    id: str
    type: str
    name: str
    muted: bool = False
    locked: bool = False
    clips: list[dict] = Field(default_factory=list)


class TimelineDocumentSchema(BaseModel):
    duration: float = 180
    fps: int = 30
    tracks: list[dict] = Field(default_factory=list)
    settings: dict = Field(default_factory=lambda: {"zoom": 80, "snapEnabled": True})


class TimelineWorkspaceResponse(BaseModel):
    project_id: int
    project_title: str
    document: dict
    playhead: float
    zoom: float
    version: int
    last_auto_saved_at: datetime | None
    track_count: int
    clip_count: int
    duration: float


class TimelineSaveRequest(BaseModel):
    document: dict
    playhead: float | None = None
    zoom: float | None = None
    autosave: bool = True


class TimelineSaveResponse(BaseModel):
    version: int
    last_auto_saved_at: datetime | None


class TimelineSnapshotResponse(ORMBase):
    id: int
    version: int
    label: str | None
    created_at: datetime


class TimelineExportCreate(BaseModel):
    format: str = "mp4"
    resolution: str | None = "1080p"


class TimelineExportResponse(ORMBase):
    id: int
    project_id: int
    format: str
    status: str
    progress: int
    output_url: str | None
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None
