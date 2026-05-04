from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.base_models import User, TeamMember
from app.schemas.admin import AdminUserCreate, AdminUserUpdate, AdminUserResponse, AdminPasswordReset
from app.services.auth_service import get_current_active_user, get_password_hash, validate_password_strength

router = APIRouter(prefix="/admin/users", tags=["User Management"])


def _build_user_response(user: User, db: Session) -> AdminUserResponse:
    memberships = db.query(TeamMember).filter(
        TeamMember.user_id == user.id,
        TeamMember.status == "active",
    ).all()
    teams = []
    for m in memberships:
        from app.models.base_models import Team
        team = db.query(Team).filter(Team.id == m.team_id).first()
        if team:
            teams.append({"team_id": team.id, "team_name": team.name, "role": m.role})

    return AdminUserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
        teams=teams,
    )


@router.get("", response_model=List[AdminUserResponse])
def list_users(
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    query = db.query(User)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if search:
        query = query.filter(
            (User.username.contains(search)) | (User.email.contains(search)) | (User.full_name.contains(search))
        )
    users = query.order_by(User.id).all()
    return [_build_user_response(u, db) for u in users]


@router.post("", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: AdminUserCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    strength_error = validate_password_strength(data.password)
    if strength_error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=strength_error)

    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    existing_email = db.query(User).filter(User.email == data.email).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    user = User(
        username=data.username,
        email=data.email,
        password_hash=get_password_hash(data.password),
        full_name=data.full_name,
        is_active=True,
        is_superuser=data.is_superuser,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _build_user_response(user, db)


@router.get("/{user_id}", response_model=AdminUserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return _build_user_response(user, db)


@router.put("/{user_id}", response_model=AdminUserResponse)
def update_user(
    user_id: int,
    data: AdminUserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if data.email is not None:
        existing = db.query(User).filter(User.email == data.email, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
        user.email = data.email
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.is_superuser is not None:
        user.is_superuser = data.is_superuser

    db.commit()
    db.refresh(user)
    return _build_user_response(user, db)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete yourself")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.query(TeamMember).filter(TeamMember.user_id == user_id).delete()
    db.delete(user)
    db.commit()


@router.put("/{user_id}/reset-password", response_model=dict)
def reset_password(
    user_id: int,
    data: AdminPasswordReset,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    strength_error = validate_password_strength(data.new_password)
    if strength_error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=strength_error)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.password_hash = get_password_hash(data.new_password)
    user.login_fail_count = 0
    user.locked_until = None
    db.commit()
    return {"message": "Password reset successfully"}
