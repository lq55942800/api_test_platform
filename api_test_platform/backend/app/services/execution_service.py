"""
执行记录服务
"""
import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException
from datetime import datetime
from io import BytesIO

from app.models.execution_record import TestCaseExecutionRecord, StepExecutionRecord
from app.schemas.execution import (
    TestCaseExecutionRecordResponse,
    StepExecutionRecordResponse,
    ExecutionExportRequest
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class ExecutionService:
    def __init__(self, db: Session):
        self.db = db

    def create_execution_record(
        self,
        team_id: int,
        test_case_id: int,
        test_case_name: str,
        test_case_snapshot: Optional[str] = None,
        environment_id: Optional[int] = None,
        environment_name: Optional[str] = None,
        execution_type: Optional[str] = None,
        executor_id: Optional[int] = None,
        executor_name: Optional[str] = None,
    ) -> TestCaseExecutionRecord:
        """创建执行记录"""
        try:
            logger.info(f"创建执行记录: test_case_id={test_case_id}, test_case_name={test_case_name}, executor={executor_name}")
            
            execution = TestCaseExecutionRecord(
                team_id=team_id,
                test_case_id=test_case_id,
                test_case_name=test_case_name,
                test_case_snapshot=test_case_snapshot,
                environment_id=environment_id,
                environment_name=environment_name,
                execution_type=execution_type,
                status="running",
                total_steps=0,
                passed_steps=0,
                failed_steps=0,
                skipped_steps=0,
                data_iteration_count=1,
                data_iteration_passed=0,
                data_iteration_failed=0,
                start_time=datetime.utcnow(),
                executor_id=executor_id,
                executor_name=executor_name,
            )
            self.db.add(execution)
            self.db.commit()
            self.db.refresh(execution)
            
            logger.info(f"执行记录创建成功: execution_id={execution.id}")
            return execution
        except Exception as e:
            logger.error(f"创建执行记录失败: test_case_id={test_case_id}, error={str(e)}")
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"创建执行记录失败: {str(e)}")

    def update_execution_record(
        self,
        execution_id: int,
        status: Optional[str] = None,
        total_steps: Optional[int] = None,
        passed_steps: Optional[int] = None,
        failed_steps: Optional[int] = None,
        skipped_steps: Optional[int] = None,
        data_iteration_count: Optional[int] = None,
        data_iteration_passed: Optional[int] = None,
        data_iteration_failed: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> TestCaseExecutionRecord:
        """更新执行记录"""
        try:
            logger.info(f"更新执行记录: execution_id={execution_id}, status={status}")
            
            execution = self.db.query(TestCaseExecutionRecord).filter(
                TestCaseExecutionRecord.id == execution_id
            ).first()

            if not execution:
                logger.warning(f"执行记录不存在: execution_id={execution_id}")
                raise HTTPException(status_code=404, detail="执行记录不存在")

            if status is not None:
                execution.status = status
            if total_steps is not None:
                execution.total_steps = total_steps
            if passed_steps is not None:
                execution.passed_steps = passed_steps
            if failed_steps is not None:
                execution.failed_steps = failed_steps
            if skipped_steps is not None:
                execution.skipped_steps = skipped_steps
            if data_iteration_count is not None:
                execution.data_iteration_count = data_iteration_count
            if data_iteration_passed is not None:
                execution.data_iteration_passed = data_iteration_passed
            if data_iteration_failed is not None:
                execution.data_iteration_failed = data_iteration_failed
            if error_message is not None:
                execution.error_message = error_message

            if status in ["passed", "failed", "skipped"]:
                execution.end_time = datetime.utcnow()
                if execution.start_time:
                    execution.duration = int(
                        (execution.end_time - execution.start_time).total_seconds() * 1000
                    )

            self.db.commit()
            self.db.refresh(execution)
            
            logger.info(f"执行记录更新成功: execution_id={execution.id}, status={execution.status}")
            return execution
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"更新执行记录失败: execution_id={execution_id}, error={str(e)}")
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"更新执行记录失败: {str(e)}")

    def create_step_execution_record(
        self,
        case_execution_id: int,
        step_id: Optional[int] = None,
        step_name: Optional[str] = None,
        step_order: Optional[int] = None,
        api_id: Optional[int] = None,
        api_name: Optional[str] = None,
        status: str = "pending",
    ) -> StepExecutionRecord:
        """创建步骤执行记录"""
        try:
            logger.info(f"创建步骤执行记录: case_execution_id={case_execution_id}, step_name={step_name}")
            
            step_execution = StepExecutionRecord(
                case_execution_id=case_execution_id,
                step_id=step_id,
                step_name=step_name,
                step_order=step_order,
                api_id=api_id,
                api_name=api_name,
                status=status,
                start_time=datetime.utcnow(),
            )
            self.db.add(step_execution)
            self.db.commit()
            self.db.refresh(step_execution)
            
            logger.info(f"步骤执行记录创建成功: step_execution_id={step_execution.id}")
            return step_execution
        except Exception as e:
            logger.error(f"创建步骤执行记录失败: case_execution_id={case_execution_id}, error={str(e)}")
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"创建步骤执行记录失败: {str(e)}")

    def update_step_execution_record(
        self,
        step_execution_id: int,
        status: Optional[str] = None,
        skip_reason: Optional[str] = None,
        request_url: Optional[str] = None,
        request_method: Optional[str] = None,
        request_headers: Optional[str] = None,
        request_body: Optional[str] = None,
        response_status: Optional[int] = None,
        response_headers: Optional[str] = None,
        response_body: Optional[str] = None,
        response_time: Optional[int] = None,
        assertions: Optional[str] = None,
        extractors: Optional[str] = None,
        error_message: Optional[str] = None,
        pre_actions: Optional[str] = None,
        post_actions: Optional[str] = None,
    ) -> StepExecutionRecord:
        """更新步骤执行记录"""
        try:
            logger.info(f"更新步骤执行记录: step_execution_id={step_execution_id}, status={status}")
            
            step_execution = self.db.query(StepExecutionRecord).filter(
                StepExecutionRecord.id == step_execution_id
            ).first()

            if not step_execution:
                logger.warning(f"步骤执行记录不存在: step_execution_id={step_execution_id}")
                raise HTTPException(status_code=404, detail="步骤执行记录不存在")

            if status is not None:
                step_execution.status = status
            if skip_reason is not None:
                step_execution.skip_reason = skip_reason
            if request_url is not None:
                step_execution.request_url = request_url
            if request_method is not None:
                step_execution.request_method = request_method
            if request_headers is not None:
                step_execution.request_headers = request_headers
            if request_body is not None:
                step_execution.request_body = request_body
            if response_status is not None:
                step_execution.response_status = response_status
            if response_headers is not None:
                step_execution.response_headers = response_headers
            if response_body is not None:
                step_execution.response_body = response_body
            if response_time is not None:
                step_execution.response_time = response_time
            if assertions is not None:
                step_execution.assertions = assertions
            if extractors is not None:
                step_execution.extractors = extractors
            if error_message is not None:
                step_execution.error_message = error_message
            if pre_actions is not None:
                step_execution.pre_actions = pre_actions
            if post_actions is not None:
                step_execution.post_actions = post_actions

            if status in ["passed", "failed", "skipped"]:
                step_execution.end_time = datetime.utcnow()
                if step_execution.start_time:
                    step_execution.duration = int(
                        (step_execution.end_time - step_execution.start_time).total_seconds() * 1000
                    )

            self.db.commit()
            self.db.refresh(step_execution)
            
            logger.info(f"步骤执行记录更新成功: step_execution_id={step_execution.id}, status={step_execution.status}")
            return step_execution
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"更新步骤执行记录失败: step_execution_id={step_execution_id}, error={str(e)}")
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"更新步骤执行记录失败: {str(e)}")

    def get_execution_list(
        self,
        test_case_id: int,
        status: Optional[str] = None,
        executor_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[TestCaseExecutionRecord], int]:
        """获取执行记录列表"""
        logger.info(f"获取执行记录列表: test_case_id={test_case_id}, status={status}, executor_id={executor_id}, page={page}, page_size={page_size}")

        query = self.db.query(TestCaseExecutionRecord).filter(
            TestCaseExecutionRecord.test_case_id == test_case_id
        )

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

        logger.debug(f"执行记录列表查询结果: test_case_id={test_case_id}, total={total}, returned={len(items)}")
        return items, total

    def get_execution_detail(self, execution_id: int) -> Optional[Dict[str, Any]]:
        """获取执行记录详情"""
        logger.debug(f"获取执行记录详情: execution_id={execution_id}")

        execution = self.db.query(TestCaseExecutionRecord).filter(
            TestCaseExecutionRecord.id == execution_id
        ).first()

        if not execution:
            logger.warning(f"执行记录不存在: execution_id={execution_id}")
            return None

        steps = self.db.query(StepExecutionRecord).filter(
            StepExecutionRecord.case_execution_id == execution_id
        ).order_by(StepExecutionRecord.step_order).all()

        logger.debug(f"执行记录详情查询完成: execution_id={execution_id}, step_count={len(steps)}")
        return {
            "execution": execution,
            "steps": steps
        }

    def export_execution_report(
        self,
        execution_id: int,
        format: str = "html",
        include_request: bool = True,
        include_response: bool = True,
    ) -> Dict[str, Any]:
        """导出执行报告"""
        try:
            logger.info(f"导出执行报告: execution_id={execution_id}, format={format}")
            
            detail = self.get_execution_detail(execution_id)
            if not detail:
                logger.warning(f"执行记录不存在: execution_id={execution_id}")
                raise HTTPException(status_code=404, detail="执行记录不存在")

            execution = detail.get("execution")
            steps = detail.get("steps", [])
            
            # 空值检查
            if not execution:
                logger.error(f"执行记录数据为空: execution_id={execution_id}")
                raise HTTPException(status_code=404, detail="执行记录数据为空")

            if format == "html":
                return self._generate_html_report(execution, steps, include_request, include_response)
            elif format == "excel":
                return self._generate_excel_report(execution, steps, include_request, include_response)
            else:
                logger.warning(f"不支持的导出格式: {format}")
                raise HTTPException(status_code=400, detail=f"不支持的导出格式: {format}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"导出执行报告失败: execution_id={execution_id}, error={str(e)}")
            raise HTTPException(status_code=500, detail=f"导出执行报告失败: {str(e)}")

    def _generate_html_report(
        self,
        execution: TestCaseExecutionRecord,
        steps: List[StepExecutionRecord],
        include_request: bool,
        include_response: bool,
    ) -> Dict[str, Any]:
        """生成HTML报告"""
        try:
            logger.info(f"生成HTML报告: execution_id={execution.id}")
            
            # 空值检查
            if not execution:
                raise ValueError("执行记录不能为空")
            
            # 安全获取属性，避免None值导致的错误
            test_case_name = execution.test_case_name or "未命名测试用例"
            executor_name = execution.executor_name or "系统"
            start_time_str = execution.start_time.strftime('%Y-%m-%d %H:%M:%S') if execution.start_time else "-"
            duration = execution.duration or 0
            
            html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试执行报告 - {test_case_name}</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #1890ff;
            padding-bottom: 10px;
        }}
        .summary {{
            background-color: #f0f2f5;
            padding: 20px;
            border-radius: 4px;
            margin: 20px 0;
        }}
        .summary-item {{
            display: inline-block;
            margin-right: 30px;
        }}
        .summary-label {{
            font-weight: bold;
            color: #666;
        }}
        .summary-value {{
            font-size: 18px;
            color: #333;
            margin-left: 10px;
        }}
        .status-passed {{
            color: #52c41a;
        }}
        .status-failed {{
            color: #ff4d4f;
        }}
        .status-skipped {{
            color: #faad14;
        }}
        .status-running {{
            color: #1890ff;
        }}
        .step-card {{
            border: 1px solid #e8e8e8;
            border-radius: 4px;
            margin: 15px 0;
            padding: 15px;
        }}
        .step-header {{
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .detail-section {{
            margin-top: 10px;
            padding: 10px;
            background-color: #fafafa;
            border-radius: 4px;
        }}
        .detail-title {{
            font-weight: bold;
            color: #666;
            margin-bottom: 5px;
        }}
        pre {{
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>测试执行报告</h1>

        <div class="summary">
            <div class="summary-item">
                <span class="summary-label">测试用例:</span>
                <span class="summary-value">{test_case_name}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">执行状态:</span>
                <span class="summary-value status-{execution.status or 'unknown'}">{(execution.status or 'unknown').upper()}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">执行人:</span>
                <span class="summary-value">{executor_name}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">执行时间:</span>
                <span class="summary-value">{start_time_str}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">耗时:</span>
                <span class="summary-value">{duration}ms</span>
            </div>
        </div>

        <div class="summary">
            <div class="summary-item">
                <span class="summary-label">总步骤数:</span>
                <span class="summary-value">{execution.total_steps or 0}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">通过:</span>
                <span class="summary-value status-passed">{execution.passed_steps or 0}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">失败:</span>
                <span class="summary-value status-failed">{execution.failed_steps or 0}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">跳过:</span>
                <span class="summary-value status-skipped">{execution.skipped_steps or 0}</span>
            </div>
        </div>

        <h2>执行步骤详情</h2>
"""

            # 处理步骤列表
            if steps:
                for idx, step in enumerate(steps, 1):
                    step_name = step.step_name or "未命名"
                    step_status = step.status or "unknown"
                    step_duration = step.duration or 0
                    
                    html_content += f"""
        <div class="step-card">
            <div class="step-header">
                步骤 {idx}: {step_name} -
                <span class="status-{step_status}">{step_status.upper()}</span>
                <span style="margin-left: 20px; color: #999;">耗时: {step_duration}ms</span>
            </div>
"""
                    if include_request and step.request_url:
                        request_method = step.request_method or "-"
                        html_content += f"""
            <div class="detail-section">
                <div class="detail-title">请求信息</div>
                <p><strong>URL:</strong> {step.request_url}</p>
                <p><strong>方法:</strong> {request_method}</p>
"""
                        if step.request_headers:
                            html_content += f"""
                <p><strong>请求头:</strong></p>
                <pre>{step.request_headers}</pre>
"""
                        if step.request_body:
                            html_content += f"""
                <p><strong>请求体:</strong></p>
                <pre>{step.request_body}</pre>
"""
                        html_content += "            </div>"

                    if include_response and step.response_status:
                        response_time = step.response_time or 0
                        html_content += f"""
            <div class="detail-section">
                <div class="detail-title">响应信息</div>
                <p><strong>状态码:</strong> {step.response_status}</p>
                <p><strong>响应时间:</strong> {response_time}ms</p>
"""
                        if step.response_headers:
                            html_content += f"""
                <p><strong>响应头:</strong></p>
                <pre>{step.response_headers}</pre>
"""
                        if step.response_body:
                            html_content += f"""
                <p><strong>响应体:</strong></p>
                <pre>{step.response_body}</pre>
"""
                        html_content += "            </div>"

                    if step.error_message:
                        html_content += f"""
            <div class="detail-section">
                <div class="detail-title" style="color: #ff4d4f;">错误信息</div>
                <pre style="color: #ff4d4f;">{step.error_message}</pre>
            </div>
"""

                    html_content += "        </div>"
            else:
                html_content += """
        <div class="step-card">
            <p style="color: #999;">暂无步骤执行记录</p>
        </div>
"""

            html_content += """
    </div>
</body>
</html>
"""

            logger.info(f"HTML报告生成成功: execution_id={execution.id}")
            return {
                "format": "html",
                "content": html_content,
                "filename": f"execution_report_{execution.id}.html"
            }
        except Exception as e:
            logger.error(f"生成HTML报告失败: execution_id={execution.id if execution else 'unknown'}, error={str(e)}")
            raise HTTPException(status_code=500, detail=f"生成HTML报告失败: {str(e)}")

    def _generate_excel_report(
        self,
        execution: TestCaseExecutionRecord,
        steps: List[StepExecutionRecord],
        include_request: bool,
        include_response: bool,
    ) -> Dict[str, Any]:
        """生成Excel报告"""
        try:
            logger.info(f"生成Excel报告: execution_id={execution.id}")
            
            # 空值检查
            if not execution:
                raise ValueError("执行记录不能为空")
            
            try:
                import pandas as pd
            except ImportError:
                logger.error("Excel导出需要安装pandas库")
                raise HTTPException(status_code=500, detail="Excel导出需要安装pandas库")

            # 安全获取属性
            test_case_name = execution.test_case_name or "未命名测试用例"
            executor_name = execution.executor_name or "系统"
            start_time_str = execution.start_time.strftime('%Y-%m-%d %H:%M:%S') if execution.start_time else "-"
            end_time_str = execution.end_time.strftime('%Y-%m-%d %H:%M:%S') if execution.end_time else "-"
            duration = execution.duration or 0
            
            summary_data = {
                "项目": ["测试用例", "执行状态", "执行人", "开始时间", "结束时间", "耗时(ms)",
                        "总步骤数", "通过数", "失败数", "跳过数", "数据迭代次数", "迭代通过", "迭代失败"],
                "值": [
                    test_case_name,
                    execution.status or "unknown",
                    executor_name,
                    start_time_str,
                    end_time_str,
                    duration,
                    execution.total_steps or 0,
                    execution.passed_steps or 0,
                    execution.failed_steps or 0,
                    execution.skipped_steps or 0,
                    execution.data_iteration_count or 0,
                    execution.data_iteration_passed or 0,
                    execution.data_iteration_failed or 0,
                ]
            }

            steps_data = []
            if steps:
                for idx, step in enumerate(steps, 1):
                    step_dict = {
                        "步骤序号": idx,
                        "步骤名称": step.step_name or "-",
                        "API名称": step.api_name or "-",
                        "状态": step.status or "unknown",
                        "请求方法": step.request_method or "-",
                        "请求URL": step.request_url or "-",
                        "响应状态码": step.response_status or "-",
                        "响应时间(ms)": step.response_time or "-",
                        "耗时(ms)": step.duration or 0,
                        "错误信息": step.error_message or "-",
                    }

                    if include_request:
                        step_dict["请求头"] = step.request_headers or "-"
                        step_dict["请求体"] = step.request_body or "-"

                    if include_response:
                        step_dict["响应头"] = step.response_headers or "-"
                        step_dict["响应体"] = step.response_body or "-"

                    steps_data.append(step_dict)
            else:
                # 如果没有步骤数据，添加一条提示记录
                steps_data.append({
                    "步骤序号": "-",
                    "步骤名称": "暂无步骤执行记录",
                    "API名称": "-",
                    "状态": "-",
                    "请求方法": "-",
                    "请求URL": "-",
                    "响应状态码": "-",
                    "响应时间(ms)": "-",
                    "耗时(ms)": "-",
                    "错误信息": "-",
                })

            df_summary = pd.DataFrame(summary_data)
            df_steps = pd.DataFrame(steps_data)

            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_summary.to_excel(writer, sheet_name='执行概览', index=False)
                df_steps.to_excel(writer, sheet_name='步骤详情', index=False)

            output.seek(0)

            logger.info(f"Excel报告生成成功: execution_id={execution.id}")
            return {
                "format": "excel",
                "content": output.getvalue(),
                "filename": f"execution_report_{execution.id}.xlsx"
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"生成Excel报告失败: execution_id={execution.id if execution else 'unknown'}, error={str(e)}")
            raise HTTPException(status_code=500, detail=f"生成Excel报告失败: {str(e)}")

    def stop_execution(self, execution_id: int) -> Dict[str, Any]:
        """停止执行中的测试用例"""
        logger.info(f"停止执行: execution_id={execution_id}")

        execution = self.db.query(TestCaseExecutionRecord).filter(
            TestCaseExecutionRecord.id == execution_id
        ).first()

        if not execution:
            logger.warning(f"停止执行失败，执行记录不存在: execution_id={execution_id}")
            raise HTTPException(status_code=404, detail="执行记录不存在")

        if execution.status != "running":
            logger.warning(f"停止执行失败，执行状态不是running: execution_id={execution_id}, current_status={execution.status}")
            raise HTTPException(status_code=400, detail="只能停止正在执行的记录")

        execution.status = "stopped"
        execution.end_time = datetime.utcnow()
        self.db.commit()
        self.db.refresh(execution)

        logger.info(f"执行已停止: execution_id={execution_id}")
        return {"message": "执行已停止", "execution_id": execution_id}
