"""
Test Case Module Service - CRUD Operations
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.test_case_module import TestCaseModule
from app.models.test_case import TestCase
from app.schemas.test_case_module import (
    TestCaseModuleCreate,
    TestCaseModuleUpdate,
    TestCaseModuleTreeResponse
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class TestCaseModuleService:
    """Test Case Module Service"""

    def __init__(self, db: Session):
        self.db = db

    def get_modules_by_team(
        self,
        team_id: int,
        include_test_case_count: bool = False
    ) -> List[TestCaseModule]:
        """
        Get all modules for a team
        
        Args:
            team_id: Team ID
            include_test_case_count: Whether to include test case count
            
        Returns:
            List of test case modules
        """
        logger.debug(f"获取团队模块列表: team_id={team_id}, include_test_case_count={include_test_case_count}")

        modules = self.db.query(TestCaseModule).filter(
            TestCaseModule.team_id == team_id
        ).order_by(TestCaseModule.sort_order).all()
        
        logger.debug(f"团队模块列表查询结果: team_id={team_id}, module_count={len(modules)}")
        return modules

    def get_module_tree(
        self,
        team_id: int
    ) -> List[TestCaseModuleTreeResponse]:
        """
        Get module tree structure for a team
        
        Args:
            team_id: Team ID
            
        Returns:
            List of module tree nodes
        """
        logger.info(f"获取模块树: team_id={team_id}")

        # Get all modules
        modules = self.get_modules_by_team(team_id)
        
        # Get test case counts for all modules
        module_counts = {}
        for module in modules:
            count = self.db.query(TestCase).filter(
                TestCase.module_id == module.id
            ).count()
            module_counts[module.id] = count
        
        logger.debug(f"模块用例统计完成: team_id={team_id}, module_count={len(module_counts)}")

        # Build tree structure
        module_map = {m.id: m for m in modules}
        root_modules = []
        
        for module in modules:
            if module.parent_id is None:
                root_modules.append(module)
        
        def build_tree(module: TestCaseModule) -> TestCaseModuleTreeResponse:
            """Recursively build tree structure"""
            children = [
                build_tree(module_map[child.id])
                for child in modules
                if child.parent_id == module.id
            ]
            
            return TestCaseModuleTreeResponse(
                id=module.id,
                team_id=module.team_id,
                name=module.name,
                parent_id=module.parent_id,
                description=module.description,
                sort_order=module.sort_order,
                created_by=module.created_by,
                created_at=module.created_at,
                updated_at=module.updated_at,
                children=children,
                test_case_count=module_counts.get(module.id, 0)
            )
        
        result = [build_tree(m) for m in root_modules]
        logger.debug(f"模块树构建完成: team_id={team_id}, root_count={len(root_modules)}")
        return result

    def get_module(self, module_id: int) -> Optional[TestCaseModule]:
        """
        Get module by ID
        
        Args:
            module_id: Module ID
            
        Returns:
            Test case module or None
        """
        logger.debug(f"获取模块: module_id={module_id}")

        module = self.db.query(TestCaseModule).filter(
            TestCaseModule.id == module_id
        ).first()
        
        if not module:
            logger.warning(f"模块不存在: module_id={module_id}")
        
        return module

    def create_module(
        self,
        module_data: TestCaseModuleCreate,
        team_id: int,
        user_id: int
    ) -> TestCaseModule:
        """
        Create a new module
        
        Args:
            module_data: Module creation data
            team_id: Team ID
            user_id: Creator user ID
            
        Returns:
            Created module
        """
        logger.info(f"创建模块: name={module_data.name}, team_id={team_id}, parent_id={module_data.parent_id}, user_id={user_id}")

        # Check if parent module exists and belongs to the same team
        if module_data.parent_id:
            parent = self.get_module(module_data.parent_id)
            if not parent:
                logger.warning(f"创建模块失败，父模块不存在: parent_id={module_data.parent_id}")
                raise HTTPException(
                    status_code=404,
                    detail="Parent module not found"
                )
            if parent.team_id != team_id:
                logger.warning(f"创建模块失败，父模块不属于当前团队: parent_id={module_data.parent_id}, parent_team_id={parent.team_id}, team_id={team_id}")
                raise HTTPException(
                    status_code=400,
                    detail="Parent module does not belong to this team"
                )
        
        # Check for duplicate name in same parent
        existing = self.db.query(TestCaseModule).filter(
            TestCaseModule.team_id == team_id,
            TestCaseModule.name == module_data.name,
            TestCaseModule.parent_id == module_data.parent_id
        ).first()
        
        if existing:
            logger.warning(f"创建模块失败，同层级下已存在同名模块: name={module_data.name}, team_id={team_id}, parent_id={module_data.parent_id}")
            raise HTTPException(
                status_code=400,
                detail="Module with this name already exists in the same parent"
            )
        
        module = TestCaseModule(
            team_id=team_id,
            name=module_data.name,
            parent_id=module_data.parent_id,
            description=module_data.description,
            sort_order=module_data.sort_order,
            created_by=user_id
        )
        
        self.db.add(module)
        self.db.commit()
        self.db.refresh(module)
        
        logger.info(f"模块创建成功: module_id={module.id}, name={module.name}, team_id={team_id}")
        return module

    def update_module(
        self,
        module_id: int,
        module_data: TestCaseModuleUpdate,
        user_id: int
    ) -> TestCaseModule:
        """
        Update module
        
        Args:
            module_id: Module ID
            module_data: Module update data
            user_id: User ID performing the update
            
        Returns:
            Updated module
        """
        logger.info(f"更新模块: module_id={module_id}, user_id={user_id}")

        module = self.get_module(module_id)
        if not module:
            logger.warning(f"更新模块失败，模块不存在: module_id={module_id}")
            raise HTTPException(status_code=404, detail="Module not found")
        
        # Check parent module if changing
        if module_data.parent_id is not None:
            if module_data.parent_id == module_id:
                logger.warning(f"更新模块失败，不能将模块设为自身的子模块: module_id={module_id}")
                raise HTTPException(
                    status_code=400,
                    detail="Module cannot be its own parent"
                )
            
            if module_data.parent_id:
                parent = self.get_module(module_data.parent_id)
                if not parent:
                    logger.warning(f"更新模块失败，父模块不存在: parent_id={module_data.parent_id}")
                    raise HTTPException(
                        status_code=404,
                        detail="Parent module not found"
                    )
                if parent.team_id != module.team_id:
                    logger.warning(f"更新模块失败，父模块不属于当前团队: parent_id={module_data.parent_id}")
                    raise HTTPException(
                        status_code=400,
                        detail="Parent module does not belong to this team"
                    )
                
                # Check for circular reference
                current_parent = parent
                while current_parent:
                    if current_parent.id == module_id:
                        logger.warning(f"更新模块失败，检测到循环引用: module_id={module_id}, parent_id={module_data.parent_id}")
                        raise HTTPException(
                            status_code=400,
                            detail="Circular reference detected in module hierarchy"
                        )
                    current_parent = self.get_module(current_parent.parent_id) if current_parent.parent_id else None
        
        # Check for duplicate name if name is being changed
        if module_data.name:
            existing = self.db.query(TestCaseModule).filter(
                TestCaseModule.team_id == module.team_id,
                TestCaseModule.name == module_data.name,
                TestCaseModule.parent_id == module_data.parent_id if module_data.parent_id is not None else module.parent_id,
                TestCaseModule.id != module_id
            ).first()
            
            if existing:
                logger.warning(f"更新模块失败，同层级下已存在同名模块: name={module_data.name}, module_id={module_id}")
                raise HTTPException(
                    status_code=400,
                    detail="Module with this name already exists in the same parent"
                )
        
        # Update fields
        update_dict = module_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(module, field, value)
        
        self.db.commit()
        self.db.refresh(module)
        
        logger.info(f"模块更新成功: module_id={module_id}")
        return module

    def delete_module(self, module_id: int) -> dict:
        """
        Delete module
        
        Args:
            module_id: Module ID
            
        Returns:
            Deletion confirmation
        """
        logger.info(f"删除模块: module_id={module_id}")

        module = self.get_module(module_id)
        if not module:
            logger.warning(f"删除模块失败，模块不存在: module_id={module_id}")
            raise HTTPException(status_code=404, detail="Module not found")
        
        # Check if module has children
        children_count = self.db.query(TestCaseModule).filter(
            TestCaseModule.parent_id == module_id
        ).count()
        
        if children_count > 0:
            logger.warning(f"删除模块失败，存在子模块: module_id={module_id}, children_count={children_count}")
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete module with {children_count} child module(s). Please delete or move child modules first."
            )
        
        # Check if module has test cases
        test_cases_count = self.db.query(TestCase).filter(
            TestCase.module_id == module_id
        ).count()
        
        if test_cases_count > 0:
            logger.warning(f"删除模块失败，存在测试用例: module_id={module_id}, test_cases_count={test_cases_count}")
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete module with {test_cases_count} test case(s). Please delete or move test cases first."
            )
        
        # Store info before deletion
        module_info = {
            "id": module.id,
            "name": module.name,
            "team_id": module.team_id
        }
        
        self.db.delete(module)
        self.db.commit()
        
        logger.info(f"模块删除成功: module_id={module_id}, name={module_info['name']}")
        return {
            "success": True,
            "deleted_module": module_info,
            "message": f"Module '{module_info['name']}' deleted successfully"
        }
