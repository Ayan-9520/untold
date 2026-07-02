"""Sports events API — live matches as events."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.events_service import EventsService

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("")
def list_events(
    sport: str | None = Query(None),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return EventsService.overview(db, sport=sport, search=search)


@router.get("/featured")
def featured_event(db: Session = Depends(get_db)):
    featured = EventsService.get_featured(db)
    if not featured:
        raise HTTPException(status_code=404, detail="No featured event")
    return featured


@router.get("/{event_id}")
def get_event(event_id: str, db: Session = Depends(get_db)):
    event = EventsService.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
