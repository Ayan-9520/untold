"""Newsletter subscription API."""

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.middleware.rate_limit import limiter
from app.schemas.common import MessageResponse
from app.services.newsletter_service import NewsletterService

router = APIRouter(prefix="/newsletter", tags=["Newsletter"])


class NewsletterSubscribeRequest(BaseModel):
    email: EmailStr


@router.post("/subscribe", response_model=MessageResponse, status_code=201)
@limiter.limit("10/minute")
def subscribe_newsletter(
    request: Request,
    response: Response,
    data: NewsletterSubscribeRequest,
    db: Session = Depends(get_db),
):
    NewsletterService.subscribe(db, data.email)
    return MessageResponse(message="You're on the list. Welcome to UNTOLD.")
