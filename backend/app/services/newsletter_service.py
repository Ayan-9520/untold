"""Newsletter subscription."""

from sqlalchemy.orm import Session

from app.models.auth_tokens import NewsletterSubscriber
from app.services.email_service import EmailService


class NewsletterService:
    @staticmethod
    def subscribe(db: Session, email: str, *, source: str = "website") -> NewsletterSubscriber:
        normalized = email.strip().lower()
        existing = db.query(NewsletterSubscriber).filter(NewsletterSubscriber.email == normalized).first()
        if existing:
            return existing

        row = NewsletterSubscriber(email=normalized, source=source)
        db.add(row)
        db.commit()
        db.refresh(row)

        EmailService.send_email(
            to=normalized,
            subject="Welcome to UNTOLD",
            body="You're on the list. We'll send you new documentaries, drops, and exclusive stories.",
        )
        return row

    @staticmethod
    def unsubscribe(db: Session, email: str) -> None:
        normalized = email.strip().lower()
        row = db.query(NewsletterSubscriber).filter(NewsletterSubscriber.email == normalized).first()
        if row:
            db.delete(row)
            db.commit()
