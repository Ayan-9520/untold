from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_active_user, get_current_studio_user
from app.db.session import get_db
from app.middleware.rate_limit import limiter
from app.models import User
from app.schemas.auth import (
    GoogleLoginRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    StudioUserResponse,
    TokenResponse,
    UserResponse,
)
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
    _, tokens = AuthService.login(db, data)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit(settings.rate_limit_auth)
def refresh_token(request: Request, response: Response, data: RefreshTokenRequest, db: Session = Depends(get_db)):
    return AuthService.refresh_access_token(db, data.refresh_token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get("/studio/me", response_model=StudioUserResponse)
def get_studio_me(current_user: User = Depends(get_current_studio_user)):
    return AuthService.studio_user_response(current_user)


@router.post("/google", response_model=TokenResponse)
@limiter.limit(settings.rate_limit_auth)
def google_login(request: Request, response: Response, data: GoogleLoginRequest, db: Session = Depends(get_db)):
    _, tokens = AuthService.login_google(db, data.id_token)
    return tokens
