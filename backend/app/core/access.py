"""Premium access control — tier hierarchy and video/magazine gating."""

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, get_optional_user
from app.core.exceptions import ForbiddenError
from app.db.session import get_db
from app.models import Subscription, SubscriptionPlan, SubscriptionStatus, User, Video
from app.models.monetization import AccessTier, MagazineEdition, VideoAccessLog

TIER_RANK = {
    SubscriptionPlan.FREE: 0,
    SubscriptionPlan.PREMIUM: 1,
    SubscriptionPlan.VIP: 2,
    "free": 0,
    "premium": 1,
    "vip": 2,
}

ACCESS_TIER_RANK = {
    AccessTier.FREE: 0,
    AccessTier.PREMIUM: 1,
    AccessTier.VIP: 2,
    "free": 0,
    "premium": 1,
    "vip": 2,
}


def get_user_plan(db: Session, user: User | None) -> SubscriptionPlan:
    if not user:
        return SubscriptionPlan.FREE
    if user.is_admin:
        return SubscriptionPlan.VIP

    sub = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user.id,
            Subscription.status == SubscriptionStatus.ACTIVE,
        )
        .order_by(Subscription.created_at.desc())
        .first()
    )
    if not sub:
        return SubscriptionPlan.FREE
    return sub.plan


def tier_allows(user_tier: SubscriptionPlan, required: str) -> bool:
    user_rank = TIER_RANK.get(user_tier, 0)
    req_rank = ACCESS_TIER_RANK.get(required, 0)
    if isinstance(required, AccessTier):
        req_rank = ACCESS_TIER_RANK.get(required.value, 0)
    return user_rank >= req_rank


def check_video_access(db: Session, user: User | None, video: Video, request: Request | None = None) -> bool:
    required = getattr(video, "access_tier", "free") or "free"
    user_tier = get_user_plan(db, user)
    granted = tier_allows(user_tier, required)

    log = VideoAccessLog(
        user_id=user.id if user else None,
        video_id=video.id,
        access_granted=granted,
        access_tier_required=required,
        user_tier=user_tier.value,
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None,
    )
    db.add(log)
    db.commit()
    return granted


def require_video_access(db: Session, user: User | None, video: Video, request: Request | None = None) -> None:
    if not check_video_access(db, user, video, request):
        raise ForbiddenError("Premium subscription required to watch this content")


def check_magazine_access(db: Session, user: User | None, magazine: MagazineEdition) -> bool:
    user_tier = get_user_plan(db, user)
    return tier_allows(user_tier, magazine.access_tier.value)


def get_current_subscriber(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> tuple[User, SubscriptionPlan]:
    return current_user, get_user_plan(db, current_user)
