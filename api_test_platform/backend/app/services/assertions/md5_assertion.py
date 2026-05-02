import hashlib
from typing import Any
from app.services.assertions.base_assertion import BaseAssertion, AssertionResult


class MD5Assertion(BaseAssertion):
    async def execute(self, assertion: dict, context: dict) -> AssertionResult:
        import time
        start = time.monotonic()
        config = self._get_config(assertion)
        try:
            response_data = context.get("response_data", {})
            expected_md5 = config.get("expected_md5", "")
            message = config.get("message", "")
            severity = config.get("severity", "critical")
            body = response_data.get("body", "")
            actual_md5 = hashlib.md5(body.encode('utf-8') if isinstance(body, str) else body).hexdigest()
            passed = actual_md5 == expected_md5
            if not message:
                message = f"MD5断言{'通过' if passed else '失败'}: 实际={actual_md5}, 期望={expected_md5}"
            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="md5",
                passed=passed,
                actual=actual_md5,
                expected=expected_md5,
                operator="equals",
                message=message,
                severity=severity,
                duration_ms=int((time.monotonic() - start) * 1000),
            )
        except Exception as e:
            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="md5",
                passed=False,
                message=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )
