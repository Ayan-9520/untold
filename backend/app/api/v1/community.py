from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_optional_user
from app.db.session import get_db
from app.models import User
from app.services.community_service import CommunityService

router = APIRouter(prefix="/community", tags=["Fan Community"])


class FanWarVoteRequest(BaseModel):
    war_id: str
    side: str


class PredictionRequest(BaseModel):
    event_id: str
    answers: dict[str, Any]


@router.get("/fan-dna")
def get_fan_dna(user: User | None = Depends(get_optional_user)):
    return CommunityService.get_fan_dna(user.id if user else None)


@router.get("/debates")
def get_debates(db: Session = Depends(get_db)):
    return {"items": CommunityService.get_debates(db)}


@router.get("/fan-wars")
def get_fan_wars(db: Session = Depends(get_db)):
    return {"items": CommunityService.get_fan_wars(db)}


@router.post("/fan-wars/vote")
def vote_fan_war(
    data: FanWarVoteRequest,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    return CommunityService.vote_fan_war(db, data.war_id, data.side, user.id if user else None)


@router.get("/predictions")
def get_predictions(db: Session = Depends(get_db)):
    return CommunityService.get_predictions(db)


@router.post("/predictions")
def submit_prediction(
    data: PredictionRequest,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    return CommunityService.submit_prediction(db, user.id if user else None, data.event_id, data.answers)


@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db), user: User | None = Depends(get_optional_user)):
    return {"items": CommunityService.get_leaderboard(db, user.id if user else None)}
