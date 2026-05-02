from typing import Any
from app.services.assertions.base_assertion import BaseAssertion, AssertionResult


class SizeAssertion(BaseAssertion):
    async def execute(self, assertion: dict, context: dict) -> AssertionResult:
        import time
        start = time.monotonic()
        config = self._get_config(assertion)
        try:
            response_data = context.get("response_data", {})
            field = config.get("field", "response_body")
            operator = config.get("operator", "less_than")
            expected = config.get("expected", 10240)
            unit = config.get("unit", "byte")
            message = config.get("message", "")
            severity = config.get("severity", "critical")
            field_map = {
                "response_body": len(response_data.get("body", "").encode('utf-8')) if response_data.get("body") else 0,
                "response_headers": len(str(response_data.get("headers", {})).encode('utf-8')),
                "response_code": len(str(response_data.get("status_code", ""))),
                "request_data": len(str(context.get("request_body", "")).encode('utf-8')),
            }
            actual_bytes = field_map.get(field, 0)
            if unit == "kb":
                actual = actual_bytes / 1024.0
            elif unit == "mb":
                actual = actual_bytes / (1024.0 * 1024.0)
            else:
                actual = actual_bytes
            passed = self._compare(actual, expected, operator)
            if not message:
                message = f"大小断言{'通过' if passed else '失败'}: 实际={actual:.2f}{unit}, 期望{operator} {expected}{unit}"
            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="size",
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
                type="size",
                passed=False,
                message=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )
