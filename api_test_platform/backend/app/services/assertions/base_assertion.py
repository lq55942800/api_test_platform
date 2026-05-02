import logging
import re
from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

OPERATOR_ALIASES = {
    "eq": "eq", "equals": "eq", "==": "eq", "equal": "eq",
    "neq": "neq", "not_equals": "neq", "!=": "neq",
    "gt": "gt", "greater_than": "gt", ">": "gt",
    "lt": "lt", "less_than": "lt", "<": "lt",
    "gte": "gte", "greater_or_equal": "gte", ">=": "gte",
    "lte": "lte", "less_or_equal": "lte", "<=": "lte",
    "contains": "contains",
    "not_contains": "not_contains",
    "starts_with": "starts_with",
    "ends_with": "ends_with",
    "matches": "matches",
    "is_empty": "is_empty",
    "not_empty": "not_empty",
    "length_eq": "length_eq", "length_equals": "length_eq",
    "length_gt": "length_gt", "length_greater": "length_gt",
    "length_lt": "length_lt", "length_less": "length_lt",
    "has_key": "has_key", "has_field": "has_key",
    "type_eq": "type_eq", "type_equals": "type_eq",
    "in": "in",
    "between": "between",
    "not_matches": "not_matches",
    "not_in": "not_in",
    "not_has_key": "not_has_key",
    "length_gte": "length_gte",
    "length_lte": "length_lte",
}


class AssertionResult(BaseModel):
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


class BaseAssertion(ABC):
    def __init__(self, variable_manager=None, extractor_engine=None):
        self.variable_manager = variable_manager
        self.extractor_engine = extractor_engine

    @abstractmethod
    async def execute(self, assertion: dict, context: dict) -> AssertionResult:
        pass

    def _get_config(self, assertion: dict) -> dict:
        return assertion.get("config", {})

    def _resolve_expression(self, expression: str) -> str:
        if self.variable_manager and expression:
            return self.variable_manager.resolve(expression)
        return expression or ""

    def _normalize_operator(self, raw_operator: str) -> str:
        return OPERATOR_ALIASES.get(raw_operator, raw_operator)

    def _compare(self, actual: Any, expected: Any, operator: str) -> bool:
        normalized = self._normalize_operator(operator)
        try:
            if normalized == "eq":
                return actual == expected
            elif normalized == "neq":
                return actual != expected
            elif normalized == "contains":
                return str(expected) in str(actual)
            elif normalized == "not_contains":
                return str(expected) not in str(actual)
            elif normalized == "starts_with":
                return str(actual).startswith(str(expected))
            elif normalized == "ends_with":
                return str(actual).endswith(str(expected))
            elif normalized == "gt":
                return float(actual) > float(expected)
            elif normalized == "lt":
                return float(actual) < float(expected)
            elif normalized == "gte":
                return float(actual) >= float(expected)
            elif normalized == "lte":
                return float(actual) <= float(expected)
            elif normalized == "in":
                return actual in (expected if isinstance(expected, list) else [expected])
            elif normalized == "between":
                if isinstance(expected, (list, tuple)) and len(expected) == 2:
                    return float(expected[0]) <= float(actual) <= float(expected[1])
                return False
            elif normalized == "matches":
                return bool(re.search(str(expected), str(actual)))
            elif normalized == "is_empty":
                return not actual
            elif normalized == "not_empty":
                return bool(actual)
            elif normalized == "length_eq":
                return len(actual if hasattr(actual, '__len__') else str(actual)) == int(expected)
            elif normalized == "length_gt":
                return len(actual if hasattr(actual, '__len__') else str(actual)) > int(expected)
            elif normalized == "length_lt":
                return len(actual if hasattr(actual, '__len__') else str(actual)) < int(expected)
            elif normalized == "has_key":
                if isinstance(actual, dict):
                    return str(expected) in actual
                return False
            elif normalized == "type_eq":
                type_map = {"string": str, "integer": int, "float": float, "boolean": bool, "list": list, "dict": dict, "null": type(None)}
                expected_type = type_map.get(str(expected), str)
                return isinstance(actual, expected_type)
            elif normalized == "not_matches":
                return not bool(re.search(str(expected), str(actual)))
            elif normalized == "not_in":
                return actual not in (expected if isinstance(expected, list) else [expected])
            elif normalized == "not_has_key":
                if isinstance(actual, dict):
                    return str(expected) not in actual
                return True
            elif normalized == "length_gte":
                return len(actual if hasattr(actual, '__len__') else str(actual)) >= int(expected)
            elif normalized == "length_lte":
                return len(actual if hasattr(actual, '__len__') else str(actual)) <= int(expected)
            logger.warning(f"Unknown operator: {operator} (normalized: {normalized})")
            return False
        except (ValueError, TypeError) as e:
            logger.warning(f"Comparison error for operator={operator}, actual={actual}, expected={expected}: {e}")
            return False

    def _operator_label(self, operator: str) -> str:
        labels = {
            "eq": "等于", "neq": "不等于", "gt": "大于", "lt": "小于",
            "gte": "大于等于", "lte": "小于等于", "contains": "包含",
            "not_contains": "不包含", "starts_with": "开头为", "ends_with": "结尾为",
            "matches": "匹配正则", "is_empty": "为空", "not_empty": "不为空",
            "length_eq": "长度等于", "length_gt": "长度大于", "length_lt": "长度小于",
            "has_key": "包含字段", "type_eq": "类型为", "in": "在列表中",
            "between": "在范围内",
            "not_matches": "不匹配正则",
            "not_in": "不在列表中",
            "not_has_key": "不包含字段",
            "length_gte": "长度大于等于",
            "length_lte": "长度小于等于",
        }
        return labels.get(operator, operator)
