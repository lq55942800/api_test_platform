from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime


class TestCaseStepCreate(BaseModel):
    api_id: int
    step_name: Optional[str] = None
    sort_order: int = 0
    enabled: bool = True
    override_headers: Optional[Dict[str, Any]] = None
    override_params: Optional[Dict[str, Any]] = None
    override_body: Optional[str] = None
    override_body_type: Optional[str] = None
    override_cookies: Optional[List[Dict[str, Any]]] = None
    assertions: Optional[List[Dict[str, Any]]] = None
    extractors: Optional[List[Dict[str, Any]]] = None
    pre_script: Optional[str] = None
    post_script: Optional[str] = None
    timeout_config: Optional[Dict[str, Any]] = None
    execution_condition: Optional[Dict[str, Any]] = None


class TestCaseStepResponse(TestCaseStepCreate):
    id: int
    test_case_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TestCaseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    module_id: Optional[int] = None
    description: Optional[str] = Field(None, max_length=500)
    status: str = "enabled"
    priority: str = "P2"
    tags: Optional[List[str]] = None
    variables: Optional[List[Dict[str, Any]]] = None
    execution_condition: Optional[Dict[str, Any]] = None
    steps: Optional[List[TestCaseStepCreate]] = None


class TestCaseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    module_id: Optional[int] = None
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    variables: Optional[List[Dict[str, Any]]] = None
    execution_condition: Optional[Dict[str, Any]] = None
    steps: Optional[List[TestCaseStepCreate]] = None


class TestCaseResponse(BaseModel):
    id: int
    team_id: int
    name: str
    module_id: Optional[int]
    description: Optional[str]
    status: str
    priority: str
    tags: Optional[List[str]]
    variables: Optional[List[Dict[str, Any]]]
    execution_condition: Optional[Dict[str, Any]]
    created_by: int
    created_at: datetime
    updated_at: datetime
    steps: Optional[List[TestCaseStepResponse]] = None

    class Config:
        from_attributes = True


class TestCaseExecuteRequest(BaseModel):
    environment_id: int = Field(..., description="执行环境ID")
    fail_strategy: str = Field("stop", description="失败策略: stop/continue")
    save_record: bool = Field(True, description="是否保存执行记录")
    timeout: int = Field(600000, description="超时时间(毫秒)")
    step_interval: int = Field(0, description="步骤间隔(毫秒)")
    data_source_id: Optional[int] = Field(None, description="数据源ID(数据驱动时)")


class CrossTeamCopyRequest(BaseModel):
    target_team_id: int
    copy_options: Optional[Dict[str, bool]] = None


class CrossTeamCopyCheckResponse(BaseModel):
    can_copy: bool
    warnings: List[Dict[str, Any]]
    services_to_check: List[Dict[str, Any]]
    variables_to_check: List[Dict[str, Any]]
