from typing import Any
from app.services.assertions.base_assertion import BaseAssertion, AssertionResult


class HeaderAssertion(BaseAssertion):
    async def execute(self, assertion: dict, context: dict) -> AssertionResult:
        import time
        start = time.monotonic()
        config = self._get_config(assertion)
        try:
            response_data = context.get("response_data", {})
            headers = response_data.get("headers", {})
            header_name = config.get("header_name", "")
            operator = config.get("operator", "contains")
            expected = config.get("expected", "")
            message = config.get("message", "")
            severity = config.get("severity", "critical")
            actual = None
            for key, value in headers.items():
                if key.lower() == header_name.lower():
                    actual = value
                    break
            if actual is None:
                normalized_op = self._normalize_operator(operator)
                passed = normalized_op in ("neq", "not_contains", "is_empty")
                if not message:
                    message = f"响应头 {header_name} 不存在"
            else:
                passed = self._compare(actual, expected, operator)
                if not message:
                    message = f"响应头断言{'通过' if passed else '失败'}: {header_name}={actual}, 期望{operator} {expected}"
            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="header",
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
                type="header",
                passed=False,
                message=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )
