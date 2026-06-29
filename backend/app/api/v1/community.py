from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.deps import get_optional_user
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
def get_debates():
    return {"items": CommunityService.get_debates()}


@router.get("/fan-wars")
def get_fan_wars():
    return {"items": CommunityService.get_fan_wars()}


@router.post("/fan-wars/vote")
def vote_fan_war(data: FanWarVoteRequest, user: User | None = Depends(get_optional_user)):
    return CommunityService.vote_fan_war(data.war_id, data.side, user.id if user else None)


@router.get("/predictions")
def get_predictions():
    return CommunityService.get_predictions()


@router.post("/predictions")
def submit_prediction(data: PredictionRequest, user: User | None = Depends(get_optional_user)):
    return CommunityService.submit_prediction(user.id if user else None, data.event_id, data.answers)


@router.get("/leaderboard")
def get_leaderboard():
    return {"items": CommunityService.get_leaderboard()}
