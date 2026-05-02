"""
Test Case Service - CRUD and Cross Team Copy Functionality
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from fastapi import HTTPException
import json

from app.models.test_case import TestCase
from app.models.test_case_step import TestCaseStep
from app.models.api import ApiDefinition
from app.models.environment import Environment, EnvService, EnvVariable
from app.schemas.test_case import TestCaseCreate, TestCaseUpdate
from app.core.logging import get_logger

logger = get_logger(__name__)


class TestCaseService:
    """Test Case Service for cross-team copy operations"""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def build_step_tree(steps) -> list:
        logger.debug(f"构建步骤树: step_count={len(steps) if steps else 0}")

        import json
        step_map = {}
        roots = []
        for step in steps:
            step_dict = {
                "id": step.id,
                "test_case_id": step.test_case_id,
                "step_type": step.step_type or "api",
                "api_id": step.api_id,
                "parent_step_id": step.parent_step_id,
                "step_name": step.step_name,
                "sort_order": step.sort_order,
                "enabled": step.enabled,
                "override_headers": step.override_headers,
                "override_params": step.override_params,
                "override_body": step.override_body,
                "override_body_type": step.override_body_type,
                "override_cookies": step.override_cookies,
                "assertions": step.assertions,
                "extractors": step.extractors,
                "pre_script": step.pre_script,
                "post_script": step.post_script,
                "timeout_config": step.timeout_config,
                "execution_condition": step.execution_condition,
                "created_at": step.created_at.isoformat() if step.created_at else None,
                "updated_at": step.updated_at.isoformat() if step.updated_at else None,
                "children": []
            }
            for json_field in ["override_headers", "override_params", "assertions", "extractors", "execution_condition", "timeout_config"]:
                if isinstance(step_dict[json_field], str):
                    try:
                        step_dict[json_field] = json.loads(step_dict[json_field])
                    except (json.JSONDecodeError, TypeError):
                        pass
            step_map[step.id] = step_dict
        for step_id, step_dict in step_map.items():
            parent_id = step_dict["parent_step_id"]
            if parent_id and parent_id in step_map:
                step_map[parent_id]["children"].append(step_dict)
            else:
                roots.append(step_dict)
        for step_dict in step_map.values():
            step_dict["children"].sort(key=lambda x: x["sort_order"])
        roots.sort(key=lambda x: x["sort_order"])

        logger.debug(f"步骤树构建完成: root_count={len(roots)}")
        return roots

    def _convert_test_case(self, test_case: TestCase) -> TestCase:
        """Convert JSON string fields to Python objects"""
        if test_case:
            # Convert tags
            if test_case.tags and isinstance(test_case.tags, str):
                try:
                    test_case.tags = json.loads(test_case.tags)
                except Exception:
                    logger.warning(f"测试用例tags JSON解析失败: test_case_id={test_case.id}")
                    test_case.tags = []
            
            # Convert variables
            if test_case.variables and isinstance(test_case.variables, str):
                try:
                    test_case.variables = json.loads(test_case.variables)
                except Exception:
                    logger.warning(f"测试用例variables JSON解析失败: test_case_id={test_case.id}")
                    test_case.variables = []
            
            # Convert step fields
            for step in test_case.steps:
                if step.override_headers and isinstance(step.override_headers, str):
                    try:
                        step.override_headers = json.loads(step.override_headers)
                    except Exception:
                        logger.debug(f"步骤override_headers JSON解析失败: step_id={step.id}")
                        step.override_headers = None
                
                if step.override_params and isinstance(step.override_params, str):
                    try:
                        step.override_params = json.loads(step.override_params)
                    except Exception:
                        logger.debug(f"步骤override_params JSON解析失败: step_id={step.id}")
                        step.override_params = None
                
                if step.override_body and isinstance(step.override_body, str):
                    try:
                        step.override_body = json.loads(step.override_body)
                    except Exception:
                        logger.debug(f"步骤override_body JSON解析失败: step_id={step.id}")
                        step.override_body = None
                
                if step.override_cookies and isinstance(step.override_cookies, str):
                    try:
                        step.override_cookies = json.loads(step.override_cookies)
                    except Exception:
                        logger.debug(f"步骤override_cookies JSON解析失败: step_id={step.id}")
                        step.override_cookies = None
                
                if step.assertions and isinstance(step.assertions, str):
                    try:
                        step.assertions = json.loads(step.assertions)
                    except Exception:
                        logger.debug(f"步骤assertions JSON解析失败: step_id={step.id}")
                        step.assertions = None
                
                if step.extractors and isinstance(step.extractors, str):
                    try:
                        step.extractors = json.loads(step.extractors)
                    except Exception:
                        logger.debug(f"步骤extractors JSON解析失败: step_id={step.id}")
                        step.extractors = None
                
                if step.timeout_config and isinstance(step.timeout_config, str):
                    try:
                        step.timeout_config = json.loads(step.timeout_config)
                    except Exception:
                        logger.debug(f"步骤timeout_config JSON解析失败: step_id={step.id}")
                        step.timeout_config = None
                
                if step.execution_condition and isinstance(step.execution_condition, str):
                    try:
                        step.execution_condition = json.loads(step.execution_condition)
                    except Exception:
                        logger.debug(f"步骤execution_condition JSON解析失败: step_id={step.id}")
                        step.execution_condition = None
        
        return test_case

    def get_test_case(self, test_case_id: int) -> Optional[TestCase]:
        """Get test case by ID with steps loaded"""
        logger.debug(f"获取测试用例: test_case_id={test_case_id}")

        test_case = self.db.query(TestCase).options(
            joinedload(TestCase.steps).joinedload(TestCaseStep.api)
        ).filter(TestCase.id == test_case_id).first()
        test_case = self._convert_test_case(test_case)
        if test_case:
            test_case.steps_tree = self.build_step_tree(test_case.steps)
            self.db.expunge(test_case)
        else:
            logger.warning(f"测试用例不存在: test_case_id={test_case_id}")

        return test_case

    def get_test_cases(
        self,
        team_id: Optional[int] = None,
        module_id: Optional[int] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        priority: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TestCase]:
        """
        Get test cases with optional filtering and pagination
        """
        logger.info(f"获取测试用例列表: team_id={team_id}, module_id={module_id}, status={status}, keyword={keyword}, priority={priority}, skip={skip}, limit={limit}")

        query = self.db.query(TestCase).options(
            joinedload(TestCase.steps)
        )
        
        if team_id:
            query = query.filter(TestCase.team_id == team_id)
        if module_id:
            query = query.filter(TestCase.module_id == module_id)
        if status:
            query = query.filter(TestCase.status == status)
        if priority:
            query = query.filter(TestCase.priority == priority)
        if keyword:
            query = query.filter(
                or_(
                    TestCase.name.ilike(f"%{keyword}%"),
                    TestCase.description.ilike(f"%{keyword}%"),
                )
            )
            
        test_cases = query.order_by(TestCase.created_at.desc()).offset(skip).limit(limit).all()
        result = []
        for tc in test_cases:
            converted = self._convert_test_case(tc)
            self.db.expunge(converted)
            result.append(converted)

        logger.debug(f"测试用例列表查询结果: count={len(result)}")
        return result

    def create_test_case(
        self,
        test_case_data: TestCaseCreate,
        team_id: int,
        user_id: int
    ) -> TestCase:
        """
        Create a new test case with steps
        
        Args:
            test_case_data: Test case creation data
            team_id: Team ID
            user_id: Creator user ID
            
        Returns:
            Created test case
        """
        logger.info(f"创建测试用例: name={test_case_data.name}, team_id={team_id}, user_id={user_id}, step_count={len(test_case_data.steps) if test_case_data.steps else 0}")

        try:
            # Create test case
            test_case_dict = test_case_data.model_dump(exclude={'steps'})
            
            # Convert tags and variables to JSON string if they are lists
            if 'tags' in test_case_dict and isinstance(test_case_dict['tags'], list):
                test_case_dict['tags'] = json.dumps(test_case_dict['tags'], ensure_ascii=False)
            if 'variables' in test_case_dict and isinstance(test_case_dict['variables'], list):
                test_case_dict['variables'] = json.dumps(test_case_dict['variables'], ensure_ascii=False)
            
            test_case = TestCase(
                team_id=team_id,
                created_by=user_id,
                **test_case_dict
            )
            self.db.add(test_case)
            self.db.flush()  # Get test_case.id
            
            # Create test steps
            if test_case_data.steps:
                for step_data in test_case_data.steps:
                    step_dict = step_data.model_dump()
                    
                    if step_dict.get('step_type') is None:
                        step_dict['step_type'] = 'api'
                    
                    # Convert JSON fields to string
                    if step_dict.get('override_headers') and isinstance(step_dict['override_headers'], dict):
                        step_dict['override_headers'] = json.dumps(step_dict['override_headers'])
                    if step_dict.get('override_params') and isinstance(step_dict['override_params'], dict):
                        step_dict['override_params'] = json.dumps(step_dict['override_params'])
                    if step_dict.get('override_body') and isinstance(step_dict['override_body'], dict):
                        step_dict['override_body'] = json.dumps(step_dict['override_body'])
                    if step_dict.get('override_cookies') and isinstance(step_dict['override_cookies'], list):
                        step_dict['override_cookies'] = json.dumps(step_dict['override_cookies'])
                    if step_dict.get('assertions') and isinstance(step_dict['assertions'], list):
                        step_dict['assertions'] = json.dumps(step_dict['assertions'])
                    if step_dict.get('extractors') and isinstance(step_dict['extractors'], list):
                        step_dict['extractors'] = json.dumps(step_dict['extractors'])
                    if step_dict.get('timeout_config') and isinstance(step_dict['timeout_config'], dict):
                        step_dict['timeout_config'] = json.dumps(step_dict['timeout_config'])
                    if step_dict.get('execution_condition') and isinstance(step_dict['execution_condition'], dict):
                        step_dict['execution_condition'] = json.dumps(step_dict['execution_condition'])
                    
                    step = TestCaseStep(
                        test_case_id=test_case.id,
                        **step_dict
                    )
                    self.db.add(step)
                
                logger.debug(f"创建测试步骤: test_case_id={test_case.id}, step_count={len(test_case_data.steps)}")
            
            self.db.commit()
            self.db.refresh(test_case)
            
            logger.info(f"测试用例创建成功: test_case_id={test_case.id}, name={test_case.name}")
            return self.get_test_case(test_case.id)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建测试用例失败: name={test_case_data.name}, team_id={team_id}, error={str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to create test case: {str(e)}")

    def update_test_case(
        self,
        test_case_id: int,
        test_case_data: TestCaseUpdate,
        user_id: int
    ) -> TestCase:
        """
        Update test case and its steps
        
        Args:
            test_case_id: Test case ID
            test_case_data: Test case update data
            user_id: User ID performing the update
            
        Returns:
            Updated test case
        """
        logger.info(f"更新测试用例: test_case_id={test_case_id}, user_id={user_id}")

        try:
            # Get existing test case (without conversion)
            test_case = self.db.query(TestCase).options(
                joinedload(TestCase.steps)
            ).filter(TestCase.id == test_case_id).first()
            
            if not test_case:
                logger.warning(f"更新测试用例失败，用例不存在: test_case_id={test_case_id}")
                raise HTTPException(status_code=404, detail="Test case not found")
            
            # Update test case fields
            update_dict = test_case_data.model_dump(exclude_unset=True, exclude={'steps'})
            
            # Convert JSON fields
            if 'tags' in update_dict and isinstance(update_dict['tags'], list):
                update_dict['tags'] = json.dumps(update_dict['tags'])
            if 'variables' in update_dict and isinstance(update_dict['variables'], list):
                update_dict['variables'] = json.dumps(update_dict['variables'])
            
            for field, value in update_dict.items():
                setattr(test_case, field, value)
            
            # Update steps if provided
            if test_case_data.steps is not None:
                # Delete existing steps
                deleted_count = self.db.query(TestCaseStep).filter(
                    TestCaseStep.test_case_id == test_case_id
                ).delete()
                logger.debug(f"删除旧步骤: test_case_id={test_case_id}, deleted_count={deleted_count}")
                
                # Create new steps
                for step_data in test_case_data.steps:
                    step_dict = step_data.model_dump()
                    
                    if step_dict.get('step_type') is None:
                        step_dict['step_type'] = 'api'
                    
                    # Convert JSON fields to string
                    if step_dict.get('override_headers') and isinstance(step_dict['override_headers'], dict):
                        step_dict['override_headers'] = json.dumps(step_dict['override_headers'])
                    if step_dict.get('override_params') and isinstance(step_dict['override_params'], dict):
                        step_dict['override_params'] = json.dumps(step_dict['override_params'])
                    if step_dict.get('override_body') and isinstance(step_dict['override_body'], dict):
                        step_dict['override_body'] = json.dumps(step_dict['override_body'])
                    if step_dict.get('override_cookies') and isinstance(step_dict['override_cookies'], list):
                        step_dict['override_cookies'] = json.dumps(step_dict['override_cookies'])
                    if step_dict.get('assertions') and isinstance(step_dict['assertions'], list):
                        step_dict['assertions'] = json.dumps(step_dict['assertions'])
                    if step_dict.get('extractors') and isinstance(step_dict['extractors'], list):
                        step_dict['extractors'] = json.dumps(step_dict['extractors'])
                    if step_dict.get('timeout_config') and isinstance(step_dict['timeout_config'], dict):
                        step_dict['timeout_config'] = json.dumps(step_dict['timeout_config'])
                    if step_dict.get('execution_condition') and isinstance(step_dict['execution_condition'], dict):
                        step_dict['execution_condition'] = json.dumps(step_dict['execution_condition'])
                    
                    step = TestCaseStep(
                        test_case_id=test_case_id,
                        **step_dict
                    )
                    self.db.add(step)
                
                logger.debug(f"创建新步骤: test_case_id={test_case_id}, step_count={len(test_case_data.steps)}")
            
            self.db.commit()
            self.db.refresh(test_case)
            
            logger.info(f"测试用例更新成功: test_case_id={test_case_id}")
            return self.get_test_case(test_case_id)
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新测试用例失败: test_case_id={test_case_id}, error={str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to update test case: {str(e)}")

    def delete_test_case(self, test_case_id: int) -> Dict[str, Any]:
        """
        Delete test case and all its steps
        
        Args:
            test_case_id: Test case ID
            
        Returns:
            Deletion confirmation
        """
        logger.info(f"删除测试用例: test_case_id={test_case_id}")

        try:
            test_case = self.get_test_case(test_case_id)
            if not test_case:
                logger.warning(f"删除测试用例失败，用例不存在: test_case_id={test_case_id}")
                raise HTTPException(status_code=404, detail="Test case not found")
            
            # Store info before deletion
            test_case_info = {
                "id": test_case.id,
                "name": test_case.name,
                "team_id": test_case.team_id
            }
            
            # Delete test case (cascade will delete steps)
            self.db.delete(test_case)
            self.db.commit()
            
            logger.info(f"测试用例删除成功: test_case_id={test_case_id}, name={test_case_info['name']}")
            return {
                "success": True,
                "deleted_test_case": test_case_info,
                "message": f"Test case '{test_case_info['name']}' deleted successfully"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除测试用例失败: test_case_id={test_case_id}, error={str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to delete test case: {str(e)}")

    def check_cross_team_copy(
        self,
        test_case_id: int,
        target_team_id: int
    ) -> Dict[str, Any]:
        """
        Check cross-team copy compatibility

        Args:
            test_case_id: Source test case ID
            target_team_id: Target team ID

        Returns:
            Dict containing compatibility check results
        """
        logger.info(f"检查跨团队复制兼容性: test_case_id={test_case_id}, target_team_id={target_team_id}")

        # Get source test case with steps
        source_case = self.get_test_case(test_case_id)
        if not source_case:
            logger.warning(f"检查跨团队复制失败，源用例不存在: test_case_id={test_case_id}")
            raise HTTPException(status_code=404, detail="Test case not found")

        if source_case.team_id == target_team_id:
            logger.warning(f"跨团队复制目标团队与源团队相同: team_id={target_team_id}")
            raise HTTPException(
                status_code=400,
                detail="Cannot copy to the same team"
            )

        # Collect unique service names from test case steps
        services_info: Dict[str, Dict[str, Any]] = {}
        variables_used: set = set()

        for step in source_case.steps:
            if step.api and step.api.service_id:
                # Get service info
                service = self.db.query(EnvService).filter(
                    EnvService.id == step.api.service_id
                ).first()

                if service:
                    service_name = service.name
                    if service_name not in services_info:
                        services_info[service_name] = {
                            "source_service_id": service.id,
                            "source_environment_id": service.environment_id,
                            "source_service_name": service_name,
                            "api_count": 0,
                            "target_service_exists": False,
                            "target_service_id": None
                        }
                    services_info[service_name]["api_count"] += 1

            # Extract variables from step configurations
            self._extract_variables_from_step(step, variables_used)

        logger.debug(f"跨团队复制检查: service_count={len(services_info)}, variable_count={len(variables_used)}")

        # Extract variables from test case level
        if source_case.variables:
            try:
                case_vars = json.loads(source_case.variables) if isinstance(source_case.variables, str) else source_case.variables
                if isinstance(case_vars, list):
                    for var in case_vars:
                        if isinstance(var, dict) and "key" in var:
                            variables_used.add(var["key"])
            except (json.JSONDecodeError, TypeError):
                pass

        # Check target team's services
        target_environments = self.db.query(Environment).filter(
            Environment.team_id == target_team_id,
            Environment.is_active == True
        ).all()

        target_env_ids = [env.id for env in target_environments]

        warnings: List[Dict[str, str]] = []
        services_to_check: List[Dict[str, Any]] = []

        for service_name, info in services_info.items():
            # Check if target team has service with same name
            target_service = self.db.query(EnvService).join(Environment).filter(
                and_(
                    EnvService.name == service_name,
                    Environment.team_id == target_team_id,
                    Environment.is_active == True
                )
            ).first()

            if target_service:
                info["target_service_exists"] = True
                info["target_service_id"] = target_service.id
                info["target_environment_id"] = target_service.environment_id
            else:
                warnings.append({
                    "type": "service_missing",
                    "level": "error",
                    "service_name": service_name,
                    "message": f"Target team does not have service '{service_name}'. Please create this service in target team's environment first."
                })

            services_to_check.append(info)

        # Check variables in target team's default environment
        variables_to_check: List[Dict[str, Any]] = []
        if variables_used and target_env_ids:
            # Get default environment for target team
            default_env = self.db.query(Environment).filter(
                Environment.team_id == target_team_id,
                Environment.is_default == True,
                Environment.is_active == True
            ).first()

            if default_env:
                target_vars = self.db.query(EnvVariable).filter(
                    EnvVariable.environment_id == default_env.id
                ).all()
                target_var_keys = {var.key for var in target_vars}

                for var_key in variables_used:
                    var_info = {
                        "key": var_key,
                        "exists_in_target": var_key in target_var_keys
                    }
                    if not var_info["exists_in_target"]:
                        warnings.append({
                            "type": "variable_missing",
                            "level": "warning",
                            "variable_key": var_key,
                            "message": f"Variable '${{{var_key}}}' may not exist in target team's default environment. Please verify or create this variable."
                        })
                    variables_to_check.append(var_info)
            else:
                logger.warning(f"目标团队无默认环境: target_team_id={target_team_id}")
                warnings.append({
                    "type": "environment_missing",
                    "level": "warning",
                    "message": "Target team has no default environment configured. Variable references may not work correctly."
                })
                for var_key in variables_used:
                    variables_to_check.append({
                        "key": var_key,
                        "exists_in_target": False
                    })
                    warnings.append({
                        "type": "variable_missing",
                        "level": "warning",
                        "variable_key": var_key,
                        "message": f"Variable '${{{var_key}}}' may not exist in target team's environment. Please verify or create this variable."
                    })

        # Determine if copy can proceed
        has_blocking_errors = any(
            w["level"] == "error" for w in warnings
        )

        logger.info(f"跨团队复制检查完成: can_copy={not has_blocking_errors}, warning_count={len(warnings)}")
        return {
            "can_copy": not has_blocking_errors,
            "source_test_case": {
                "id": source_case.id,
                "name": source_case.name,
                "team_id": source_case.team_id,
                "step_count": len(source_case.steps)
            },
            "target_team_id": target_team_id,
            "warnings": warnings,
            "services_to_check": services_to_check,
            "variables_to_check": variables_to_check,
            "summary": {
                "total_services": len(services_info),
                "missing_services": sum(1 for s in services_to_check if not s["target_service_exists"]),
                "total_variables": len(variables_used),
                "missing_variables": sum(1 for v in variables_to_check if not v["exists_in_target"])
            }
        }

    def copy_to_team(
        self,
        test_case_id: int,
        target_team_id: int,
        user_id: int,
        copy_options: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """
        Execute cross-team copy

        Args:
            test_case_id: Source test case ID
            target_team_id: Target team ID
            user_id: User performing the copy
            copy_options: Optional copy configuration

        Returns:
            Dict containing copy results
        """
        logger.info(f"执行跨团队复制: test_case_id={test_case_id}, target_team_id={target_team_id}, user_id={user_id}")

        # First check compatibility
        check_result = self.check_cross_team_copy(test_case_id, target_team_id)

        if not check_result["can_copy"]:
            logger.warning(f"跨团队复制被阻止: test_case_id={test_case_id}, target_team_id={target_team_id}")
            raise HTTPException(
                status_code=400,
                detail="Cannot copy due to missing services. Please resolve the errors first."
            )

        # Get source test case
        source_case = self.get_test_case(test_case_id)
        if not source_case:
            logger.warning(f"跨团队复制失败，源用例不存在: test_case_id={test_case_id}")
            raise HTTPException(status_code=404, detail="Test case not found")

        # Default copy options
        options = copy_options or {}
        copy_steps = options.get("copy_steps", True)
        copy_variables = options.get("copy_variables", True)

        # Create new test case
        new_case = TestCase(
            team_id=target_team_id,
            name=f"{source_case.name} (副本)",
            module_id=None,
            description=source_case.description,
            status=source_case.status,
            priority=source_case.priority,
            tags=source_case.tags,
            variables=source_case.variables if copy_variables else None,
            created_by=user_id
        )
        self.db.add(new_case)
        self.db.flush()

        # Copy steps
        copied_steps = []
        api_mapping: Dict[int, int] = {}  # source_api_id -> target_api_id

        if copy_steps:
            for step in source_case.steps:
                # Check if we need to copy the API definition
                target_api_id = step.api_id

                if step.api:
                    # Check if target team has the same API
                    target_api = self._find_or_create_target_api(
                        step.api,
                        target_team_id,
                        check_result["services_to_check"],
                        user_id
                    )
                    target_api_id = target_api.id
                    api_mapping[step.api_id] = target_api.id

                new_step = TestCaseStep(
                    test_case_id=new_case.id,
                    api_id=target_api_id,
                    step_type=step.step_type or "api",
                    parent_step_id=step.parent_step_id,
                    step_name=step.step_name,
                    sort_order=step.sort_order,
                    enabled=step.enabled,
                    override_headers=step.override_headers,
                    override_params=step.override_params,
                    override_body=step.override_body,
                    override_body_type=step.override_body_type,
                    override_cookies=step.override_cookies,
                    assertions=step.assertions,
                    extractors=step.extractors,
                    pre_script=step.pre_script,
                    post_script=step.post_script,
                    timeout_config=step.timeout_config,
                    execution_condition=step.execution_condition
                )
                self.db.add(new_step)
                copied_steps.append({
                    "source_step_id": step.id,
                    "step_name": step.step_name
                })

        self.db.commit()
        self.db.refresh(new_case)

        logger.info(f"跨团队复制完成: source_test_case_id={test_case_id}, new_test_case_id={new_case.id}, copied_steps={len(copied_steps)}, api_mapping_count={len(api_mapping)}")
        return {
            "success": True,
            "new_test_case": {
                "id": new_case.id,
                "name": new_case.name,
                "team_id": new_case.team_id
            },
            "copied_steps": len(copied_steps),
            "api_mapping": api_mapping,
            "warnings": check_result["warnings"],
            "message": f"Test case copied successfully. {len(check_result['warnings'])} warning(s) need attention."
        }

    def _find_or_create_target_api(
        self,
        source_api: ApiDefinition,
        target_team_id: int,
        services_mapping: List[Dict[str, Any]],
        user_id: int
    ) -> ApiDefinition:
        """
        Find existing API in target team or create a reference

        Args:
            source_api: Source API definition
            target_team_id: Target team ID
            services_mapping: Service mapping from check result
            user_id: User ID

        Returns:
            Target API definition
        """
        logger.debug(f"查找或创建目标API: source_api_id={source_api.id}, method={source_api.method}, path={source_api.path}, target_team_id={target_team_id}")

        # Try to find existing API with same method and path in target team
        target_api = self.db.query(ApiDefinition).filter(
            and_(
                ApiDefinition.team_id == target_team_id,
                ApiDefinition.method == source_api.method,
                ApiDefinition.path == source_api.path,
                ApiDefinition.is_deleted == False
            )
        ).first()

        if target_api:
            logger.debug(f"找到目标团队已有API: target_api_id={target_api.id}")
            return target_api

        # Create new API definition for target team
        # Find target service ID
        target_service_id = None
        if source_api.service_id:
            for svc_info in services_mapping:
                if svc_info.get("source_service_id") == source_api.service_id:
                    target_service_id = svc_info.get("target_service_id")
                    break

        new_api = ApiDefinition(
            team_id=target_team_id,
            module_id=None,  # Reset module for target team
            service_id=target_service_id,
            name=source_api.name,
            method=source_api.method,
            path=source_api.path,
            description=source_api.description,
            status=source_api.status,
            protocol=source_api.protocol,
            path_params=source_api.path_params,
            query_params=source_api.query_params,
            header_params=source_api.header_params,
            cookie_params=source_api.cookie_params,
            body_type=source_api.body_type,
            body_definition=source_api.body_definition,
            responses=source_api.responses,
            pre_request_actions=source_api.pre_request_actions,
            post_request_actions=source_api.post_request_actions,
            assertions=source_api.assertions,
            connect_timeout=source_api.connect_timeout,
            read_timeout=source_api.read_timeout,
            write_timeout=source_api.write_timeout,
            pool_timeout=source_api.pool_timeout,
            sample_timeout=source_api.sample_timeout,
            sql_timeout=source_api.sql_timeout,
            script_timeout=source_api.script_timeout,
            timeout_enabled=source_api.timeout_enabled,
            owner_id=user_id,
            created_by=user_id
        )
        self.db.add(new_api)
        self.db.flush()

        logger.info(f"为目标团队创建新API: new_api_id={new_api.id}, name={new_api.name}, target_team_id={target_team_id}")
        return new_api

    def _extract_variables_from_step(
        self,
        step: TestCaseStep,
        variables: set
    ) -> None:
        """
        Extract variable references from step configuration

        Args:
            step: Test case step
            variables: Set to store extracted variable names
        """
        import re
        var_pattern = r'\$\{([^}]+)\}'

        fields_to_check = [
            step.override_headers,
            step.override_params,
            step.override_body,
            step.pre_script,
            step.post_script,
            step.assertions,
            step.extractors
        ]

        for field in fields_to_check:
            if field:
                if isinstance(field, str):
                    matches = re.findall(var_pattern, field)
                    variables.update(matches)
                elif isinstance(field, dict):
                    field_str = json.dumps(field)
                    matches = re.findall(var_pattern, field_str)
                    variables.update(matches)
                elif isinstance(field, list):
                    field_str = json.dumps(field)
                    matches = re.findall(var_pattern, field_str)
                    variables.update(matches)
