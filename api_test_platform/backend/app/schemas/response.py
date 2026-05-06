"""
统一响应码规范
所有API接口应使用此规范返回响应
"""
from enum import Enum
from typing import Generic, TypeVar, Optional, Any, Dict
from pydantic import BaseModel, Field

T = TypeVar('T')


class ResponseCode(str, Enum):
    """统一响应码枚举"""
    
    SUCCESS = "0000"
    
    CLIENT_ERROR_BAD_REQUEST = "1001"
    CLIENT_ERROR_INVALID_PARAM = "1002"
    CLIENT_ERROR_NOT_FOUND = "1003"
    CLIENT_ERROR_ALREADY_EXISTS = "1004"
    CLIENT_ERROR_PERMISSION_DENIED = "1005"
    CLIENT_ERROR_AUTH_FAILED = "1006"
    CLIENT_ERROR_TOKEN_EXPIRED = "1007"
    CLIENT_ERROR_TOKEN_INVALID = "1008"
    
    BUSINESS_ERROR = "2001"
    BUSINESS_ERROR_API_NOT_FOUND = "2002"
    BUSINESS_ERROR_ENV_NOT_FOUND = "2003"
    BUSINESS_ERROR_SERVICE_NOT_FOUND = "2004"
    BUSINESS_ERROR_CASE_NOT_FOUND = "2005"
    BUSINESS_ERROR_MODULE_NOT_FOUND = "2006"
    BUSINESS_ERROR_DUPLICATE_API = "2007"
    BUSINESS_ERROR_IMPORT_FAILED = "2008"
    BUSINESS_ERROR_EXPORT_FAILED = "2009"
    
    EXECUTION_ERROR = "3001"
    EXECUTION_ERROR_CONNECTION_FAILED = "3002"
    EXECUTION_ERROR_TIMEOUT = "3003"
    EXECUTION_ERROR_DNS_FAILED = "3004"
    EXECUTION_ERROR_SSL_ERROR = "3005"
    EXECUTION_ERROR_ASSERTION_FAILED = "3006"
    EXECUTION_ERROR_PRE_PROCESSOR_FAILED = "3007"
    EXECUTION_ERROR_POST_PROCESSOR_FAILED = "3008"
    EXECUTION_ERROR_VARIABLE_NOT_FOUND = "3009"
    EXECUTION_ERROR_SCRIPT_ERROR = "3010"
    
    SERVER_ERROR = "5000"
    SERVER_ERROR_DATABASE = "5001"
    SERVER_ERROR_EXTERNAL_SERVICE = "5002"


CODE_MESSAGES: Dict[str, str] = {
    ResponseCode.SUCCESS: "操作成功",
    
    ResponseCode.CLIENT_ERROR_BAD_REQUEST: "请求参数错误",
    ResponseCode.CLIENT_ERROR_INVALID_PARAM: "参数校验失败",
    ResponseCode.CLIENT_ERROR_NOT_FOUND: "资源不存在",
    ResponseCode.CLIENT_ERROR_ALREADY_EXISTS: "资源已存在",
    ResponseCode.CLIENT_ERROR_PERMISSION_DENIED: "权限不足",
    ResponseCode.CLIENT_ERROR_AUTH_FAILED: "认证失败",
    ResponseCode.CLIENT_ERROR_TOKEN_EXPIRED: "令牌已过期",
    ResponseCode.CLIENT_ERROR_TOKEN_INVALID: "令牌无效",
    
    ResponseCode.BUSINESS_ERROR: "业务处理失败",
    ResponseCode.BUSINESS_ERROR_API_NOT_FOUND: "接口不存在",
    ResponseCode.BUSINESS_ERROR_ENV_NOT_FOUND: "环境不存在",
    ResponseCode.BUSINESS_ERROR_SERVICE_NOT_FOUND: "服务不存在",
    ResponseCode.BUSINESS_ERROR_CASE_NOT_FOUND: "测试用例不存在",
    ResponseCode.BUSINESS_ERROR_MODULE_NOT_FOUND: "模块不存在",
    ResponseCode.BUSINESS_ERROR_DUPLICATE_API: "接口已存在",
    ResponseCode.BUSINESS_ERROR_IMPORT_FAILED: "导入失败",
    ResponseCode.BUSINESS_ERROR_EXPORT_FAILED: "导出失败",
    
    ResponseCode.EXECUTION_ERROR: "执行失败",
    ResponseCode.EXECUTION_ERROR_CONNECTION_FAILED: "连接失败，请检查网络或目标服务是否可用",
    ResponseCode.EXECUTION_ERROR_TIMEOUT: "请求超时，请检查目标服务响应时间或调整超时配置",
    ResponseCode.EXECUTION_ERROR_DNS_FAILED: "DNS解析失败，请检查域名是否正确",
    ResponseCode.EXECUTION_ERROR_SSL_ERROR: "SSL证书错误，请检查证书配置",
    ResponseCode.EXECUTION_ERROR_ASSERTION_FAILED: "断言验证失败",
    ResponseCode.EXECUTION_ERROR_PRE_PROCESSOR_FAILED: "前置处理器执行失败",
    ResponseCode.EXECUTION_ERROR_POST_PROCESSOR_FAILED: "后置处理器执行失败",
    ResponseCode.EXECUTION_ERROR_VARIABLE_NOT_FOUND: "变量未找到",
    ResponseCode.EXECUTION_ERROR_SCRIPT_ERROR: "脚本执行错误",
    
    ResponseCode.SERVER_ERROR: "服务器内部错误",
    ResponseCode.SERVER_ERROR_DATABASE: "数据库错误",
    ResponseCode.SERVER_ERROR_EXTERNAL_SERVICE: "外部服务错误",
}


class ApiResponse(BaseModel, Generic[T]):
    """统一API响应格式"""
    code: str = Field(default=ResponseCode.SUCCESS, description="响应码")
    message: str = Field(default="操作成功", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")
    
    @classmethod
    def success(cls, data: T = None, message: str = "操作成功") -> "ApiResponse[T]":
        """创建成功响应"""
        return cls(code=ResponseCode.SUCCESS, message=message, data=data)
    
    @classmethod
    def error(cls, code: ResponseCode, message: str = None, data: T = None) -> "ApiResponse[T]":
        """创建错误响应"""
        actual_message = message or CODE_MESSAGES.get(code, "未知错误")
        return cls(code=code, message=actual_message, data=data)


class DebugResultWithCode(BaseModel):
    """带响应码的调试结果"""
    code: str = Field(default=ResponseCode.SUCCESS, description="响应码")
    message: str = Field(default="调试成功", description="响应消息")
    status_code: Optional[int] = Field(None, description="HTTP状态码")
    headers: Optional[Dict[str, str]] = Field(None, description="响应头")
    body: Optional[str] = Field(None, description="响应体")
    elapsed_ms: Optional[int] = Field(None, description="耗时(毫秒)")
    error_message: Optional[str] = Field(None, description="错误信息")
    history_id: Optional[int] = Field(None, description="调试历史ID")
    request_url: Optional[str] = Field(None, description="完整请求URL")
    request_headers: Optional[Dict[str, str]] = Field(None, description="请求头")
    pre_request_results: Optional[List[Any]] = Field(None, description="前置操作结果")
    post_request_results: Optional[List[Any]] = Field(None, description="后置操作结果")
    assertion_results: Optional[List[Any]] = Field(None, description="断言结果")
    assertion_summary: Optional[Dict[str, Any]] = Field(None, description="断言摘要")
    variables_snapshot: Optional[Dict[str, Any]] = Field(None, description="变量快照")
    timeout_config: Optional[Dict[str, int]] = Field(None, description="使用的超时配置")
