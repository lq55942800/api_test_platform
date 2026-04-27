from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class StepExecutionRecordResponse(BaseModel):
    id: int
    case_execution_id: int
    step_id: Optional[int]
    step_name: Optional[str]
    step_order: Optional[int]
    api_id: Optional[int]
    api_name: Optional[str]
    status: str
    skip_reason: Optional[str]
    request_url: Optional[str]
    request_method: Optional[str]
    request_headers: Optional[str]
    request_body: Optional[str]
    response_status: Optional[int]
    response_headers: Optional[str]
    response_body: Optional[str]
    response_time: Optional[int]
    assertions: Optional[str]
    extractors: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    duration: Optional[int]
    error_message: Optional[str]

    class Config:
        from_attributes = True


class TestCaseExecutionRecordResponse(BaseModel):
    id: int
    team_id: int
    test_case_id: int
    test_case_name: str
    test_case_snapshot: Optional[str]
    environment_id: Optional[int]
    environment_name: Optional[str]
    execution_type: Optional[str]
    status: str
    total_steps: int
    passed_steps: int
    failed_steps: int
    skipped_steps: int
    data_iteration_count: int
    data_iteration_passed: int
    data_iteration_failed: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    duration: Optional[int]
    executor_id: Optional[int]
    executor_name: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    steps: Optional[List[StepExecutionRecordResponse]] = None

    class Config:
        from_attributes = True


class ExecutionExportRequest(BaseModel):
    format: str = Field("html", description="导出格式: html, excel, pdf")
    include_request: bool = Field(True, description="包含请求详情")
    include_response: bool = Field(True, description="包含响应详情")
