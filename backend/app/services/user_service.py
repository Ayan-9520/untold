from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import get_password_hash, verify_password
from app.models import User
from app.schemas.auth import PasswordChangeRequest, UserUpdateRequest


class UserService:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("User")
        return user

    @staticmethod
    def update_profile(db: Session, user: User, data: UserUpdateRequest) -> User:
        if data.email and data.email.lower() != user.email:
            existing = db.query(User).filter(User.email == data.email.lower()).first()
            if existing:
                raise ConflictError("Email already in use")
            user.email = data.email.lower()

        if data.full_name:
            user.full_name = data.full_name

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def change_password(db: Session, user: User, data: PasswordChangeRequest) -> None:
        if not verify_password(data.current_password, user.hashed_password):
            raise ConflictError("Current password is incorrect")
        user.hashed_password = get_password_hash(data.new_password)
        db.commit()

    @staticmethod
    def list_users(db: Session, skip: int = 0, limit: int = 50) -> tuple[list[User], int]:
        query = db.query(User)
        total = query.count()
        users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
        return users, total

    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> User:
        user = UserService.get_by_id(db, user_id)
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user
