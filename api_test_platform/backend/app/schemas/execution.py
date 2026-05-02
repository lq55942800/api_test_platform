import json
from pydantic import BaseModel, Field, computed_field
from typing import Optional, List, Dict, Any
from datetime import datetime


class StepExecutionRecordResponse(BaseModel):
    id: int
    case_execution_id: int
    step_id: Optional[int] = None
    step_name: Optional[str] = None
    step_order: Optional[int] = None
    api_id: Optional[int] = None
    api_name: Optional[str] = None
    status: str
    skip_reason: Optional[str] = None
    request_url: Optional[str] = None
    request_method: Optional[str] = None
    request_headers: Optional[str] = None
    request_body: Optional[str] = None
    response_status: Optional[int] = None
    response_headers: Optional[str] = None
    response_body: Optional[str] = None
    response_time: Optional[int] = None
    assertions: Optional[str] = None
    extractors: Optional[str] = None
    pre_actions: Optional[str] = None
    post_actions: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

    @computed_field
    @property
    def request_data(self) -> Optional[Dict[str, Any]]:
        data: Dict[str, Any] = {}
        if self.request_method:
            data["method"] = self.request_method
        if self.request_url:
            data["url"] = self.request_url
        if self.request_headers:
            try:
                data["headers"] = json.loads(self.request_headers)
            except (json.JSONDecodeError, TypeError):
                data["headers"] = self.request_headers
        if self.request_body:
            try:
                data["body"] = json.loads(self.request_body)
            except (json.JSONDecodeError, TypeError):
                data["body"] = self.request_body
        if self.assertions:
            try:
                data["assertions"] = json.loads(self.assertions)
            except (json.JSONDecodeError, TypeError):
                data["assertions"] = self.assertions
        if self.extractors:
            try:
                data["extractors"] = json.loads(self.extractors)
            except (json.JSONDecodeError, TypeError):
                data["extractors"] = self.extractors
        if self.pre_actions:
            try:
                data["pre_actions"] = json.loads(self.pre_actions)
            except (json.JSONDecodeError, TypeError):
                data["pre_actions"] = self.pre_actions
        if self.post_actions:
            try:
                data["post_actions"] = json.loads(self.post_actions)
            except (json.JSONDecodeError, TypeError):
                data["post_actions"] = self.post_actions
        return data if data else None

    @computed_field
    @property
    def response_data(self) -> Optional[Dict[str, Any]]:
        data: Dict[str, Any] = {}
        if self.response_status:
            data["status_code"] = self.response_status
        if self.response_headers:
            try:
                data["headers"] = json.loads(self.response_headers)
            except (json.JSONDecodeError, TypeError):
                data["headers"] = self.response_headers
        if self.response_body:
            try:
                data["body"] = json.loads(self.response_body)
            except (json.JSONDecodeError, TypeError):
                data["body"] = self.response_body
        if self.response_time:
            data["duration"] = self.response_time
        return data if data else None


class TestCaseExecutionRecordResponse(BaseModel):
    id: int
    team_id: int
    test_case_id: int
    test_case_name: str
    test_case_snapshot: Optional[str] = None
    environment_id: Optional[int] = None
    environment_name: Optional[str] = None
    execution_type: Optional[str] = None
    status: str
    total_steps: int = 0
    passed_steps: int = 0
    failed_steps: int = 0
    skipped_steps: int = 0
    data_iteration_count: int = 1
    data_iteration_passed: int = 0
    data_iteration_failed: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    executor_id: Optional[int] = None
    executor_name: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    steps: Optional[List[StepExecutionRecordResponse]] = None

    class Config:
        from_attributes = True


class ExecutionExportRequest(BaseModel):
    format: str = Field("html", description="导出格式: html, excel, pdf")
    include_request: bool = Field(True, description="包含请求详情")
    include_response: bool = Field(True, description="包含响应详情")
