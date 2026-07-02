"""Contact form submissions."""

from sqlalchemy.orm import Session

from app.models.auth_tokens import ContactMessage
from app.services.email_service import EmailService


class ContactService:
    @staticmethod
    def submit(db: Session, *, name: str, email: str, subject: str, message: str) -> ContactMessage:
        row = ContactMessage(name=name.strip(), email=email.strip().lower(), subject=subject.strip(), message=message.strip())
        db.add(row)
        db.commit()
        db.refresh(row)

        EmailService.send_email(
            to=email,
            subject="We received your message — UNTOLD",
            body=f"Hi {name},\n\nThank you for contacting UNTOLD. We'll respond to your inquiry about \"{subject}\" soon.\n",
        )
        return row
