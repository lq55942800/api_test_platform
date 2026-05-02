"""
API Management Schemas
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any, Dict
from datetime import datetime
from enum import Enum


class ApiStatus(str, Enum):
    DRAFT = "draft"
    ENABLED = "enabled"
    DISABLED = "disabled"
    DEPRECATED = "deprecated"


class BodyType(str, Enum):
    NONE = "none"
    JSON = "json"
    FORM_DATA = "form-data"
    X_WWW_FORM_URLENCODED = "x-www-form-urlencoded"
    RAW = "raw"
    XML = "xml"
    BINARY = "binary"


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class ChangeType(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ROLLBACK = "rollback"


class AuditAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    DEBUG = "debug"
    IMPORT = "import"
    EXPORT = "export"
    STATUS_CHANGE = "status_change"
    ROLLBACK = "rollback"


class ConflictStrategy(str, Enum):
    SKIP = "skip"
    OVERWRITE = "overwrite"
    COPY = "copy"
    MANUAL = "manual"


class ExportFormat(str, Enum):
    OPENAPI3 = "openapi3"
    SWAGGER2 = "swagger2"
    POSTMAN = "postman"


class PreRequestActionType(str, Enum):
    PARAM_PROCESS = "param_process"
    DATABASE = "database"
    VARIABLE_EXTRACT = "variable_extract"
    CONDITION = "condition"
    WAIT = "wait"
    SCRIPT = "script"
    REGEX_PARAM = "regex_param"
    COOKIE_MANAGER = "cookie_manager"
    HEADER_MODIFIER = "header_modifier"
    SAMPLE_TIMEOUT = "sample_timeout"


class PostRequestActionType(str, Enum):
    EXTRACT = "extract"
    DATABASE = "database"
    SET_VARIABLE = "set_variable"
    CONDITION = "condition"
    SCRIPT = "script"
    RESULT_STATUS_HANDLER = "result_status_handler"
    DEBUG_OUTPUT = "debug_output"


class AssertionType(str, Enum):
    STATUS_CODE = "status_code"
    HEADER = "header"
    RESPONSE_TIME = "response_time"
    BODY = "body"
    JSONPATH = "jsonpath"
    XPATH = "xpath"
    REGEX = "regex"
    JSON_SCHEMA = "json_schema"
    SIZE = "size"
    XML = "xml"
    XML_SCHEMA = "xml_schema"
    MD5 = "md5"
    SCRIPT = "script"


# ==================== 前置/后置操作与断言 Schema ====================

class PreRequestAction(BaseModel):
    """前置操作"""
    id: str = Field(default="", description="操作ID")
    enabled: bool = Field(default=True, description="是否启用")
    name: str = Field(..., max_length=100, description="操作名称")
    type: str = Field(default="param_process", description="操作类型")
    phase: str = Field(default="pre_request", description="执行阶段")
    order: int = Field(default=0, description="执行顺序")
    config: Dict[str, Any] = Field(default_factory=dict, description="操作配置")
    description: Optional[str] = Field(None, max_length=500, description="操作描述")


class PostRequestAction(BaseModel):
    """后置操作"""
    id: str = Field(default="", description="操作ID")
    enabled: bool = Field(default=True, description="是否启用")
    name: str = Field(..., max_length=100, description="操作名称")
    type: str = Field(default="extract", description="操作类型")
    phase: str = Field(default="post_request", description="执行阶段")
    order: int = Field(default=0, description="执行顺序")
    config: Dict[str, Any] = Field(default_factory=dict, description="操作配置")
    description: Optional[str] = Field(None, max_length=500, description="操作描述")


class Assertion(BaseModel):
    """断言"""
    id: str = Field(default="", description="断言ID")
    enabled: bool = Field(default=True, description="是否启用")
    name: str = Field(..., max_length=100, description="断言名称")
    type: str = Field(default="status_code", description="断言类型")
    phase: str = Field(default="assertion", description="执行阶段")
    order: int = Field(default=0, description="执行顺序")
    config: Dict[str, Any] = Field(default_factory=dict, description="断言配置")
    description: Optional[str] = Field(None, max_length=500, description="断言描述")


# ==================== 参数定义 Schema ====================

class ParamDefinition(BaseModel):
    """参数定义"""
    name: str = Field(..., max_length=100, description="参数名称")
    param_type: str = Field(default="String", description="参数类型: String/Integer/Float/Boolean/Array/Object/File")
    required: bool = Field(default=False, description="是否必填")
    default_value: Optional[Any] = Field(None, description="默认值")
    description: Optional[str] = Field(None, max_length=500, description="参数说明")
    example: Optional[str] = Field(None, description="示例值")
    validation_rules: Optional[Dict[str, Any]] = Field(None, description="校验规则")


class ResponseDefinition(BaseModel):
    """响应定义"""
    status_code: int = Field(..., description="HTTP状态码")
    description: str = Field(..., description="状态码说明")
    body_schema: Optional[Dict[str, Any]] = Field(None, description="响应体JSON Schema")
    example: Optional[str] = Field(None, description="响应示例")
    headers: Optional[Dict[str, Any]] = Field(None, description="响应头定义")


# ==================== 接口定义 Schema ====================

class ApiDefinitionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="接口名称")
    method: HttpMethod = Field(..., description="HTTP方法")
    path: str = Field(..., min_length=1, max_length=255, description="接口路径")
    description: Optional[str] = Field(None, description="接口描述")
    protocol: str = Field(default="http", max_length=20, description="协议")
    service_id: Optional[int] = Field(None, description="关联服务ID")
    path_params: Optional[List[ParamDefinition]] = Field(None, description="路径参数")
    query_params: Optional[List[ParamDefinition]] = Field(None, description="查询参数")
    header_params: Optional[List[ParamDefinition]] = Field(None, description="请求头参数")
    cookie_params: Optional[List[ParamDefinition]] = Field(None, description="Cookie参数")
    body_type: BodyType = Field(default=BodyType.NONE, description="请求体类型")
    body_definition: Optional[Any] = Field(None, description="请求体定义")
    responses: Optional[List[ResponseDefinition]] = Field(None, description="响应定义")
    pre_request_actions: Optional[List[PreRequestAction]] = Field(None, description="前置操作列表")
    post_request_actions: Optional[List[PostRequestAction]] = Field(None, description="后置操作列表")
    assertions: Optional[List[Assertion]] = Field(None, description="断言列表")
    connect_timeout: Optional[int] = Field(default=5000, ge=1, le=60000, description="连接超时(毫秒)")
    read_timeout: Optional[int] = Field(default=30000, ge=1, le=300000, description="读取超时(毫秒)")
    write_timeout: Optional[int] = Field(default=10000, ge=1, le=60000, description="发送超时(毫秒)")
    pool_timeout: Optional[int] = Field(default=5000, ge=1, le=30000, description="连接池超时(毫秒)")
    sample_timeout: Optional[int] = Field(default=60000, ge=1, le=600000, description="全局超时(毫秒)")
    sql_timeout: Optional[int] = Field(default=30000, ge=1, le=300000, description="SQL超时(毫秒)")
    script_timeout: Optional[int] = Field(default=10000, ge=1, le=120000, description="脚本超时(毫秒)")
    timeout_enabled: Optional[bool] = Field(default=True, description="是否启用自定义超时")


class ApiDefinitionCreate(ApiDefinitionBase):
    team_id: Optional[int] = Field(None, description="团队ID")
    module_id: Optional[int] = Field(None, description="模块ID")
    owner_id: Optional[int] = Field(None, description="责任人ID")
    tag_ids: Optional[List[int]] = Field(None, description="标签ID列表")


class ApiDefinitionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="接口名称")
    method: Optional[HttpMethod] = Field(None, description="HTTP方法")
    path: Optional[str] = Field(None, min_length=1, max_length=255, description="接口路径")
    description: Optional[str] = Field(None, description="接口描述")
    protocol: Optional[str] = Field(None, max_length=20, description="协议")
    module_id: Optional[int] = Field(None, description="模块ID")
    service_id: Optional[int] = Field(None, description="关联服务ID")
    owner_id: Optional[int] = Field(None, description="责任人ID")
    path_params: Optional[List[ParamDefinition]] = Field(None, description="路径参数")
    query_params: Optional[List[ParamDefinition]] = Field(None, description="查询参数")
    header_params: Optional[List[ParamDefinition]] = Field(None, description="请求头参数")
    cookie_params: Optional[List[ParamDefinition]] = Field(None, description="Cookie参数")
    body_type: Optional[BodyType] = Field(None, description="请求体类型")
    body_definition: Optional[Any] = Field(None, description="请求体定义")
    responses: Optional[List[ResponseDefinition]] = Field(None, description="响应定义")
    pre_request_actions: Optional[List[PreRequestAction]] = Field(None, description="前置操作列表")
    post_request_actions: Optional[List[PostRequestAction]] = Field(None, description="后置操作列表")
    assertions: Optional[List[Assertion]] = Field(None, description="断言列表")
    tag_ids: Optional[List[int]] = Field(None, description="标签ID列表")
    connect_timeout: Optional[int] = Field(None, ge=1, le=60000, description="连接超时(毫秒)")
    read_timeout: Optional[int] = Field(None, ge=1, le=300000, description="读取超时(毫秒)")
    write_timeout: Optional[int] = Field(None, ge=1, le=60000, description="发送超时(毫秒)")
    pool_timeout: Optional[int] = Field(None, ge=1, le=30000, description="连接池超时(毫秒)")
    sample_timeout: Optional[int] = Field(None, ge=1, le=600000, description="全局超时(毫秒)")
    sql_timeout: Optional[int] = Field(None, ge=1, le=300000, description="SQL超时(毫秒)")
    script_timeout: Optional[int] = Field(None, ge=1, le=120000, description="脚本超时(毫秒)")
    timeout_enabled: Optional[bool] = Field(None, description="是否启用自定义超时")


class UpdateStatusRequest(BaseModel):
    status: ApiStatus = Field(..., description="目标状态")


class ApiDefinitionResponse(ApiDefinitionBase):
    id: int
    team_id: int
    module_id: Optional[int]
    service_id: Optional[int]
    status: ApiStatus
    owner_id: Optional[int]
    lock_user_id: Optional[int]
    lock_time: Optional[datetime]
    last_debug_at: Optional[datetime]
    last_debug_status: Optional[str]
    reference_count: int
    is_deleted: bool
    created_by: int
    updated_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    module_name: Optional[str] = None
    tags: Optional[List[Dict[str, Any]]] = None
    class Config:
        from_attributes = True


class ApiDefinitionListResponse(BaseModel):
    items: List[ApiDefinitionResponse]
    total: int
    page: int
    page_size: int


class ApiDefinitionSummary(BaseModel):
    """接口列表简要信息"""
    id: int
    name: str
    method: str
    path: str
    status: ApiStatus
    module_id: Optional[int]
    owner_id: Optional[int]
    updated_at: datetime
    tags: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True


# ==================== 模块 Schema ====================

class ApiModuleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="模块名称")
    description: Optional[str] = Field(None, max_length=200, description="模块描述")
    sort_order: int = Field(default=0, description="排序序号")


class ApiModuleCreate(ApiModuleBase):
    team_id: Optional[int] = Field(None, description="团队ID")
    parent_id: Optional[int] = Field(None, description="父模块ID")


class ApiModuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="模块名称")
    description: Optional[str] = Field(None, max_length=200, description="模块描述")
    sort_order: Optional[int] = Field(None, description="排序序号")
    parent_id: Optional[int] = Field(None, description="父模块ID")


class ApiModuleResponse(ApiModuleBase):
    id: int
    team_id: int
    parent_id: Optional[int]
    created_by: int
    created_at: datetime
    updated_at: datetime
    children: Optional[List["ApiModuleResponse"]] = None
    api_count: Optional[int] = 0

    class Config:
        from_attributes = True


# ==================== 标签 Schema ====================

class ApiTagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=20, description="标签名称")
    color: Optional[str] = Field(None, max_length=7, description="标签颜色")
    tag_group: Optional[str] = Field(None, max_length=50, description="标签分组")


class ApiTagCreate(ApiTagBase):
    team_id: Optional[int] = Field(None, description="团队ID")


class ApiTagResponse(ApiTagBase):
    id: int
    team_id: int
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class ApiTagBatchRequest(BaseModel):
    api_id: int = Field(..., description="接口ID")
    tag_ids: List[int] = Field(..., description="标签ID列表")


# ==================== 版本 Schema ====================

class ApiVersionResponse(BaseModel):
    id: int
    api_id: int
    version_number: int
    change_type: ChangeType
    change_summary: Optional[str]
    affected_fields: Optional[str]
    changed_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class ApiVersionListResponse(BaseModel):
    items: List[ApiVersionResponse]
    total: int
    page: int
    page_size: int


class VersionCompareRequest(BaseModel):
    v1: int = Field(..., description="版本号1")
    v2: int = Field(..., description="版本号2")


class VersionDiffChange(BaseModel):
    type: str = Field(..., description="变更类型")
    field: str = Field(..., description="变更字段")
    old_value: Optional[Any] = Field(None, description="旧值")
    new_value: Optional[Any] = Field(None, description="新值")
    impact: str = Field(default="low", description="影响等级: high/medium/low")


class VersionDiffResponse(BaseModel):
    changes: List[VersionDiffChange]
    impact_level: str = Field(..., description="整体影响等级")
    summary: str = Field(..., description="变更摘要")


class RollbackRequest(BaseModel):
    target_version: int = Field(..., description="目标版本号")


# ==================== 调试 Schema ====================

class DebugRequest(BaseModel):
    environment_id: Optional[int] = Field(None, description="环境ID")
    service_id: Optional[int] = Field(None, description="服务ID")
    param_overrides: Optional[Dict[str, Any]] = Field(None, description="参数覆盖")
    header_overrides: Optional[Dict[str, Any]] = Field(None, description="Header覆盖")
    body_overrides: Optional[str] = Field(None, description="Body覆盖")
    body_type: Optional[str] = Field(None, description="Body类型")
    cookie_overrides: Optional[List[Dict[str, Any]]] = Field(None, description="Cookie覆盖")
    pre_request_actions_overrides: Optional[List[Dict[str, Any]]] = Field(None, description="前置操作覆盖")
    post_request_actions_overrides: Optional[List[Dict[str, Any]]] = Field(None, description="后置操作覆盖")
    assertions_overrides: Optional[List[Dict[str, Any]]] = Field(None, description="断言覆盖")
    timeout_config_overrides: Optional[Dict[str, Any]] = Field(None, description="超时配置覆盖")


class ActionExecutionResult(BaseModel):
    id: str = Field(default="", description="操作ID")
    name: str = Field(default="", description="操作名称")
    type: str = Field(default="", description="操作类型")
    success: bool = Field(default=True, description="是否成功")
    error: Optional[str] = Field(None, description="错误信息")
    duration_ms: int = Field(default=0, description="执行耗时(毫秒)")
    output: Optional[Dict[str, Any]] = Field(None, description="输出数据")


class AssertionExecutionResult(BaseModel):
    id: str = Field(default="", description="断言ID")
    name: str = Field(default="", description="断言名称")
    type: str = Field(default="", description="断言类型")
    passed: bool = Field(default=True, description="是否通过")
    actual: Any = Field(None, description="实际值")
    expected: Any = Field(None, description="期望值")
    operator: Optional[str] = Field(None, description="操作符")
    message: str = Field(default="", description="断言消息")
    severity: str = Field(default="critical", description="严重级别")
    duration_ms: int = Field(default=0, description="执行耗时(毫秒)")


class AssertionSummary(BaseModel):
    total: int = 0
    passed: int = 0
    failed: int = 0
    critical_failed: int = 0
    warning_failed: int = 0
    info_failed: int = 0
    all_passed: bool = True
    critical_passed: bool = True


class DebugResultResponse(BaseModel):
    status_code: Optional[int] = Field(None, description="HTTP状态码")
    headers: Optional[Dict[str, str]] = Field(None, description="响应头")
    body: Optional[str] = Field(None, description="响应体")
    elapsed_ms: Optional[int] = Field(None, description="耗时(毫秒)")
    error_message: Optional[str] = Field(None, description="错误信息")
    history_id: Optional[int] = Field(None, description="调试历史ID")
    request_url: Optional[str] = Field(None, description="完整请求URL")
    request_headers: Optional[Dict[str, str]] = Field(None, description="请求头")
    pre_request_results: Optional[List[ActionExecutionResult]] = Field(None, description="前置操作结果")
    post_request_results: Optional[List[ActionExecutionResult]] = Field(None, description="后置操作结果")
    assertion_results: Optional[List[AssertionExecutionResult]] = Field(None, description="断言结果")
    assertion_summary: Optional[AssertionSummary] = Field(None, description="断言摘要")
    variables_snapshot: Optional[Dict[str, Any]] = Field(None, description="变量快照")
    timeout_config: Optional[Dict[str, int]] = Field(None, description="使用的超时配置")


class DebugHistoryResponse(BaseModel):
    id: int
    api_id: int
    environment_id: Optional[int]
    user_id: int
    request_method: str
    request_url: str
    request_headers: Optional[str]
    request_body: Optional[str]
    response_status: Optional[int]
    response_headers: Optional[str]
    response_body: Optional[str]
    elapsed_ms: Optional[int]
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DebugHistoryListResponse(BaseModel):
    items: List[DebugHistoryResponse]
    total: int
    page: int
    page_size: int


# ==================== 导入 Schema ====================

class ImportRequest(BaseModel):
    import_type: str = Field(default="file", description="导入类型: file/url")
    content: Optional[str] = Field(None, description="文件内容(JSON/YAML)")
    url: Optional[str] = Field(None, description="导入URL地址")
    format: Optional[str] = Field(None, description="文件格式: swagger2/openapi3/har，不传则自动检测")
    module_id: Optional[int] = Field(None, description="目标模块ID")
    conflict_strategy: ConflictStrategy = Field(default=ConflictStrategy.SKIP, description="冲突处理策略")


class ImportResultResponse(BaseModel):
    total: int = Field(..., description="总接口数")
    created: int = Field(..., description="成功创建数")
    skipped: int = Field(..., description="跳过数")
    failed: int = Field(..., description="失败数")
    details: Optional[List[Dict[str, Any]]] = Field(None, description="详细结果")


class ImportPreviewItem(BaseModel):
    method: str = Field(..., description="HTTP方法")
    path: str = Field(..., description="接口路径")
    name: str = Field(..., description="接口名称")
    status: str = Field(..., description="状态: new/duplicate/failed")
    error: Optional[str] = Field(None, description="错误信息")
    module_name: Optional[str] = Field(None, description="模块名称")
    selected: bool = Field(default=True, description="是否选中")


class ImportPreviewResponse(BaseModel):
    total: int = Field(..., description="总接口数")
    new_count: int = Field(..., description="新增数")
    duplicate_count: int = Field(..., description="重复数")
    failed_count: int = Field(..., description="失败数")
    apis: List[ImportPreviewItem] = Field(..., description="接口预览列表")


# ==================== 导出 Schema ====================

class ExportRequest(BaseModel):
    format: ExportFormat = Field(..., description="导出格式")
    module_id: Optional[int] = Field(None, description="按模块导出")
    api_ids: Optional[List[int]] = Field(None, description="指定接口ID列表")
    include_draft: bool = Field(default=False, description="是否包含草稿状态接口")
    include_deprecated: bool = Field(default=False, description="是否包含废弃状态接口")
    title: Optional[str] = Field(None, description="文档标题")
    description: Optional[str] = Field(None, description="文档描述")


# ==================== 审计日志 Schema ====================

class AuditLogResponse(BaseModel):
    id: int
    team_id: int
    api_id: Optional[int]
    user_id: int
    action: AuditAction
    resource_type: str
    resource_name: Optional[str]
    old_value: Optional[str]
    new_value: Optional[str]
    change_summary: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    items: List[AuditLogResponse]
    total: int
    page: int
    page_size: int


# ==================== 锁定 Schema ====================

class LockResultResponse(BaseModel):
    acquired: bool = Field(..., description="是否获取成功")
    locked_by: Optional[int] = Field(None, description="锁定者用户ID")
    locked_at: Optional[datetime] = Field(None, description="锁定时间")


# ==================== 批量操作 Schema ====================

class BatchDeleteRequest(BaseModel):
    api_ids: List[int] = Field(..., min_length=1, max_length=100, description="接口ID列表")


class BatchMoveRequest(BaseModel):
    api_ids: List[int] = Field(..., min_length=1, max_length=100, description="接口ID列表")
    target_module_id: Optional[int] = Field(None, description="目标模块ID")


class BatchStatusRequest(BaseModel):
    api_ids: List[int] = Field(..., min_length=1, max_length=100, description="接口ID列表")
    status: ApiStatus = Field(..., description="目标状态")


class BatchResultResponse(BaseModel):
    success_count: int = Field(..., description="成功数")
    failed_count: int = Field(..., description="失败数")
    details: Optional[List[Dict[str, Any]]] = Field(None, description="详细结果")


# ==================== 引用 Schema ====================

class ReferenceInfo(BaseModel):
    type: str = Field(..., description="引用类型: testcase/scenario")
    id: int = Field(..., description="引用ID")
    name: str = Field(..., description="引用名称")


class ReferenceListResponse(BaseModel):
    api_id: int
    references: List[ReferenceInfo]
    total: int


# ==================== 通知 Schema ====================

class NotificationResponse(BaseModel):
    id: int
    api_id: int
    change_type: str
    change_summary: Optional[str]
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    items: List[NotificationResponse]
    total: int
    page: int
    page_size: int
