"""
Test Case Module API Routes - CRUD Operations
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.session import get_db
from app.schemas.test_case_module import (
    TestCaseModuleCreate,
    TestCaseModuleUpdate,
    TestCaseModuleResponse,
    TestCaseModuleTreeResponse
)
from app.services.test_case_module_service import TestCaseModuleService

logger = get_logger(__name__)

router = APIRouter(prefix="/test-case-modules", tags=["Test Case Modules"])


@router.get("/", response_model=List[TestCaseModuleResponse])
def get_modules(
    team_id: int = Query(..., description="Team ID"),
    db: Session = Depends(get_db)
):
    """
    Get all modules for a team (flat list)
    
    - **team_id**: Team ID (required)
    """
    logger.info(f"查询模块列表: team_id={team_id}")
    try:
        service = TestCaseModuleService(db)
        modules = service.get_modules_by_team(team_id)
        logger.info(f"查询模块列表成功: team_id={team_id}, count={len(modules)}")
        return modules
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询模块列表失败: team_id={team_id}, error={str(e)}")
        raise


@router.get("/tree", response_model=List[TestCaseModuleTreeResponse])
def get_module_tree(
    team_id: int = Query(..., description="Team ID"),
    db: Session = Depends(get_db)
):
    """
    Get module tree structure for a team
    
    Returns modules in a hierarchical tree structure with test case counts.
    
    - **team_id**: Team ID (required)
    """
    logger.info(f"查询模块树: team_id={team_id}")
    try:
        service = TestCaseModuleService(db)
        tree = service.get_module_tree(team_id)
        logger.info(f"查询模块树成功: team_id={team_id}")
        return tree
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询模块树失败: team_id={team_id}, error={str(e)}")
        raise


@router.get("/{module_id}", response_model=TestCaseModuleResponse)
def get_module(
    module_id: int,
    db: Session = Depends(get_db)
):
    """
    Get module by ID
    
    - **module_id**: Module ID
    """
    logger.info(f"查询模块详情: module_id={module_id}")
    try:
        service = TestCaseModuleService(db)
        module = service.get_module(module_id)
        if not module:
            logger.warning(f"模块不存在: module_id={module_id}")
            raise HTTPException(status_code=404, detail="Module not found")
        return module
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询模块详情失败: module_id={module_id}, error={str(e)}")
        raise


@router.post("/", response_model=TestCaseModuleResponse, status_code=201)
def create_module(
    module_data: TestCaseModuleCreate,
    team_id: int = Query(..., description="Team ID"),
    user_id: int = Query(..., description="Creator user ID"),
    db: Session = Depends(get_db)
):
    """
    Create a new module
    
    - **name**: Module name (required, 1-50 characters)
    - **parent_id**: Parent module ID (optional, for nested modules)
    - **description**: Module description (optional, max 500 characters)
    - **sort_order**: Sort order (default: 0)
    """
    logger.info(f"创建模块: team_id={team_id}, user_id={user_id}, name={module_data.name}")
    try:
        service = TestCaseModuleService(db)
        module = service.create_module(
            module_data=module_data,
            team_id=team_id,
            user_id=user_id
        )
        logger.info(f"模块创建成功: team_id={team_id}, name={module_data.name}, module_id={module.id}")
        return module
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建模块失败: team_id={team_id}, name={module_data.name}, error={str(e)}")
        raise


@router.put("/{module_id}", response_model=TestCaseModuleResponse)
def update_module(
    module_id: int,
    module_data: TestCaseModuleUpdate,
    user_id: int = Query(..., description="User ID performing the update"),
    db: Session = Depends(get_db)
):
    """
    Update module
    
    - **name**: Module name (optional, 1-50 characters)
    - **parent_id**: Parent module ID (optional, for nested modules)
    - **description**: Module description (optional, max 500 characters)
    - **sort_order**: Sort order (optional)
    """
    logger.info(f"更新模块: module_id={module_id}, user_id={user_id}")
    try:
        service = TestCaseModuleService(db)
        module = service.update_module(
            module_id=module_id,
            module_data=module_data,
            user_id=user_id
        )
        logger.info(f"模块更新成功: module_id={module_id}")
        return module
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新模块失败: module_id={module_id}, error={str(e)}")
        raise


@router.delete("/{module_id}")
def delete_module(
    module_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete module
    
    Note: Cannot delete a module that has child modules or test cases.
    Please delete or move child modules and test cases first.
    
    - **module_id**: Module ID
    """
    logger.info(f"删除模块: module_id={module_id}")
    try:
        service = TestCaseModuleService(db)
        result = service.delete_module(module_id)
        logger.info(f"模块删除成功: module_id={module_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除模块失败: module_id={module_id}, error={str(e)}")
        raise
