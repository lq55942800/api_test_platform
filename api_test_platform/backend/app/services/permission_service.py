from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.base_models import User, TeamMember
from app.services.auth_service import get_current_active_user


async def get_user_team_ids(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[int]:
    if current_user.is_superuser:
        from app.models.base_models import Team
        teams = db.query(Team).filter(Team.is_active == True).all()
        return [t.id for t in teams]

    memberships = db.query(TeamMember).filter(
        TeamMember.user_id == current_user.id,
        TeamMember.status == "active",
    ).all()
    return [m.team_id for m in memberships]


async def get_user_team_ids_with_user(
    current_user: User,
    db: Session,
) -> List[int]:
    if current_user.is_superuser:
        from app.models.base_models import Team
        teams = db.query(Team).filter(Team.is_active == True).all()
        return [t.id for t in teams]

    memberships = db.query(TeamMember).filter(
        TeamMember.user_id == current_user.id,
        TeamMember.status == "active",
    ).all()
    return [m.team_id for m in memberships]


def check_team_access(user: User, db: Session, team_id: int) -> None:
    if user.is_superuser:
        return
    membership = db.query(TeamMember).filter(
        TeamMember.user_id == user.id,
        TeamMember.team_id == team_id,
        TeamMember.status == "active",
    ).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this team"
        )


def check_team_admin(user: User, db: Session, team_id: int) -> None:
    if user.is_superuser:
        return
    membership = db.query(TeamMember).filter(
        TeamMember.user_id == user.id,
        TeamMember.team_id == team_id,
        TeamMember.status == "active",
        TeamMember.role == "team_leader",
    ).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only team leaders can perform this action"
        )
