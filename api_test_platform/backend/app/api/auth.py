from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.base_models import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    UpdateUserRequest,
    ChangePasswordRequest,
    TokenResponse,
    UserResponse,
    MessageResponse,
)
from app.services.auth_service import AuthService, get_current_active_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    return auth_service.register(data)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    return auth_service.login(data)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(data: RefreshRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    return auth_service.refresh_token(data.refresh_token)


@router.post("/logout", response_model=MessageResponse)
def logout(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    auth_service.logout(current_user)
    return MessageResponse(message="Successfully logged out")


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
def update_me(
    data: UpdateUserRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    auth_service = AuthService(db)
    return auth_service.update_profile(current_user, data)


@router.put("/password", response_model=MessageResponse)
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    auth_service = AuthService(db)
    auth_service.change_password(current_user, data)
    return MessageResponse(message="Password changed successfully")
