"""Magazine monetization — tiered access and secure downloads."""

from sqlalchemy.orm import Session

from app.core.access import check_magazine_access
from app.core.exceptions import ForbiddenError, NotFoundError
from app.models import User
from app.models.monetization import MagazineDownload, MagazineEdition
from app.services.streaming_service import StreamingService


class MagazineMonetizationService:
    @staticmethod
    def get_magazine(db: Session, issue_slug: str) -> MagazineEdition:
        magazine = db.query(MagazineEdition).filter(MagazineEdition.issue_slug == issue_slug).first()
        if not magazine:
            raise NotFoundError("Magazine issue")
        return magazine

    @staticmethod
    def create_download(
        db: Session,
        user: User,
        issue_slug: str,
        ip_address: str | None = None,
    ) -> dict:
        magazine = MagazineMonetizationService.get_magazine(db, issue_slug)

        if not check_magazine_access(db, user, magazine):
            raise ForbiddenError("Subscription upgrade required for this magazine issue")

        url, expires_in = StreamingService.get_magazine_download_url(
            magazine.pdf_storage_key,
            f"/api/v1/magazine/issues/{issue_slug}/pdf",
        )

        record = MagazineDownload(
            user_id=user.id,
            magazine_id=magazine.id,
            download_url=url,
            ip_address=ip_address,
        )
        db.add(record)
        db.commit()

        return {
            "download_url": url,
            "expires_in": expires_in,
            "magazine_id": magazine.id,
            "title": magazine.title,
        }
