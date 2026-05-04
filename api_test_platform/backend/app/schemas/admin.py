from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class TeamResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    member_count: int = 0
    api_count: int = 0
    test_case_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TeamMemberCreate(BaseModel):
    user_id: int
    role: str = Field(default="tester", pattern=r'^(team_leader|developer|tester)$')


class TeamMemberUpdate(BaseModel):
    role: str = Field(pattern=r'^(team_leader|developer|tester)$')


class TeamMemberResponse(BaseModel):
    id: int
    team_id: int
    user_id: int
    username: str
    full_name: Optional[str] = None
    role: str
    status: str
    joined_at: datetime

    model_config = {"from_attributes": True}


class AdminUserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    email: str = Field(max_length=100)
    password: str = Field(min_length=8, max_length=32)
    full_name: Optional[str] = Field(None, max_length=100)
    is_superuser: bool = False


class AdminUserUpdate(BaseModel):
    email: Optional[str] = Field(None, max_length=100)
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class AdminUserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime
    teams: List[dict] = []

    model_config = {"from_attributes": True}


class AdminPasswordReset(BaseModel):
    new_password: str = Field(min_length=8, max_length=32)
