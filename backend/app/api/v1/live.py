from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models import User
from app.schemas.live import (
    CommentaryGenerateRequest,
    LiveCommentaryResponse,
    LiveEventResponse,
    LiveMatchResponse,
    LiveOverviewResponse,
    MatchStatsResponse,
    WebhookEventPayload,
)
from app.services.live_provider_service import SUPPORTED_PROVIDERS
from app.services.live_service import LiveService
from app.services.live_sync_service import LiveSyncService

router = APIRouter(prefix="/live", tags=["Live"])


def _to_match_response(data: dict) -> LiveMatchResponse:
    return LiveMatchResponse(
        id=data["id"],
        db_id=data["db_id"],
        event_name=data.get("event_name") or data.get("eventName", ""),
        sport=data["sport"],
        teams_or_players=data.get("teams_or_players") or data.get("teamsOrPlayers", []),
        score=data.get("score", {}),
        status=data.get("status", "live"),
        timer=data.get("timer"),
        thumbnail=data.get("thumbnail"),
        location=data.get("location"),
        league=data.get("league"),
        featured=data.get("featured", False),
        provider=data.get("provider"),
    )


@router.get("", response_model=LiveOverviewResponse)
def get_live_overview(db: Session = Depends(get_db)):
    overview = LiveService.get_overview(db)
    return LiveOverviewResponse(
        featured=_to_match_response(overview["featured"]) if overview.get("featured") else None,
        matches=[_to_match_response(m) for m in overview["matches"]],
        total=overview["total"],
    )


@router.get("/featured", response_model=LiveMatchResponse)
def get_featured_match(db: Session = Depends(get_db)):
    match = LiveService.get_featured(db)
    if not match:
        raise HTTPException(status_code=404, detail="No live matches")
    return _to_match_response(match)


@router.get("/matches")
def list_live_matches(sport: str | None = Query(None), db: Session = Depends(get_db)):
    matches = LiveService.list_matches(db, sport)
    return {"items": matches, "total": len(matches)}


@router.get("/matches/{match_id}")
def get_live_match(match_id: str, db: Session = Depends(get_db)):
    try:
        return LiveService.get_match(db, match_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Match not found")


@router.get("/matches/{match_id}/events")
def get_match_events(match_id: str, db: Session = Depends(get_db)):
    try:
        events = LiveService.get_events(db, match_id)
        return {"items": events, "match_id": match_id}
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Match not found")


@router.get("/matches/{match_id}/commentary")
def get_match_commentary(match_id: str, db: Session = Depends(get_db)):
    try:
        commentary = LiveService.get_commentary(db, match_id)
        return {"items": commentary, "match_id": match_id}
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Match not found")


@router.get("/matches/{match_id}/stats", response_model=MatchStatsResponse)
def get_match_stats(match_id: str, db: Session = Depends(get_db)):
    try:
        return LiveService.get_stats(db, match_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Match not found")


@router.post("/commentary/generate")
def generate_commentary(data: CommentaryGenerateRequest, _: User = Depends(get_current_admin)):
    return {
        "commentary": LiveService.generate_commentary_preview(data.model_dump(), data.sport),
        "pipeline": "Sports API → AI Live Agent → UNTOLD",
    }


@router.post("/webhook/{provider}")
def sports_api_webhook(provider: str, payload: WebhookEventPayload, db: Session = Depends(get_db)):
    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unsupported provider. Use: {SUPPORTED_PROVIDERS}")
    return LiveSyncService.ingest_webhook(db, provider, payload.model_dump())


@router.post("/sync")
def trigger_live_sync(db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    from app.workers.tasks import sync_live_matches

    task = sync_live_matches.delay()
    return {"message": "Live sync queued", "task_id": task.id}
