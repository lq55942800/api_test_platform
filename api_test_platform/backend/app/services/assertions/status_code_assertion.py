import logging
import time
from typing import Any
from app.services.assertions.base_assertion import BaseAssertion, AssertionResult, OPERATOR_ALIASES

logger = logging.getLogger(__name__)


class StatusCodeAssertion(BaseAssertion):
    async def execute(self, assertion: dict, context: dict) -> AssertionResult:
        start = time.monotonic()
        config = self._get_config(assertion)
        try:
            response_data = context.get("response_data", {})
            actual = response_data.get("status_code", 0)
            raw_operator = config.get("operator", "eq")
            operator = OPERATOR_ALIASES.get(raw_operator, "eq")
            expected = config.get("expected", 200)
            message = config.get("message", "")
            severity = config.get("severity", "critical")

            if operator == "in":
                expected_list = config.get("expected_list", [expected])
                if not isinstance(expected_list, list):
                    expected_list = [expected_list]
                passed = actual in expected_list
            elif operator == "between":
                expected_min = config.get("expected_min", 200)
                expected_max = config.get("expected_max", 300)
                passed = expected_min <= actual <= expected_max
                expected = f"{expected_min}-{expected_max}"
            else:
                passed = self._compare(actual, expected, operator)

            if not message:
                status = "通过" if passed else "失败"
                message = f"状态码断言{status}: 实际={actual}, 期望{self._operator_label(operator)} {expected}"

            duration_ms = int((time.monotonic() - start) * 1000)
            logger.debug(f"StatusCode assertion: actual={actual}, operator={operator}, expected={expected}, passed={passed}, duration={duration_ms}ms")

            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="status_code",
                passed=passed,
                actual=actual,
                expected=expected,
                operator=operator,
                message=message,
                severity=severity,
                duration_ms=duration_ms,
            )
        except Exception as e:
            logger.error(f"StatusCode assertion error: {e}")
            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="status_code",
                passed=False,
                message=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )

    def _operator_label(self, operator: str) -> str:
        labels = {
            "eq": "等于", "neq": "不等于", "gt": "大于", "lt": "小于",
            "gte": "大于等于", "lte": "小于等于", "contains": "包含",
            "not_contains": "不包含", "in": "在列表中", "between": "在范围内",
        }
        return labels.get(operator, operator)
