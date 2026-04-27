"""
Test Case Service - Cross Team Copy Functionality
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from fastapi import HTTPException
import json

from app.models.test_case import TestCase
from app.models.test_case_step import TestCaseStep
from app.models.api import ApiDefinition
from app.models.environment import Environment, EnvService, EnvVariable


class TestCaseService:
    """Test Case Service for cross-team copy operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_test_case(self, test_case_id: int) -> Optional[TestCase]:
        """Get test case by ID with steps loaded"""
        return self.db.query(TestCase).options(
            joinedload(TestCase.steps).joinedload(TestCaseStep.api)
        ).filter(TestCase.id == test_case_id).first()

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
        # Get source test case with steps
        source_case = self.get_test_case(test_case_id)
        if not source_case:
            raise HTTPException(status_code=404, detail="Test case not found")

        if source_case.team_id == target_team_id:
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
        # First check compatibility
        check_result = self.check_cross_team_copy(test_case_id, target_team_id)

        if not check_result["can_copy"]:
            raise HTTPException(
                status_code=400,
                detail="Cannot copy due to missing services. Please resolve the errors first."
            )

        # Get source test case
        source_case = self.get_test_case(test_case_id)
        if not source_case:
            raise HTTPException(status_code=404, detail="Test case not found")

        # Default copy options
        options = copy_options or {}
        copy_steps = options.get("copy_steps", True)
        copy_variables = options.get("copy_variables", True)

        # Create new test case
        new_case = TestCase(
            team_id=target_team_id,
            name=f"{source_case.name} (副本)",
            module_id=None,  # Module belongs to source team, reset for target
            description=source_case.description,
            status=source_case.status,
            priority=source_case.priority,
            tags=source_case.tags,
            variables=source_case.variables if copy_variables else None,
            execution_condition=source_case.execution_condition,
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
