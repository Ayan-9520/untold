"""Contact form API."""

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.middleware.rate_limit import limiter
from app.schemas.common import MessageResponse
from app.services.contact_service import ContactService

router = APIRouter(prefix="/contact", tags=["Contact"])


class ContactSubmitRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    subject: str = Field(min_length=2, max_length=500)
    message: str = Field(min_length=10, max_length=5000)


@router.post("", response_model=MessageResponse, status_code=201)
@limiter.limit("5/minute")
def submit_contact(
    request: Request,
    response: Response,
    data: ContactSubmitRequest,
    db: Session = Depends(get_db),
):
    ContactService.submit(db, name=data.name, email=data.email, subject=data.subject, message=data.message)
    return MessageResponse(message="Thank you for reaching out. We'll be in touch soon.")
