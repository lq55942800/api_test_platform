from typing import Any
from app.services.assertions.base_assertion import BaseAssertion, AssertionResult, OPERATOR_ALIASES


class ResponseTimeAssertion(BaseAssertion):
    async def execute(self, assertion: dict, context: dict) -> AssertionResult:
        import time
        start = time.monotonic()
        config = self._get_config(assertion)
        try:
            response_data = context.get("response_data", {})
            actual = response_data.get("elapsed_ms", 0)
            raw_operator = config.get("operator", "lt")
            operator = OPERATOR_ALIASES.get(raw_operator, "lt")
            expected = config.get("expected", 1000)
            message = config.get("message", "")
            severity = config.get("severity", "critical")

            if operator == "between":
                expected_min = config.get("expected_min", 0)
                expected_max = config.get("expected_max", 0)
                passed = float(expected_min) <= float(actual) <= float(expected_max)
                expected = f"{expected_min}-{expected_max}"
            else:
                passed = self._compare(actual, expected, operator)

            if not message:
                message = f"响应时间断言{'通过' if passed else '失败'}: 实际={actual}ms, 期望{self._operator_label(operator)} {expected}ms"

            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="response_time",
                passed=passed,
                actual=actual,
                expected=expected,
                operator=operator,
                message=message,
                severity=severity,
                duration_ms=int((time.monotonic() - start) * 1000),
            )
        except Exception as e:
            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="response_time",
                passed=False,
                message=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )
