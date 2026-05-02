from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ActionResult(BaseModel):
    id: str = Field(default="", description="操作ID")
    name: str = Field(default="", description="操作名称")
    type: str = Field(default="", description="操作类型")
    success: bool = Field(default=True, description="是否成功")
    error: Optional[str] = Field(None, description="错误信息")
    duration_ms: int = Field(default=0, description="执行耗时(毫秒)")
    output: Optional[Dict[str, Any]] = Field(None, description="输出数据")


class BaseProcessor(ABC):
    def __init__(self, variable_manager=None, extractor_engine=None):
        self.variable_manager = variable_manager
        self.extractor_engine = extractor_engine

    @abstractmethod
    async def execute(self, action: Dict[str, Any], context: Dict[str, Any]) -> ActionResult:
        pass

    def _get_config(self, action: Dict[str, Any]) -> Dict[str, Any]:
        return action.get("config", {})

    def _resolve_expression(self, expression: str) -> str:
        if self.variable_manager and expression:
            return self.variable_manager.resolve(expression)
        return expression or ""

    def _get_on_error(self, action: Dict[str, Any], default: str = "abort") -> str:
        return self._get_config(action).get("on_error", default)
