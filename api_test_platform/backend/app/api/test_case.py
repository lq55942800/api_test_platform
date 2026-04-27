"""
Test Case API Routes - Cross Team Copy
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.test_case import (
    CrossTeamCopyRequest,
    CrossTeamCopyCheckResponse,
    TestCaseResponse
)
from app.services.test_case_service import TestCaseService

router = APIRouter(prefix="/test-cases", tags=["Test Cases"])


@router.get("/{test_case_id}", response_model=TestCaseResponse)
def get_test_case(
    test_case_id: int,
    db: Session = Depends(get_db)
):
    """Get test case by ID"""
    service = TestCaseService(db)
    test_case = service.get_test_case(test_case_id)
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    return test_case


@router.post("/{test_case_id}/check-copy", response_model=CrossTeamCopyCheckResponse)
def check_cross_team_copy(
    test_case_id: int,
    target_team_id: int = Query(..., description="Target team ID"),
    db: Session = Depends(get_db)
):
    """
    Check cross-team copy compatibility

    This endpoint checks if a test case can be copied to another team by verifying:
    - Whether target team has the required services
    - Whether environment variables exist in target team
    - Generates environment difference report

    Returns warnings and recommendations for any missing configurations.
    """
    service = TestCaseService(db)
    result = service.check_cross_team_copy(test_case_id, target_team_id)

    return CrossTeamCopyCheckResponse(
        can_copy=result["can_copy"],
        warnings=result["warnings"],
        services_to_check=result["services_to_check"],
        variables_to_check=result["variables_to_check"]
    )


@router.post("/{test_case_id}/copy-to-team", response_model=dict)
def copy_to_team(
    test_case_id: int,
    request: CrossTeamCopyRequest,
    user_id: int = Query(..., description="User ID performing the copy"),
    db: Session = Depends(get_db)
):
    """
    Execute cross-team copy

    Copies a test case to another team. Before copying, ensure you have:
    1. Called the check-copy endpoint to verify compatibility
    2. Created necessary services in target team's environment
    3. Configured required environment variables

    The copy process will:
    - Create a new test case in target team
    - Copy all test steps
    - Create API definitions if they don't exist in target team
    - Map services to target team's environment
    """
    service = TestCaseService(db)
    result = service.copy_to_team(
        test_case_id=test_case_id,
        target_team_id=request.target_team_id,
        user_id=user_id,
        copy_options=request.copy_options
    )
    return result
