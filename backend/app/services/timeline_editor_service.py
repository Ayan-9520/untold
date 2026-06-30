"""Timeline Editor — document persistence, autosave, export queue."""

from __future__ import annotations

import copy
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import User
from app.models.studio import Production
from app.models.studio_platform import TimelineExportJob, TimelineSession, TimelineSnapshot
from app.schemas.timeline_editor import TimelineExportCreate, TimelineSaveRequest
from app.services.studio_platform_service import StudioPlatformService

TRACK_TYPES = ("video", "audio", "image", "text", "transition", "caption")

_CLIP_COLORS = {
    "video": "#3b82f6",
    "audio": "#22c55e",
    "image": "#a855f7",
    "text": "#f59e0b",
    "transition": "#ec4899",
    "caption": "#06b6d4",
}


def _uid() -> str:
    return uuid.uuid4().hex[:12]


def _demo_waveform(length: int = 64) -> list[float]:
    import math
    return [abs(math.sin(i * 0.35)) * 0.4 + 0.15 + (i % 7) * 0.02 for i in range(length)]


class TimelineEditorService:
    @staticmethod
    def _default_document() -> dict:
        tracks = []
        for ttype, name, clips in [
            ("video", "Video 1", [
                {"label": "Opening montage", "start": 0, "duration": 18, "trimIn": 0, "trimOut": 18},
                {"label": "Interview A-roll", "start": 20, "duration": 32, "trimIn": 2, "trimOut": 34},
            ]),
            ("audio", "Narration", [
                {"label": "Voice-over track", "start": 0, "duration": 52, "waveformPeaks": _demo_waveform()},
            ]),
            ("audio", "Music bed", [
                {"label": "Ambient score", "start": 5, "duration": 45, "waveformPeaks": _demo_waveform(48)},
            ]),
            ("image", "B-roll stills", [
                {"label": "Stadium wide", "start": 8, "duration": 6},
                {"label": "Archive photo", "start": 28, "duration": 5},
            ]),
            ("text", "Lower thirds", [
                {"label": "Name title", "start": 22, "duration": 4, "caption": "Captain · 2011"},
            ]),
            ("transition", "Transitions", [
                {"label": "Crossfade", "start": 17.5, "duration": 1, "transitionIn": {"type": "crossfade", "duration": 0.5}},
                {"label": "Dip to black", "start": 50, "duration": 0.8, "transitionIn": {"type": "dip", "duration": 0.8}},
            ]),
            ("caption", "Captions", [
                {"label": "EN subs", "start": 0, "duration": 55, "caption": "The story behind the glory…"},
            ]),
        ]:
            track_clips = []
            for c in clips:
                track_clips.append({
                    "id": _uid(),
                    "type": ttype,
                    "start": c["start"],
                    "duration": c["duration"],
                    "trimIn": c.get("trimIn", 0),
                    "trimOut": c.get("trimOut", c["duration"]),
                    "label": c["label"],
                    "assetUrl": c.get("assetUrl"),
                    "color": _CLIP_COLORS.get(ttype),
                    "transitionIn": c.get("transitionIn"),
                    "transitionOut": c.get("transitionOut"),
                    "caption": c.get("caption"),
                    "waveformPeaks": c.get("waveformPeaks"),
                })
            tracks.append({
                "id": _uid(),
                "type": ttype,
                "name": name,
                "muted": False,
                "locked": False,
                "clips": track_clips,
            })
        return {
            "duration": 120,
            "fps": 30,
            "tracks": tracks,
            "settings": {"zoom": 80, "snapEnabled": True},
        }

    @staticmethod
    def _counts(document: dict) -> tuple[int, int, float]:
        tracks = document.get("tracks") or []
        clip_count = sum(len(t.get("clips") or []) for t in tracks)
        duration = float(document.get("duration") or 120)
        return len(tracks), clip_count, duration

    @staticmethod
    def _get_or_create_session(db: Session, project_id: int) -> TimelineSession:
        session = db.query(TimelineSession).filter(TimelineSession.project_id == project_id).first()
        if session:
            return session
        session = TimelineSession(
            project_id=project_id,
            document=TimelineEditorService._default_document(),
            playhead=0,
            zoom=80,
            version=1,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_workspace(db: Session, user: User, project_id: int) -> dict:
        StudioPlatformService.require_permission(db, user, project_id, "timeline.edit")
        project = db.query(Production).filter(Production.id == project_id).first()
        if not project:
            raise NotFoundError("Project")
        session = TimelineEditorService._get_or_create_session(db, project_id)
        track_count, clip_count, duration = TimelineEditorService._counts(session.document)
        return {
            "project_id": project_id,
            "project_title": project.title,
            "document": session.document,
            "playhead": session.playhead,
            "zoom": session.zoom,
            "version": session.version,
            "last_auto_saved_at": session.last_auto_saved_at,
            "track_count": track_count,
            "clip_count": clip_count,
            "duration": duration,
        }

    @staticmethod
    def save_timeline(db: Session, user: User, project_id: int, data: TimelineSaveRequest) -> dict:
        StudioPlatformService.require_permission(db, user, project_id, "timeline.edit")
        session = TimelineEditorService._get_or_create_session(db, project_id)
        session.document = data.document
        if data.playhead is not None:
            session.playhead = data.playhead
        if data.zoom is not None:
            session.zoom = data.zoom
        session.version += 1
        now = datetime.now(timezone.utc)
        if data.autosave:
            session.last_auto_saved_at = now
        session.updated_at = now
        db.commit()
        db.refresh(session)
        return {"version": session.version, "last_auto_saved_at": session.last_auto_saved_at}

    @staticmethod
    def create_snapshot(db: Session, user: User, project_id: int, label: str | None = None) -> TimelineSnapshot:
        StudioPlatformService.require_permission(db, user, project_id, "timeline.edit")
        session = TimelineEditorService._get_or_create_session(db, project_id)
        snap = TimelineSnapshot(
            session_id=session.id,
            version=session.version,
            label=label or f"Snapshot v{session.version}",
            document=copy.deepcopy(session.document),
            created_by_id=user.id,
        )
        db.add(snap)
        db.commit()
        db.refresh(snap)
        return snap

    @staticmethod
    def list_snapshots(db: Session, user: User, project_id: int) -> list[TimelineSnapshot]:
        StudioPlatformService.require_permission(db, user, project_id, "timeline.edit")
        session = db.query(TimelineSession).filter(TimelineSession.project_id == project_id).first()
        if not session:
            return []
        return (
            db.query(TimelineSnapshot)
            .filter(TimelineSnapshot.session_id == session.id)
            .order_by(TimelineSnapshot.created_at.desc())
            .limit(20)
            .all()
        )

    @staticmethod
    def _export_dict(job: TimelineExportJob) -> dict:
        return {
            "id": job.id,
            "project_id": job.project_id,
            "format": job.format,
            "status": job.status,
            "progress": job.progress,
            "output_url": job.output_url,
            "error_message": job.error_message,
            "created_at": job.created_at,
            "completed_at": job.completed_at,
        }

    @staticmethod
    def list_exports(db: Session, user: User, project_id: int) -> list[dict]:
        StudioPlatformService.require_permission(db, user, project_id, "timeline.export")
        jobs = (
            db.query(TimelineExportJob)
            .filter(TimelineExportJob.project_id == project_id)
            .order_by(TimelineExportJob.created_at.desc())
            .limit(30)
            .all()
        )
        return [TimelineEditorService._export_dict(j) for j in jobs]

    @staticmethod
    def create_export(db: Session, user: User, project_id: int, data: TimelineExportCreate) -> dict:
        StudioPlatformService.require_permission(db, user, project_id, "timeline.export")
        project = db.query(Production).filter(Production.id == project_id).first()
        if not project:
            raise NotFoundError("Project")
        TimelineEditorService._get_or_create_session(db, project_id)
        job = TimelineExportJob(
            project_id=project_id,
            format=data.format,
            status="processing",
            progress=0,
            created_by_id=user.id,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        # Demo: complete export immediately
        job.status = "completed"
        job.progress = 100
        job.output_url = f"/api/v1/studio/platform/timeline/exports/{job.id}/demo.{data.format}"
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(job)
        return TimelineEditorService._export_dict(job)
