from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_active_user, get_current_studio_user
from app.db.session import get_db
from app.middleware.rate_limit import limiter
from app.models import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    GoogleLoginRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    StudioUserResponse,
    TokenResponse,
    UserResponse,
)
from app.schemas.common import MessageResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])
settings = get_settings()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.rate_limit_auth)
def register(request: Request, response: Response, data: RegisterRequest, db: Session = Depends(get_db)):
    user = AuthService.register(db, data)
    return user


@router.post("/login", response_model=TokenResponse)
@limiter.limit(settings.rate_limit_auth)
def login(request: Request, response: Response, data: LoginRequest, db: Session = Depends(get_db)):
    forwarded = request.headers.get("X-Forwarded-For")
    ip_address = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else None)
    _, tokens = AuthService.login(
        db,
        data,
        ip_address=ip_address,
        user_agent=request.headers.get("user-agent"),
    )
    return tokens


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit(settings.rate_limit_auth)
def refresh_token(request: Request, response: Response, data: RefreshTokenRequest, db: Session = Depends(get_db)):
    return AuthService.refresh_access_token(db, data.refresh_token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get("/studio/me", response_model=StudioUserResponse)
def get_studio_me(current_user: User = Depends(get_current_studio_user), db: Session = Depends(get_db)):
    return AuthService.studio_user_response(db, current_user)


@router.post("/google", response_model=TokenResponse)
@limiter.limit(settings.rate_limit_auth)
def google_login(request: Request, response: Response, data: GoogleLoginRequest, db: Session = Depends(get_db)):
    _, tokens = AuthService.login_google(db, data.id_token)
    return tokens


@router.post("/forgot-password", response_model=MessageResponse)
@limiter.limit(settings.rate_limit_auth)
def forgot_password(request: Request, response: Response, data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    AuthService.request_password_reset(db, data.email)
    return MessageResponse(message="If an account exists for that email, a password reset link has been sent.")


@router.post("/reset-password", response_model=MessageResponse)
@limiter.limit(settings.rate_limit_auth)
def reset_password(request: Request, response: Response, data: ResetPasswordRequest, db: Session = Depends(get_db)):
    AuthService.reset_password(db, data.token, data.new_password)
    return MessageResponse(message="Password updated. You can sign in with your new password.")
