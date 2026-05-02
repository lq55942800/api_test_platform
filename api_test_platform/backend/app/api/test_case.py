"""
Test Case API Routes - CRUD, Execution, Debug and Cross Team Copy
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import asyncio
import json

from app.core.logging import get_logger
from app.db.session import get_db
from app.schemas.test_case import (
    TestCaseCreate,
    TestCaseUpdate,
    TestCaseResponse,
    CrossTeamCopyRequest,
    CrossTeamCopyCheckResponse,
    TestCaseExecuteRequest,
)
from app.services.test_case_service import TestCaseService
from app.services.test_case_execution_engine import TestCaseExecutionEngine

logger = get_logger(__name__)

router = APIRouter(prefix="/test-cases", tags=["Test Cases"])


@router.get("/", response_model=List[TestCaseResponse])
def get_test_cases(
    team_id: Optional[int] = Query(None, description="Filter by team ID"),
    module_id: Optional[int] = Query(None, description="Filter by module ID"),
    status: Optional[str] = Query(None, description="Filter by status (enabled/disabled)"),
    keyword: Optional[str] = Query(None, description="Search keyword"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get test cases list with optional filtering and pagination
    """
    logger.info(f"查询测试用例列表: team_id={team_id}, module_id={module_id}, status={status}, keyword={keyword}, priority={priority}, skip={skip}, limit={limit}")
    try:
        service = TestCaseService(db)
        test_cases = service.get_test_cases(
            team_id=team_id,
            module_id=module_id,
            status=status,
            keyword=keyword,
            priority=priority,
            skip=skip,
            limit=limit
        )
        logger.info(f"查询测试用例列表成功: team_id={team_id}, count={len(test_cases)}")
        return test_cases
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询测试用例列表失败: team_id={team_id}, error={str(e)}")
        raise


@router.post("/", response_model=TestCaseResponse, status_code=201)
def create_test_case(
    test_case_data: TestCaseCreate,
    team_id: int = Query(..., description="Team ID"),
    user_id: int = Query(..., description="Creator user ID"),
    db: Session = Depends(get_db)
):
    """
    Create a new test case with steps
    """
    logger.info(f"创建测试用例: team_id={team_id}, user_id={user_id}, name={test_case_data.name}")
    try:
        service = TestCaseService(db)
        test_case = service.create_test_case(
            test_case_data=test_case_data,
            team_id=team_id,
            user_id=user_id
        )
        logger.info(f"测试用例创建成功: test_case_id={test_case.id}, name={test_case_data.name}")
        return test_case
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建测试用例失败: team_id={team_id}, name={test_case_data.name}, error={str(e)}")
        raise


@router.get("/{test_case_id}", response_model=TestCaseResponse)
def get_test_case(
    test_case_id: int,
    db: Session = Depends(get_db)
):
    """Get test case by ID"""
    logger.info(f"查询测试用例详情: test_case_id={test_case_id}")
    try:
        service = TestCaseService(db)
        test_case = service.get_test_case(test_case_id)
        if not test_case:
            logger.warning(f"测试用例不存在: test_case_id={test_case_id}")
            raise HTTPException(status_code=404, detail="Test case not found")
        return test_case
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询测试用例详情失败: test_case_id={test_case_id}, error={str(e)}")
        raise


@router.put("/{test_case_id}", response_model=TestCaseResponse)
def update_test_case(
    test_case_id: int,
    test_case_data: TestCaseUpdate,
    user_id: int = Query(..., description="User ID performing the update"),
    db: Session = Depends(get_db)
):
    """
    Update test case and its steps
    """
    logger.info(f"更新测试用例: test_case_id={test_case_id}, user_id={user_id}")
    try:
        service = TestCaseService(db)
        test_case = service.update_test_case(
            test_case_id=test_case_id,
            test_case_data=test_case_data,
            user_id=user_id
        )
        logger.info(f"测试用例更新成功: test_case_id={test_case_id}")
        return test_case
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新测试用例失败: test_case_id={test_case_id}, error={str(e)}")
        raise


@router.delete("/{test_case_id}")
def delete_test_case(
    test_case_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete test case and all its steps
    """
    logger.info(f"删除测试用例: test_case_id={test_case_id}")
    try:
        service = TestCaseService(db)
        result = service.delete_test_case(test_case_id)
        logger.info(f"测试用例删除成功: test_case_id={test_case_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除测试用例失败: test_case_id={test_case_id}, error={str(e)}")
        raise


@router.post("/{test_case_id}/execute")
async def execute_test_case(
    test_case_id: int,
    execute_request: TestCaseExecuteRequest,
    user_id: int = Query(0, description="Executor user ID"),
    db: Session = Depends(get_db)
):
    logger.info(f"执行测试用例(SSE): test_case_id={test_case_id}, user_id={user_id}, environment_id={execute_request.environment_id}")

    async def event_stream():
        from app.db.session import SessionLocal
        stream_db = SessionLocal()
        try:
            engine = TestCaseExecutionEngine(stream_db)
            execution_record = engine.create_execution_record(
                test_case_id=test_case_id,
                environment_id=execute_request.environment_id,
                executor_id=user_id,
            )
            yield f"data: {json.dumps({'type': 'started', 'execution_id': execution_record.id, 'status': 'running'}, ensure_ascii=False)}\n\n"

            test_case = engine._load_test_case(test_case_id)
            if not test_case:
                yield f"data: {json.dumps({'type': 'error', 'message': f'Test case {test_case_id} not found'}, ensure_ascii=False)}\n\n"
                return

            from app.services.test_case_service import TestCaseService
            step_tree = TestCaseService.build_step_tree(test_case.steps)
            if not step_tree:
                yield f"data: {json.dumps({'type': 'completed', 'execution_id': execution_record.id, 'status': 'skipped', 'message': 'No enabled steps'}, ensure_ascii=False)}\n\n"
                return

            engine.variable_manager.clear_scope("request")
            engine.variable_manager.clear_scope("test_case")
            if test_case.variables:
                engine._load_case_variables(test_case.variables)

            context = {
                "environment_id": execute_request.environment_id,
                "test_case_id": test_case_id,
                "fail_strategy": execute_request.fail_strategy,
                "step_interval": execute_request.step_interval,
                "execution_status": "running",
            }

            total_steps = 0
            passed_steps = 0
            failed_steps = 0
            skipped_steps = 0

            try:
                step_results = await engine._execute_step_tree(
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
                    step_data = {
                        "type": "step",
                        "step_index": total_steps,
                        "step_name": sr.get("step_name", ""),
                        "status": sr.get("status", "unknown"),
                        "duration": sr.get("duration"),
                        "error": sr.get("error_message"),
                    }
                    yield f"data: {json.dumps(step_data, ensure_ascii=False)}\n\n"
            except Exception as e:
                logger.error(f"SSE执行步骤异常: test_case_id={test_case_id}, error={str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

            final_status = "passed" if failed_steps == 0 else "failed"
            engine._finalize_execution_record(
                execution_record.id, final_status, total_steps, passed_steps, failed_steps, skipped_steps, None
            )

            yield f"data: {json.dumps({'type': 'completed', 'execution_id': execution_record.id, 'status': final_status, 'total_steps': total_steps, 'passed_steps': passed_steps, 'failed_steps': failed_steps, 'skipped_steps': skipped_steps}, ensure_ascii=False)}\n\n"
        except Exception as e:
            logger.error(f"SSE流异常: test_case_id={test_case_id}, error={str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
        finally:
            stream_db.close()

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/{test_case_id}/debug")
async def debug_test_case(
    test_case_id: int,
    execute_request: TestCaseExecuteRequest,
    user_id: int = Query(0, description="Executor user ID"),
    db: Session = Depends(get_db)
):
    """
    Debug a test case

    Similar to execute but runs in debug mode:
    - Does not save execution record by default
    - Returns detailed debug information for each step
    - Includes request/response details
    """
    logger.info(f"调试测试用例: test_case_id={test_case_id}, user_id={user_id}, environment_id={execute_request.environment_id}")
    try:
        engine = TestCaseExecutionEngine(db)
        result = await engine.execute_test_case(
            test_case_id=test_case_id,
            environment_id=execute_request.environment_id,
            fail_strategy=execute_request.fail_strategy,
            save_record=execute_request.save_record if execute_request.save_record else False,
            timeout=execute_request.timeout,
            step_interval=execute_request.step_interval,
            executor_id=user_id,
            debug_mode=True,
        )
        logger.info(f"测试用例调试完成: test_case_id={test_case_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"调试测试用例失败: test_case_id={test_case_id}, error={str(e)}")
        raise


@router.post("/{test_case_id}/copy")
def copy_test_case(
    test_case_id: int,
    user_id: int = Query(0, description="User ID performing the copy"),
    db: Session = Depends(get_db)
):
    """
    Copy a test case within the same team

    Creates a duplicate of the test case with all steps in the same team.
    """
    logger.info(f"复制测试用例: test_case_id={test_case_id}, user_id={user_id}")
    try:
        service = TestCaseService(db)
        test_case = service.get_test_case(test_case_id)
        if not test_case:
            logger.warning(f"测试用例不存在: test_case_id={test_case_id}")
            raise HTTPException(status_code=404, detail="Test case not found")

        from app.schemas.test_case import TestCaseCreate as TCCreate
        from app.schemas.test_case import TestCaseStepCreate as StepCreate

        steps_data = []
        if test_case.steps:
            for step in test_case.steps:
                steps_data.append(StepCreate(
                    step_type=getattr(step, "step_type", "api") or "api",
                    api_id=step.api_id,
                    parent_step_id=getattr(step, "parent_step_id", None),
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
                    execution_condition=step.execution_condition,
                ))

        new_case_data = TCCreate(
            name=f"{test_case.name} (副本)",
            module_id=test_case.module_id,
            description=test_case.description,
            status=test_case.status,
            priority=test_case.priority,
            tags=test_case.tags,
            variables=test_case.variables,
            steps=steps_data,
        )

        new_case = service.create_test_case(
            test_case_data=new_case_data,
            team_id=test_case.team_id,
            user_id=user_id,
        )
        logger.info(f"测试用例复制成功: source_id={test_case_id}, new_id={new_case.id}")
        return new_case
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"复制测试用例失败: test_case_id={test_case_id}, error={str(e)}")
        raise


@router.post("/{test_case_id}/check-copy", response_model=CrossTeamCopyCheckResponse)
def check_cross_team_copy(
    test_case_id: int,
    target_team_id: int = Query(..., description="Target team ID"),
    db: Session = Depends(get_db)
):
    """
    Check cross-team copy compatibility
    """
    logger.info(f"检查跨团队复制兼容性: test_case_id={test_case_id}, target_team_id={target_team_id}")
    try:
        service = TestCaseService(db)
        result = service.check_cross_team_copy(test_case_id, target_team_id)

        logger.info(f"跨团队复制兼容性检查完成: test_case_id={test_case_id}, can_copy={result['can_copy']}")
        return CrossTeamCopyCheckResponse(
            can_copy=result["can_copy"],
            warnings=result["warnings"],
            services_to_check=result["services_to_check"],
            variables_to_check=result["variables_to_check"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"检查跨团队复制兼容性失败: test_case_id={test_case_id}, target_team_id={target_team_id}, error={str(e)}")
        raise


@router.post("/{test_case_id}/copy-to-team", response_model=dict)
def copy_to_team(
    test_case_id: int,
    request: CrossTeamCopyRequest,
    user_id: int = Query(..., description="User ID performing the copy"),
    db: Session = Depends(get_db)
):
    """
    Execute cross-team copy
    """
    logger.info(f"执行跨团队复制: test_case_id={test_case_id}, target_team_id={request.target_team_id}, user_id={user_id}")
    try:
        service = TestCaseService(db)
        result = service.copy_to_team(
            test_case_id=test_case_id,
            target_team_id=request.target_team_id,
            user_id=user_id,
            copy_options=request.copy_options
        )
        logger.info(f"跨团队复制成功: test_case_id={test_case_id}, target_team_id={request.target_team_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"跨团队复制失败: test_case_id={test_case_id}, target_team_id={request.target_team_id}, error={str(e)}")
        raise
