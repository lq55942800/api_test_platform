"""
Test Case Execution Engine - Execute test cases step by step with variable management,
assertion validation, and variable extraction.
"""
import json
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.test_case import TestCase
from app.models.test_case_step import TestCaseStep
from app.models.api import ApiDefinition
from app.models.execution_record import TestCaseExecutionRecord, StepExecutionRecord
from app.core.logging import get_logger
from app.services.debug_engine import DebugEngine
from app.services.execution_service import ExecutionService
from app.services.engines.variable_manager import VariableManager
from app.services.engines.assertion_engine import AssertionEngine
from app.services.extractors.extractor_engine import ExtractorEngine

logger = get_logger(__name__)


class TestCaseExecutionEngine:
    """Test case execution engine - orchestrates step-by-step execution"""

    def __init__(self, db: Session):
        self.db = db
        self.debug_engine = DebugEngine(db)
        self.execution_service = ExecutionService(db)
        self.variable_manager = VariableManager()
        self.assertion_engine = AssertionEngine(self.variable_manager, ExtractorEngine())

    def _map_variable_scope(self, frontend_scope: str) -> str:
        scope_map = {
            "temp": "temp",
            "module": "module",
            "env": "env",
            "global": "global",
        }
        return scope_map.get(frontend_scope, "temp")

    async def execute_test_case(
        self,
        test_case_id: int,
        environment_id: int,
        fail_strategy: str = "stop",
        save_record: bool = True,
        timeout: int = 600000,
        step_interval: int = 0,
        executor_id: Optional[int] = None,
        executor_name: Optional[str] = None,
        debug_mode: bool = False,
        existing_record_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute a test case with all its steps.

        Args:
            test_case_id: Test case ID
            environment_id: Environment ID for execution
            fail_strategy: "stop" or "continue" on step failure
            save_record: Whether to save execution record
            timeout: Overall timeout in milliseconds
            step_interval: Interval between steps in milliseconds
            executor_id: User ID of executor
            executor_name: User name of executor
            debug_mode: Whether running in debug mode

        Returns:
            Execution result dictionary
        """
        logger.info(f"Starting test case execution: test_case_id={test_case_id}, environment_id={environment_id}, fail_strategy={fail_strategy}, debug_mode={debug_mode}")
        test_case = self._load_test_case(test_case_id)
        if not test_case:
            logger.error(f"Test case not found: test_case_id={test_case_id}")
            return {"status": "error", "error_message": f"Test case {test_case_id} not found"}

        from app.services.test_case_service import TestCaseService
        step_tree = TestCaseService.build_step_tree(test_case.steps)

        if not step_tree:
            logger.warning(f"No enabled steps to execute for test_case_id={test_case_id}")
            return {"status": "skipped", "error_message": "No enabled steps to execute"}

        self.variable_manager.clear_scope("request")
        self.variable_manager.clear_scope("test_case")

        if test_case.variables:
            logger.debug(f"Loading case variables for test_case_id={test_case_id}")
            self._load_case_variables(test_case.variables)

        execution_record = None
        if save_record:
            if existing_record_id:
                from app.models.execution_record import ExecutionRecord
                execution_record = self.db.query(ExecutionRecord).filter(ExecutionRecord.id == existing_record_id).first()
                if execution_record:
                    execution_record.status = "running"
                    execution_record.start_time = datetime.now()
                    self.db.commit()
                    self.db.refresh(execution_record)
                    logger.info(f"Using existing execution record: id={existing_record_id}")
            if not execution_record:
                execution_record = self._create_execution_record(
                    test_case, environment_id, executor_id, executor_name, debug_mode
                )

        context = {
            "environment_id": environment_id,
            "test_case_id": test_case_id,
            "fail_strategy": fail_strategy,
            "step_interval": step_interval,
            "execution_status": "running",
        }

        total_steps = 0
        passed_steps = 0
        failed_steps = 0
        skipped_steps = 0
        step_results = []

        try:
            step_results = await self._execute_step_tree(
                step_tree, context, execution_record, depth=0
            )

            for sr in step_results:
                total_steps += 1
                if sr.get("status") == "passed":
                    passed_steps += 1
                elif sr.get("status") == "skipped":
                    skipped_steps += 1
                else:
                    failed_steps += 1

            if failed_steps > 0:
                execution_status = "failed"
            else:
                execution_status = "passed"

        except Exception as e:
            logger.error(f"Test case execution error: test_case_id={test_case_id}, error={str(e)}", exc_info=True)
            execution_status = "error"
            failed_steps = total_steps - passed_steps - skipped_steps

        result = {
            "test_case_id": test_case_id,
            "test_case_name": test_case.name,
            "environment_id": environment_id,
            "status": execution_status,
            "total_steps": total_steps,
            "passed_steps": passed_steps,
            "failed_steps": failed_steps,
            "skipped_steps": skipped_steps,
            "step_results": step_results,
            "variables_snapshot": self.variable_manager.get_all("test_case"),
            "debug_mode": debug_mode,
        }

        if execution_record:
            self._finalize_execution_record(
                execution_record.id, execution_status,
                total_steps, passed_steps, failed_steps, skipped_steps,
                None if execution_status != "error" else "Execution error"
            )
            result["execution_id"] = execution_record.id

        logger.info(f"Test case execution completed: test_case_id={test_case_id}, status={execution_status}, total={total_steps}, passed={passed_steps}, failed={failed_steps}, skipped={skipped_steps}")
        return result

    async def _execute_step_tree(self, steps, context, execution_record, depth=0):
        logger.debug(f"Executing step tree: depth={depth}, step_count={len(steps)}")
        step_results = []
        for step in steps:
            if not step.get("enabled", True):
                logger.debug(f"Skipping disabled step: step_id={step.get('id')}, step_name={step.get('step_name')}")
                step_results.append(self._skip_step_dict(step, "Step disabled"))
                continue
            if context.get("execution_status") == "failed" and context.get("fail_strategy") == "stop":
                logger.debug(f"Skipping step due to previous failure and stop strategy: step_id={step.get('id')}")
                step_results.append(self._skip_step_dict(step, "Previous step failed and fail strategy is stop"))
                continue
            step_type = step.get("step_type", "api")
            if step_type == "api":
                result = await self._execute_api_step(step, context, execution_record)
                step_results.append(result)
            elif step_type == "if":
                result = await self._execute_if_step(step, context, execution_record, depth)
                step_results.append(result)
            elif step_type == "for":
                result = await self._execute_for_step(step, context, execution_record, depth)
                step_results.append(result)
            elif step_type == "while":
                result = await self._execute_while_step(step, context, execution_record, depth)
                step_results.append(result)
            else:
                logger.warning(f"Unknown step type: {step_type}, step_id={step.get('id')}")
                step_results.append(self._skip_step_dict(step, f"Unknown step type: {step_type}"))

            last_result = step_results[-1]
            if last_result.get("status") not in ("passed", "skipped"):
                if context.get("fail_strategy") == "stop":
                    context["execution_status"] = "failed"

            if context.get("step_interval", 0) > 0:
                await asyncio.sleep(context["step_interval"] / 1000.0)

        return step_results

    async def _execute_api_step(self, step, context, execution_record):
        step_id = step.get("id")
        api_id = step.get("api_id")
        logger.info(f"Executing API step: step_id={step_id}, api_id={api_id}, step_name={step.get('step_name')}")
        step_result = {
            "step_id": step_id,
            "step_name": step.get("step_name") or f"Step {step.get('sort_order', 0)}",
            "step_type": "api",
            "api_id": api_id,
            "status": "pending",
            "assertion_results": None,
            "assertion_summary": None,
            "extracted_variables": {},
            "error_message": None,
            "request_url": None,
            "request_method": None,
            "response_status": None,
            "response_time": None,
        }

        try:
            if not api_id:
                logger.warning(f"API step missing api_id: step_id={step_id}")
                step_result["status"] = "failed"
                step_result["error_message"] = "API ID is required for api step"
                return step_result

            api = self.db.query(ApiDefinition).filter(
                ApiDefinition.id == api_id,
                ApiDefinition.is_deleted == False
            ).first()

            if not api:
                logger.error(f"API definition not found: api_id={api_id}")
                step_result["status"] = "failed"
                step_result["error_message"] = f"API {api_id} not found"
                return step_result

            step_result["api_name"] = api.name

            header_overrides = step.get("override_headers")
            if isinstance(header_overrides, str):
                try:
                    header_overrides = json.loads(header_overrides)
                except json.JSONDecodeError:
                    header_overrides = None

            param_overrides = step.get("override_params")
            if isinstance(param_overrides, str):
                try:
                    param_overrides = json.loads(param_overrides)
                except json.JSONDecodeError:
                    param_overrides = None

            body_overrides = step.get("override_body")
            if isinstance(body_overrides, str):
                try:
                    parsed = json.loads(body_overrides)
                    if isinstance(parsed, dict):
                        body_overrides = json.dumps(parsed, ensure_ascii=False)
                except json.JSONDecodeError:
                    pass

            cookie_overrides = step.get("override_cookies")
            if isinstance(cookie_overrides, str):
                try:
                    cookie_overrides = json.loads(cookie_overrides)
                except json.JSONDecodeError:
                    cookie_overrides = None

            assertions_overrides = step.get("assertions")
            if isinstance(assertions_overrides, str):
                try:
                    assertions_overrides = json.loads(assertions_overrides)
                except json.JSONDecodeError:
                    assertions_overrides = None

            timeout_overrides = step.get("timeout_config")
            if isinstance(timeout_overrides, str):
                try:
                    timeout_overrides = json.loads(timeout_overrides)
                except json.JSONDecodeError:
                    timeout_overrides = None

            pre_script = step.get("pre_script")
            pre_request_actions = None
            if pre_script:
                pre_request_actions = [{
                    "id": "pre_script",
                    "name": "前置脚本",
                    "type": "script",
                    "enabled": True,
                    "config": {
                        "script": pre_script,
                    }
                }]

            post_script = step.get("post_script")
            post_request_actions = None
            if post_script:
                post_request_actions = [{
                    "id": "post_script",
                    "name": "后置脚本",
                    "type": "script",
                    "enabled": True,
                    "config": {
                        "script": post_script,
                    }
                }]

            debug_result = await self.debug_engine.execute(
                api_id=api_id,
                environment_id=context["environment_id"],
                service_id=api.service_id,
                param_overrides=param_overrides,
                header_overrides=header_overrides,
                body_overrides=body_overrides,
                body_type=step.get("override_body_type"),
                cookie_overrides=cookie_overrides,
                pre_request_actions_overrides=pre_request_actions,
                post_request_actions_overrides=post_request_actions,
                assertions_overrides=assertions_overrides,
                timeout_config_overrides=timeout_overrides,
            )

            step_result["request_url"] = debug_result.get("request_url")
            step_result["request_method"] = api.method
            step_result["response_status"] = debug_result.get("status_code")
            step_result["response_time"] = debug_result.get("elapsed_ms")
            step_result["debug_result"] = debug_result
            
            step_result["request_data"] = {
                "method": api.method,
                "url": debug_result.get("request_url"),
                "headers": debug_result.get("request_headers"),
                "body": debug_result.get("request_body"),
            }
            step_result["response_data"] = {
                "status_code": debug_result.get("status_code"),
                "headers": debug_result.get("headers"),
                "body": debug_result.get("body"),
                "duration": debug_result.get("elapsed_ms"),
            }
            if debug_result.get("pre_request_results"):
                step_result["pre_actions"] = debug_result["pre_request_results"]
            if debug_result.get("post_request_results"):
                step_result["post_actions"] = debug_result["post_request_results"]
            if debug_result.get("assertion_results"):
                step_result["assertions"] = debug_result["assertion_results"]

            if debug_result.get("error_message"):
                logger.error(f"API step execution error: step_id={step_id}, error={debug_result['error_message']}")
                step_result["status"] = "error"
                step_result["error_message"] = debug_result["error_message"]
                return step_result

            assertion_results = debug_result.get("assertion_results")
            assertion_summary = debug_result.get("assertion_summary")
            step_result["assertion_results"] = assertion_results
            step_result["assertion_summary"] = assertion_summary

            if assertion_summary and not assertion_summary.get("all_passed", True):
                step_result["status"] = "failed"
                logger.debug(f"Step assertion failed: step_id={step_id}, assertion_summary={assertion_summary}")
                failed_assertions = [
                    a for a in (assertion_results or [])
                    if not a.get("passed", True)
                ]
                if failed_assertions:
                    step_result["error_message"] = "; ".join(
                        a.get("message", "Assertion failed") for a in failed_assertions[:3]
                    )
            else:
                step_result["status"] = "passed"
                logger.debug(f"Step passed: step_id={step_id}, response_status={debug_result.get('status_code')}, response_time={debug_result.get('elapsed_ms')}ms")

            extracted = self._extract_step_variables_from_dict(step, debug_result)
            step_result["extracted_variables"] = extracted
            logger.debug(f"Step extracted variables: step_id={step_id}, variables={list(extracted.keys()) if extracted else 'none'}")

            extractors = step.get("extractors")
            if extractors:
                try:
                    configs = json.loads(extractors) if isinstance(extractors, str) else extractors
                    extractor_list = []
                    for config in configs:
                        if not config.get("enabled", True):
                            continue
                        cfg = config.get("config", {})
                        var_name = cfg.get("target_variable", "")
                        extractor_info = {
                            "variable_name": var_name,
                            "extract_type": cfg.get("extract_type", "jsonpath"),
                            "expression": cfg.get("expression", ""),
                            "source": cfg.get("source", "body"),
                            "default_value": cfg.get("default_value", ""),
                            "value": extracted.get(var_name) if extracted else None,
                            "success": extracted.get(var_name) is not None if extracted else False
                        }
                        extractor_list.append(extractor_info)
                    if extractor_list:
                        step_result["extractors"] = extractor_list
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Failed to process extractors for step result: {str(e)}")

        except Exception as e:
            logger.error(f"Step execution error: step_id={step.get('id')}, error={str(e)}", exc_info=True)
            step_result["status"] = "error"
            step_result["error_message"] = str(e)

        if execution_record:
            step_obj = self._make_step_obj(step)
            self._save_step_record(execution_record.id, step_obj, step_result.get("_step_index", 0), step_result)

        return step_result

    async def _execute_if_step(self, step, context, execution_record, depth=0):
        step_id = step.get("id")
        logger.info(f"Executing IF step: step_id={step_id}, step_name={step.get('step_name')}")
        step_result = {
            "step_id": step_id,
            "step_name": step.get("step_name") or "IF Condition",
            "step_type": "if",
            "api_id": step.get("api_id"),
            "status": "pending",
            "assertion_results": None,
            "assertion_summary": None,
            "extracted_variables": {},
            "error_message": None,
            "children_results": [],
        }

        condition = self._parse_execution_condition(step.get("execution_condition"))
        condition_met = self._evaluate_condition(condition)
        logger.debug(f"IF step condition evaluation: step_id={step_id}, condition_met={condition_met}, condition={condition}")

        if condition_met:
            children = step.get("children", [])
            if children:
                child_results = await self._execute_step_tree(children, context, execution_record, depth + 1)
                step_result["children_results"] = child_results
                child_failed = any(
                    cr.get("status") not in ("passed", "skipped")
                    for cr in child_results
                )
                step_result["status"] = "failed" if child_failed else "passed"
            else:
                step_result["status"] = "passed"
        else:
            step_result["status"] = "skipped"
            step_result["skip_reason"] = "IF condition not met"
            logger.debug(f"IF step skipped - condition not met: step_id={step_id}")

        return step_result

    async def _execute_for_step(self, step, context, execution_record, depth=0):
        step_id = step.get("id")
        logger.info(f"Executing FOR step: step_id={step_id}, step_name={step.get('step_name')}")
        step_result = {
            "step_id": step_id,
            "step_name": step.get("step_name") or "FOR Loop",
            "step_type": "for",
            "api_id": step.get("api_id"),
            "status": "pending",
            "assertion_results": None,
            "assertion_summary": None,
            "extracted_variables": {},
            "error_message": None,
            "children_results": [],
        }

        condition = self._parse_execution_condition(step.get("execution_condition"))
        loop_variable = condition.get("loop_variable", "item")
        loop_count = condition.get("loop_count")
        loop_items = condition.get("loop_items")

        if loop_items and isinstance(loop_items, list):
            items = loop_items
        elif loop_count and isinstance(loop_count, int) and loop_count > 0:
            items = list(range(loop_count))
        else:
            step_result["status"] = "skipped"
            step_result["skip_reason"] = "FOR loop has no items or count"
            logger.warning(f"FOR loop has no items or count: step_id={step_id}")
            return step_result

        children = step.get("children", [])
        if not children:
            step_result["status"] = "passed"
            return step_result

        all_child_results = []
        has_failure = False

        for i, item in enumerate(items):
            logger.debug(f"FOR loop iteration: step_id={step_id}, iteration={i}, loop_variable={loop_variable}")
            self.variable_manager.set(loop_variable, item, "test_case")
            self.variable_manager.set(f"{loop_variable}_index", i, "test_case")

            child_results = await self._execute_step_tree(children, context, execution_record, depth + 1)
            all_child_results.extend(child_results)

            if any(cr.get("status") not in ("passed", "skipped") for cr in child_results):
                has_failure = True
                if context.get("fail_strategy") == "stop":
                    break

        step_result["children_results"] = all_child_results
        step_result["status"] = "failed" if has_failure else "passed"

        return step_result

    async def _execute_while_step(self, step, context, execution_record, depth=0):
        step_id = step.get("id")
        logger.info(f"Executing WHILE step: step_id={step_id}, step_name={step.get('step_name')}")
        step_result = {
            "step_id": step_id,
            "step_name": step.get("step_name") or "WHILE Loop",
            "step_type": "while",
            "api_id": step.get("api_id"),
            "status": "pending",
            "assertion_results": None,
            "assertion_summary": None,
            "extracted_variables": {},
            "error_message": None,
            "children_results": [],
        }

        condition = self._parse_execution_condition(step.get("execution_condition"))
        max_count = condition.get("loop_count", 100)

        children = step.get("children", [])
        if not children:
            step_result["status"] = "passed"
            return step_result

        all_child_results = []
        has_failure = False
        iteration = 0

        while iteration < max_count:
            condition_met = self._evaluate_condition(condition)
            if not condition_met:
                logger.debug(f"WHILE loop condition not met, breaking: step_id={step_id}, iteration={iteration}")
                break

            child_results = await self._execute_step_tree(children, context, execution_record, depth + 1)
            all_child_results.extend(child_results)

            if any(cr.get("status") not in ("passed", "skipped") for cr in child_results):
                has_failure = True
                if context.get("fail_strategy") == "stop":
                    break

            iteration += 1

        logger.debug(f"WHILE loop completed: step_id={step_id}, total_iterations={iteration}")
        step_result["children_results"] = all_child_results
        step_result["status"] = "failed" if has_failure else "passed"

        return step_result

    def _parse_execution_condition(self, condition):
        if not condition:
            return {}
        if isinstance(condition, str):
            try:
                return json.loads(condition)
            except (json.JSONDecodeError, TypeError):
                return {}
        if isinstance(condition, dict):
            return condition
        return {}

    def _evaluate_condition(self, condition):
        if not condition:
            return True
        cond_type = condition.get("type", "none")
        if cond_type == "none":
            return True
        elif cond_type == "expression":
            expression = condition.get("expression", "")
            if not expression:
                return True
            try:
                resolved = self.variable_manager.resolve(expression)
                result = str(resolved).lower() not in ("false", "0", "", "none")
                logger.debug(f"Condition expression evaluation: expression={expression}, resolved={resolved}, result={result}")
                return result
            except Exception as e:
                logger.warning(f"Condition expression evaluation failed: expression={expression}, error={str(e)}")
                return True
        elif cond_type == "script":
            return True
        return True

    def _extract_step_variables_from_dict(
        self,
        step: Dict[str, Any],
        debug_result: Dict[str, Any],
    ) -> Dict[str, str]:
        logger.debug(f"Extracting step variables: step_id={step.get('id')}")
        extracted = {}
        extractors = step.get("extractors")
        if isinstance(extractors, str):
            try:
                extractors = json.loads(extractors)
            except json.JSONDecodeError:
                return extracted

        if not extractors:
            return extracted

        response_data = {
            "status_code": debug_result.get("status_code"),
            "headers": debug_result.get("headers", {}),
            "body": debug_result.get("body", ""),
            "cookies": debug_result.get("cookies", {}),
            "url": debug_result.get("request_url", ""),
        }

        extractor_engine = ExtractorEngine()
        for ext_config in extractors:
            if not ext_config.get("enabled", True):
                continue
            
            config_dict = ext_config.get("config", {})
            target_variable = config_dict.get("target_variable", "")
            default_value = config_dict.get("default_value", "")
            
            if not target_variable:
                continue
                
            try:
                from app.services.extractors.base_extractor import ExtractConfig
                config = ExtractConfig(
                    extract_type=config_dict.get("extract_type") or config_dict.get("type", "jsonpath"),
                    expression=config_dict.get("expression", ""),
                    source=config_dict.get("source", "body"),
                    default_value=config_dict.get("default_value", ""),
                )
                source = config.source or "body"
                result = extractor_engine.extract_from_response(response_data, source, config)
                
                if result.success:
                    extracted[target_variable] = result.value
                    logger.debug(f"Variable extracted successfully: variable={target_variable}, value={result.value}, scope={self._map_variable_scope(config_dict.get('target_scope', 'temp'))}")
                    scope = self._map_variable_scope(config_dict.get("target_scope", "temp"))
                    self.variable_manager.set(target_variable, result.value, scope)
                else:
                    extracted[target_variable] = default_value if default_value else None
                    logger.warning(f"Variable extraction failed, using default: variable={target_variable}, default_value={default_value}")
                    if default_value:
                        scope = self._map_variable_scope(config_dict.get("target_scope", "temp"))
                        self.variable_manager.set(target_variable, default_value, scope)
                    
            except Exception as e:
                logger.warning(f"Variable extraction failed for extractor {target_variable}: {str(e)}")
                extracted[target_variable] = default_value if default_value else None
                if default_value:
                    scope = self._map_variable_scope(config_dict.get("target_scope", "temp"))
                    self.variable_manager.set(target_variable, default_value, scope)

        logger.debug(f"Step variable extraction completed: step_id={step.get('id')}, extracted_count={len(extracted)}")
        return extracted

    def _load_test_case(self, test_case_id: int) -> Optional[TestCase]:
        """Load test case with steps. Returns a detached copy to avoid SQLAlchemy tracking issues."""
        logger.debug(f"Loading test case: test_case_id={test_case_id}")
        from sqlalchemy.orm import joinedload
        test_case = self.db.query(TestCase).options(
            joinedload(TestCase.steps).joinedload(TestCaseStep.api)
        ).filter(TestCase.id == test_case_id).first()

        if test_case:
            from app.services.test_case_service import TestCaseService
            service = TestCaseService(self.db)
            test_case = service._convert_test_case(test_case)
            self.db.expunge(test_case)

        return test_case

    def _load_case_variables(self, variables: Any):
        """Load test case level variables into variable manager."""
        logger.debug(f"Loading case variables: type={type(variables).__name__}")
        if isinstance(variables, str):
            try:
                variables = json.loads(variables)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse case variables JSON")
                return

        if isinstance(variables, list):
            for var in variables:
                if isinstance(var, dict) and "key" in var and "value" in var:
                    self.variable_manager.set(var["key"], var["value"], "scenario")
            logger.debug(f"Loaded {len(variables)} case variables")

    def _check_execution_condition(self, condition: Any) -> bool:
        """Check if a step should be executed based on its condition."""
        if not condition:
            return True

        if isinstance(condition, str):
            try:
                condition = json.loads(condition)
            except json.JSONDecodeError:
                return True

        if isinstance(condition, dict):
            cond_type = condition.get("type", "none")
            if cond_type == "none":
                return True
            elif cond_type == "expression":
                expression = condition.get("expression", "")
                if not expression:
                    return True
                try:
                    resolved = self.variable_manager.resolve(expression)
                    return str(resolved).lower() not in ("false", "0", "", "none")
                except Exception:
                    return True
            elif cond_type == "script":
                return True

        return True

    def _skip_step(self, step: TestCaseStep, reason: str) -> Dict[str, Any]:
        """Create a skipped step result."""
        return {
            "step_id": step.id,
            "step_name": step.step_name or f"Step {step.sort_order}",
            "step_type": getattr(step, "step_type", "api") or "api",
            "api_id": step.api_id,
            "status": "skipped",
            "skip_reason": reason,
            "assertion_results": None,
            "assertion_summary": None,
            "extracted_variables": {},
            "error_message": None,
        }

    def _skip_step_dict(self, step: Dict[str, Any], reason: str) -> Dict[str, Any]:
        return {
            "step_id": step.get("id"),
            "step_name": step.get("step_name") or f"Step {step.get('sort_order', 0)}",
            "step_type": step.get("step_type", "api"),
            "api_id": step.get("api_id"),
            "status": "skipped",
            "skip_reason": reason,
            "assertion_results": None,
            "assertion_summary": None,
            "extracted_variables": {},
            "error_message": None,
        }

    def _make_step_obj(self, step: Dict[str, Any]):
        class StepProxy:
            pass
        obj = StepProxy()
        obj.id = step.get("id")
        obj.test_case_id = step.get("test_case_id")
        obj.step_type = step.get("step_type", "api")
        obj.api_id = step.get("api_id")
        obj.parent_step_id = step.get("parent_step_id")
        obj.step_name = step.get("step_name")
        obj.sort_order = step.get("sort_order", 0)
        obj.enabled = step.get("enabled", True)
        obj.override_headers = step.get("override_headers")
        obj.override_params = step.get("override_params")
        obj.override_body = step.get("override_body")
        obj.override_body_type = step.get("override_body_type")
        obj.override_cookies = step.get("override_cookies")
        obj.assertions = step.get("assertions")
        obj.extractors = step.get("extractors")
        obj.pre_script = step.get("pre_script")
        obj.post_script = step.get("post_script")
        obj.timeout_config = step.get("timeout_config")
        obj.execution_condition = step.get("execution_condition")
        return obj

    def create_execution_record(
        self,
        test_case_id: int,
        environment_id: int,
        executor_id: int = 0,
    ):
        test_case = self._load_test_case(test_case_id)
        if not test_case:
            raise ValueError(f"Test case {test_case_id} not found")
        from app.models.environment import Environment
        env = self.db.query(Environment).filter(Environment.id == environment_id).first()
        env_name = env.name if env else None
        return self.execution_service.create_execution_record(
            team_id=test_case.team_id,
            test_case_id=test_case.id,
            test_case_name=test_case.name,
            environment_id=environment_id,
            environment_name=env_name,
            execution_type="manual",
            executor_id=executor_id,
            executor_name=None,
        )

    def _create_execution_record(
        self,
        test_case: TestCase,
        environment_id: int,
        executor_id: Optional[int],
        executor_name: Optional[str],
        debug_mode: bool,
    ) -> TestCaseExecutionRecord:
        """Create execution record in database."""
        logger.info(f"Creating execution record: test_case_id={test_case.id}, environment_id={environment_id}, debug_mode={debug_mode}")
        from app.models.environment import Environment
        env = self.db.query(Environment).filter(Environment.id == environment_id).first()
        env_name = env.name if env else None

        return self.execution_service.create_execution_record(
            team_id=test_case.team_id,
            test_case_id=test_case.id,
            test_case_name=test_case.name,
            environment_id=environment_id,
            environment_name=env_name,
            execution_type="debug" if debug_mode else "manual",
            executor_id=executor_id,
            executor_name=executor_name,
        )

    def _save_step_record(
        self,
        execution_id: int,
        step: TestCaseStep,
        step_index: int,
        step_result: Dict[str, Any],
    ):
        """Save step execution record to database."""
        api_name = None
        if step.api_id:
            api = self.db.query(ApiDefinition).filter(ApiDefinition.id == step.api_id).first()
            if api:
                api_name = api.name

        step_record = self.execution_service.create_step_execution_record(
            case_execution_id=execution_id,
            step_id=step.id,
            step_name=step_result.get("step_name"),
            step_order=step_index + 1,
            api_id=step.api_id,
            api_name=api_name,
            status=step_result.get("status", "pending"),
        )

        update_kwargs = {}
        if step_result.get("request_url"):
            update_kwargs["request_url"] = step_result["request_url"]
        if step_result.get("request_method"):
            update_kwargs["request_method"] = step_result["request_method"]
        if step_result.get("response_status"):
            update_kwargs["response_status"] = step_result["response_status"]
        if step_result.get("response_time"):
            update_kwargs["response_time"] = step_result["response_time"]
        if step_result.get("error_message"):
            update_kwargs["error_message"] = step_result["error_message"]
        if step_result.get("skip_reason"):
            update_kwargs["skip_reason"] = step_result["skip_reason"]
        if step_result.get("assertion_results"):
            update_kwargs["assertions"] = json.dumps(
                step_result["assertion_results"], ensure_ascii=False
            )
        
        extracted_variables = step_result.get("extracted_variables", {})
        if extracted_variables or step.extractors:
            extractor_configs = []
            if step.extractors:
                try:
                    configs = json.loads(step.extractors) if isinstance(step.extractors, str) else step.extractors
                    logger.info(f"Processing extractors: {configs}")
                    for config in configs:
                        if not config.get("enabled", True):
                            continue
                        cfg = config.get("config", {})
                        var_name = cfg.get("target_variable", "")
                        extractor_info = {
                            "variable_name": var_name,
                            "extract_type": cfg.get("extract_type", "jsonpath"),
                            "expression": cfg.get("expression", ""),
                            "source": cfg.get("source", "body"),
                            "default_value": cfg.get("default_value", ""),
                            "value": extracted_variables.get(var_name) if extracted_variables else None,
                            "success": extracted_variables.get(var_name) is not None if extracted_variables else False
                        }
                        logger.info(f"Extractor info: {extractor_info}")
                        extractor_configs.append(extractor_info)
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Failed to process extractors: {str(e)}")
                    pass
            
            logger.info(f"Final extractor_configs: {extractor_configs}, extracted_variables: {extracted_variables}")
            if extractor_configs:
                update_kwargs["extractors"] = json.dumps(
                    extractor_configs, ensure_ascii=False
                )
            elif extracted_variables:
                update_kwargs["extractors"] = json.dumps(
                    extracted_variables, ensure_ascii=False
                )

        debug_result = step_result.get("debug_result")
        if debug_result:
            if debug_result.get("request_headers"):
                update_kwargs["request_headers"] = json.dumps(
                    debug_result["request_headers"], ensure_ascii=False
                ) if isinstance(debug_result["request_headers"], dict) else debug_result["request_headers"]
            if debug_result.get("request_body"):
                body = debug_result.get("request_body", "")
                update_kwargs["request_body"] = body[:50000] if body else None
            if debug_result.get("body") and step_result.get("status") != "skipped":
                body = debug_result.get("body", "")
                update_kwargs["response_body"] = body[:50000] if body else None
            if debug_result.get("headers"):
                update_kwargs["response_headers"] = json.dumps(
                    debug_result["headers"], ensure_ascii=False
                ) if isinstance(debug_result["headers"], dict) else debug_result["headers"]
            if debug_result.get("pre_request_results"):
                update_kwargs["pre_actions"] = json.dumps(
                    debug_result["pre_request_results"], ensure_ascii=False
                )
            if debug_result.get("post_request_results"):
                update_kwargs["post_actions"] = json.dumps(
                    debug_result["post_request_results"], ensure_ascii=False
                )

        if update_kwargs:
            self.execution_service.update_step_execution_record(
                step_execution_id=step_record.id, **update_kwargs
            )

    def _finalize_execution_record(
        self,
        execution_id: int,
        status: str,
        total_steps: int,
        passed_steps: int,
        failed_steps: int,
        skipped_steps: int,
        error_message: Optional[str],
    ):
        """Update execution record with final results."""
        logger.info(f"Finalizing execution record: execution_id={execution_id}, status={status}, total={total_steps}, passed={passed_steps}, failed={failed_steps}, skipped={skipped_steps}")
        self.execution_service.update_execution_record(
            execution_id=execution_id,
            status=status,
            total_steps=total_steps,
            passed_steps=passed_steps,
            failed_steps=failed_steps,
            skipped_steps=skipped_steps,
            error_message=error_message,
        )
