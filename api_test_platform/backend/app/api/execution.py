"""
执行记录API路由
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.session import get_db
from app.schemas.execution import (
    TestCaseExecutionRecordResponse,
    StepExecutionRecordResponse,
    ExecutionExportRequest,
)
from app.services.execution_service import ExecutionService
from app.models.execution_record import TestCaseExecutionRecord, StepExecutionRecord

# 配置日志
logger = get_logger(__name__)

router = APIRouter(tags=["Execution Records"])


@router.get("/test-cases/{test_case_id}/executions")
def list_executions(
    test_case_id: int,
    status: Optional[str] = Query(None, description="执行状态筛选"),
    executor_id: Optional[int] = Query(None, description="执行人筛选"),
    start_date: Optional[datetime] = Query(None, description="开始日期筛选"),
    end_date: Optional[datetime] = Query(None, description="结束日期筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    获取测试用例的执行记录列表

    - **test_case_id**: 测试用例ID
    - **status**: 执行状态筛选 (running/passed/failed/skipped)
    - **executor_id**: 执行人ID筛选
    - **start_date**: 创建时间起始日期
    - **end_date**: 创建时间结束日期
    - **page**: 页码
    - **page_size**: 每页数量
    """
    try:
        logger.info(f"查询执行记录列表: test_case_id={test_case_id}, status={status}, page={page}")
        
        service = ExecutionService(db)
        items, total = service.get_execution_list(
            test_case_id=test_case_id,
            status=status,
            executor_id=executor_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
        )

        logger.info(f"查询成功: test_case_id={test_case_id}, total={total}")
        
        return {
            "items": [
                TestCaseExecutionRecordResponse.model_validate(item) for item in items
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询执行记录列表失败: test_case_id={test_case_id}, error={str(e)}")
        raise HTTPException(status_code=500, detail=f"查询执行记录列表失败: {str(e)}")


@router.get("/executions/{execution_id}")
def get_execution_detail(
    execution_id: int,
    db: Session = Depends(get_db)
):
    """
    获取执行记录详情

    - **execution_id**: 执行记录ID
    """
    try:
        logger.info(f"查询执行记录详情: execution_id={execution_id}")
        
        service = ExecutionService(db)
        detail = service.get_execution_detail(execution_id)

        if not detail:
            logger.warning(f"执行记录不存在: execution_id={execution_id}")
            raise HTTPException(status_code=404, detail="执行记录不存在")

        execution = detail.get("execution")
        steps = detail.get("steps", [])
        
        # 空值检查
        if not execution:
            logger.error(f"执行记录数据为空: execution_id={execution_id}")
            raise HTTPException(status_code=404, detail="执行记录数据为空")

        response_data = TestCaseExecutionRecordResponse.model_validate(execution)
        response_dict = response_data.model_dump()
        response_dict["steps"] = [
            StepExecutionRecordResponse.model_validate(step) for step in steps
        ]

        logger.info(f"查询成功: execution_id={execution_id}")
        return response_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询执行记录详情失败: execution_id={execution_id}, error={str(e)}")
        raise HTTPException(status_code=500, detail=f"查询执行记录详情失败: {str(e)}")


@router.get("/executions/{execution_id}/export")
def export_execution_report(
    execution_id: int,
    format: str = Query("html", description="导出格式: html, excel"),
    include_request: bool = Query(True, description="包含请求详情"),
    include_response: bool = Query(True, description="包含响应详情"),
    db: Session = Depends(get_db)
):
    """
    导出执行报告

    - **execution_id**: 执行记录ID
    - **format**: 导出格式 (html/excel)
    - **include_request**: 是否包含请求详情
    - **include_response**: 是否包含响应详情
    """
    try:
        logger.info(f"导出执行报告: execution_id={execution_id}, format={format}")
        
        service = ExecutionService(db)
        result = service.export_execution_report(
            execution_id=execution_id,
            format=format,
            include_request=include_request,
            include_response=include_response,
        )

        if format == "html":
            logger.info(f"HTML报告导出成功: execution_id={execution_id}")
            return Response(
                content=result["content"],
                media_type="text/html; charset=utf-8",
                headers={
                    "Content-Disposition": f'attachment; filename="{result["filename"]}"'
                }
            )
        elif format == "excel":
            logger.info(f"Excel报告导出成功: execution_id={execution_id}")
            return Response(
                content=result["content"],
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": f'attachment; filename="{result["filename"]}"'
                }
            )
        else:
            logger.warning(f"不支持的导出格式: {format}")
            raise HTTPException(status_code=400, detail=f"不支持的导出格式: {format}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出执行报告失败: execution_id={execution_id}, error={str(e)}")
        raise HTTPException(status_code=500, detail=f"导出执行报告失败: {str(e)}")


@router.get("/executions/{execution_id}/steps")
def list_step_executions(
    execution_id: int,
    db: Session = Depends(get_db)
):
    """
    获取执行记录的步骤执行详情

    - **execution_id**: 执行记录ID
    """
    try:
        service = ExecutionService(db)
        detail = service.get_execution_detail(execution_id)

        if not detail:
            raise HTTPException(status_code=404, detail="执行记录不存在")

        steps = detail.get("steps", [])
        return [StepExecutionRecordResponse.model_validate(step) for step in steps]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询步骤执行记录失败: execution_id={execution_id}, error={str(e)}")
        raise HTTPException(status_code=500, detail=f"查询步骤执行记录失败: {str(e)}")


@router.post("/executions/{execution_id}/stop")
def stop_execution(
    execution_id: int,
    db: Session = Depends(get_db)
):
    """
    停止执行中的测试用例

    - **execution_id**: 执行记录ID
    """
    try:
        service = ExecutionService(db)
        result = service.stop_execution(execution_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"停止执行失败: execution_id={execution_id}, error={str(e)}")
        raise HTTPException(status_code=500, detail=f"停止执行失败: {str(e)}")


@router.post("/executions/{execution_id}/steps/{step_id}/retry")
async def retry_step(
    execution_id: int,
    step_id: int,
    db: Session = Depends(get_db)
):
    """
    重试单个步骤

    - **execution_id**: 执行记录ID
    - **step_id**: 步骤执行记录ID
    """
    try:
        service = ExecutionService(db)
        
        step_record = db.query(StepExecutionRecord).filter(
            StepExecutionRecord.id == step_id,
            StepExecutionRecord.case_execution_id == execution_id
        ).first()
        
        if not step_record:
            raise HTTPException(status_code=404, detail="步骤执行记录不存在")
        
        if not step_record.api_id:
            raise HTTPException(status_code=400, detail="该步骤没有关联API，无法重试")
        
        execution = db.query(TestCaseExecutionRecord).filter(
            TestCaseExecutionRecord.id == execution_id
        ).first()
        
        if not execution:
            raise HTTPException(status_code=404, detail="执行记录不存在")
        
        from app.services.debug_engine import DebugEngine
        
        debug_engine = DebugEngine(db)
        debug_result = await debug_engine.execute(
            api_id=step_record.api_id,
            environment_id=execution.environment_id,
        )
        
        new_status = "passed"
        error_message = None
        
        if debug_result.get("error_message"):
            new_status = "error"
            error_message = debug_result["error_message"]
        elif debug_result.get("assertion_summary"):
            if not debug_result["assertion_summary"].get("all_passed", True):
                new_status = "failed"
                failed_assertions = [
                    a for a in (debug_result.get("assertion_results") or [])
                    if not a.get("passed", True)
                ]
                if failed_assertions:
                    error_message = "; ".join(
                        a.get("message", "Assertion failed") for a in failed_assertions[:3]
                    )
        
        step_record.status = new_status
        step_record.error_message = error_message
        step_record.response_status = debug_result.get("status_code")
        step_record.response_time = debug_result.get("elapsed_ms")
        step_record.request_url = debug_result.get("request_url")
        
        if debug_result.get("headers"):
            import json
            step_record.response_headers = json.dumps(debug_result["headers"], ensure_ascii=False)
        if debug_result.get("body"):
            step_record.response_body = debug_result["body"][:50000] if debug_result["body"] else None
        if debug_result.get("request_headers"):
            import json
            step_record.request_headers = json.dumps(debug_result["request_headers"], ensure_ascii=False)
        if debug_result.get("request_body"):
            step_record.request_body = debug_result["request_body"][:50000] if debug_result["request_body"] else None
        
        from datetime import datetime
        step_record.end_time = datetime.utcnow()
        if step_record.start_time:
            step_record.duration = int((step_record.end_time - step_record.start_time).total_seconds() * 1000)
        
        db.commit()
        db.refresh(step_record)
        
        all_steps = db.query(StepExecutionRecord).filter(
            StepExecutionRecord.case_execution_id == execution_id
        ).all()
        
        total = len(all_steps)
        passed = sum(1 for s in all_steps if s.status == "passed")
        failed = sum(1 for s in all_steps if s.status in ("failed", "error"))
        skipped = sum(1 for s in all_steps if s.status == "skipped")
        
        execution.passed_steps = passed
        execution.failed_steps = failed
        execution.skipped_steps = skipped
        
        if failed > 0:
            execution.status = "failed"
        else:
            execution.status = "passed"
        
        db.commit()
        db.refresh(execution)
        
        logger.info(f"步骤重试完成: step_id={step_id}, new_status={new_status}")
        
        return {
            "success": True,
            "step_id": step_id,
            "new_status": new_status,
            "error_message": error_message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"步骤重试失败: execution_id={execution_id}, step_id={step_id}, error={str(e)}")
        raise HTTPException(status_code=500, detail=f"步骤重试失败: {str(e)}")


@router.post("/executions/{execution_id}/retry")
def retry_execution(
    execution_id: int,
    db: Session = Depends(get_db)
):
    """
    重试执行

    - **execution_id**: 原执行记录ID
    """
    try:
        service = ExecutionService(db)
        detail = service.get_execution_detail(execution_id)
        if not detail:
            raise HTTPException(status_code=404, detail="执行记录不存在")

        execution = detail.get("execution")
        if not execution:
            raise HTTPException(status_code=404, detail="执行记录数据为空")

        from app.services.test_case_execution_engine import TestCaseExecutionEngine
        import asyncio

        engine = TestCaseExecutionEngine(db)
        result = asyncio.get_event_loop().run_until_complete(
            engine.execute_test_case(
                test_case_id=execution.test_case_id,
                environment_id=execution.environment_id,
                executor_id=execution.executor_id,
                executor_name=execution.executor_name,
            )
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"重试执行失败: execution_id={execution_id}, error={str(e)}")
        raise HTTPException(status_code=500, detail=f"重试执行失败: {str(e)}")


@router.get("/teams/{team_id}/executions")
def list_team_executions(
    team_id: int,
    test_case_id: Optional[int] = Query(None, description="测试用例ID筛选"),
    status: Optional[str] = Query(None, description="执行状态筛选"),
    executor_id: Optional[int] = Query(None, description="执行人筛选"),
    start_date: Optional[datetime] = Query(None, description="开始日期筛选"),
    end_date: Optional[datetime] = Query(None, description="结束日期筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    获取团队的执行记录列表

    - **team_id**: 团队ID
    - **test_case_id**: 测试用例ID筛选
    - **status**: 执行状态筛选 (running/passed/failed/skipped)
    - **executor_id**: 执行人ID筛选
    - **start_date**: 创建时间起始日期
    - **end_date**: 创建时间结束日期
    - **page**: 页码
    - **page_size**: 每页数量
    """
    try:
        logger.info(f"查询团队执行记录列表: team_id={team_id}, test_case_id={test_case_id}, page={page}")
        
        from app.models.execution_record import TestCaseExecutionRecord
        from sqlalchemy import desc

        query = db.query(TestCaseExecutionRecord).filter(
            TestCaseExecutionRecord.team_id == team_id
        )

        if test_case_id:
            query = query.filter(TestCaseExecutionRecord.test_case_id == test_case_id)
        if status:
            query = query.filter(TestCaseExecutionRecord.status == status)
        if executor_id:
            query = query.filter(TestCaseExecutionRecord.executor_id == executor_id)
        if start_date:
            query = query.filter(TestCaseExecutionRecord.created_at >= start_date)
        if end_date:
            query = query.filter(TestCaseExecutionRecord.created_at <= end_date)

        total = query.count()
        items = query.order_by(desc(TestCaseExecutionRecord.created_at)) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()

        logger.info(f"查询成功: team_id={team_id}, total={total}")
        
        return {
            "items": [
                TestCaseExecutionRecordResponse.model_validate(item) for item in items
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询团队执行记录列表失败: team_id={team_id}, error={str(e)}")
        raise HTTPException(status_code=500, detail=f"查询团队执行记录列表失败: {str(e)}")
