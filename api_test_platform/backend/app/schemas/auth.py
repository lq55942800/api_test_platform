from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    email: EmailStr
    password: str = Field(min_length=8, max_length=32)
    full_name: Optional[str] = Field(None, max_length=100)


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UpdateUserRequest(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8, max_length=32)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class MessageResponse(BaseModel):
    message: str
