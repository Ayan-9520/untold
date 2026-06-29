from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user
from app.db.session import get_db
from app.models import User
from app.schemas.auth import PasswordChangeRequest, UserResponse, UserUpdateRequest
from app.schemas.common import MessageResponse, PaginatedResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_profile(
    data: UserUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return UserService.update_profile(db, current_user, data)


@router.post("/me/password", response_model=MessageResponse)
def change_password(
    data: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    UserService.change_password(db, current_user, data)
    return MessageResponse(message="Password updated successfully")
