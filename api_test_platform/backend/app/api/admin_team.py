from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.base_models import Team, User, TeamMember
from app.schemas.admin import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamMemberCreate,
    TeamMemberUpdate,
    TeamMemberResponse,
)
from app.services.auth_service import get_current_active_user
from app.services.permission_service import check_team_access, check_team_admin

router = APIRouter(prefix="/admin/teams", tags=["Team Management"])


@router.get("", response_model=List[TeamResponse])
def list_teams(
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    query = db.query(Team)
    if is_active is not None:
        query = query.filter(Team.is_active == is_active)
    teams = query.order_by(Team.id).all()

    result = []
    for team in teams:
        member_count = db.query(TeamMember).filter(TeamMember.team_id == team.id, TeamMember.status == "active").count()
        api_count = 0
        test_case_count = 0
        if hasattr(team, 'apis'):
            api_count = len([a for a in team.apis if not getattr(a, 'is_deleted', False)])
        if hasattr(team, 'test_cases'):
            test_case_count = len(team.test_cases)
        result.append(TeamResponse(
            id=team.id,
            name=team.name,
            description=team.description,
            is_active=team.is_active,
            member_count=member_count,
            api_count=api_count,
            test_case_count=test_case_count,
            created_at=team.created_at,
            updated_at=team.updated_at,
        ))
    return result


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(
    data: TeamCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    existing = db.query(Team).filter(Team.name == data.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Team name already exists")

    team = Team(name=data.name, description=data.description)
    db.add(team)
    db.commit()
    db.refresh(team)
    return TeamResponse(
        id=team.id, name=team.name, description=team.description,
        is_active=team.is_active, member_count=0, api_count=0, test_case_count=0,
        created_at=team.created_at, updated_at=team.updated_at,
    )


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    check_team_access(current_user, db, team_id)
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    member_count = db.query(TeamMember).filter(TeamMember.team_id == team.id, TeamMember.status == "active").count()
    api_count = 0
    test_case_count = 0
    if hasattr(team, 'apis'):
        api_count = len([a for a in team.apis if not getattr(a, 'is_deleted', False)])
    if hasattr(team, 'test_cases'):
        test_case_count = len(team.test_cases)

    return TeamResponse(
        id=team.id, name=team.name, description=team.description,
        is_active=team.is_active, member_count=member_count,
        api_count=api_count, test_case_count=test_case_count,
        created_at=team.created_at, updated_at=team.updated_at,
    )


@router.put("/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: int,
    data: TeamUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    if data.name is not None:
        existing = db.query(Team).filter(Team.name == data.name, Team.id != team_id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Team name already exists")
        team.name = data.name
    if data.description is not None:
        team.description = data.description
    if data.is_active is not None:
        team.is_active = data.is_active

    db.commit()
    db.refresh(team)

    member_count = db.query(TeamMember).filter(TeamMember.team_id == team.id, TeamMember.status == "active").count()
    return TeamResponse(
        id=team.id, name=team.name, description=team.description,
        is_active=team.is_active, member_count=member_count,
        api_count=0, test_case_count=0,
        created_at=team.created_at, updated_at=team.updated_at,
    )


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    db.query(TeamMember).filter(TeamMember.team_id == team_id).delete()
    db.delete(team)
    db.commit()


@router.get("/{team_id}/members", response_model=List[TeamMemberResponse])
def list_team_members(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    check_team_access(current_user, db, team_id)

    members = db.query(TeamMember).filter(TeamMember.team_id == team_id).all()
    result = []
    for m in members:
        user = db.query(User).filter(User.id == m.user_id).first()
        result.append(TeamMemberResponse(
            id=m.id, team_id=m.team_id, user_id=m.user_id,
            username=user.username if user else "unknown",
            full_name=user.full_name if user else None,
            role=m.role, status=m.status, joined_at=m.joined_at,
        ))
    return result


@router.post("/{team_id}/members", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
def add_team_member(
    team_id: int,
    data: TeamMemberCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    check_team_admin(current_user, db, team_id)

    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == data.user_id,
    ).first()
    if existing:
        if existing.status == "active":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is already a member of this team")
        existing.status = "active"
        existing.role = data.role
        db.commit()
        db.refresh(existing)
        return TeamMemberResponse(
            id=existing.id, team_id=existing.team_id, user_id=existing.user_id,
            username=user.username, full_name=user.full_name,
            role=existing.role, status=existing.status, joined_at=existing.joined_at,
        )

    member = TeamMember(team_id=team_id, user_id=data.user_id, role=data.role)
    db.add(member)
    db.commit()
    db.refresh(member)
    return TeamMemberResponse(
        id=member.id, team_id=member.team_id, user_id=member.user_id,
        username=user.username, full_name=user.full_name,
        role=member.role, status=member.status, joined_at=member.joined_at,
    )


@router.put("/{team_id}/members/{member_id}", response_model=TeamMemberResponse)
def update_team_member(
    team_id: int,
    member_id: int,
    data: TeamMemberUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    check_team_admin(current_user, db, team_id)

    member = db.query(TeamMember).filter(
        TeamMember.id == member_id,
        TeamMember.team_id == team_id,
    ).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    member.role = data.role
    db.commit()
    db.refresh(member)

    user = db.query(User).filter(User.id == member.user_id).first()
    return TeamMemberResponse(
        id=member.id, team_id=member.team_id, user_id=member.user_id,
        username=user.username if user else "unknown",
        full_name=user.full_name if user else None,
        role=member.role, status=member.status, joined_at=member.joined_at,
    )


@router.delete("/{team_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_team_member(
    team_id: int,
    member_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    check_team_admin(current_user, db, team_id)

    member = db.query(TeamMember).filter(
        TeamMember.id == member_id,
        TeamMember.team_id == team_id,
    ).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    member.status = "inactive"
    db.commit()
