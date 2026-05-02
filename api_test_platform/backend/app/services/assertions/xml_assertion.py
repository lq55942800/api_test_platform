from typing import Any
from app.services.assertions.base_assertion import BaseAssertion, AssertionResult


class XMLAssertion(BaseAssertion):
    async def execute(self, assertion: dict, context: dict) -> AssertionResult:
        import time
        start = time.monotonic()
        config = self._get_config(assertion)
        try:
            response_data = context.get("response_data", {})
            message = config.get("message", "")
            severity = config.get("severity", "critical")
            body = response_data.get("body", "")
            try:
                from lxml import etree
                etree.fromstring(body.encode('utf-8') if isinstance(body, str) else body)
                passed = True
            except Exception as e:
                passed = False
                if not message:
                    message = f"XML格式验证失败: {e}"
            if passed and not message:
                message = "XML格式验证通过"
            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="xml",
                passed=passed,
                actual="XML格式" + ("正确" if passed else "错误"),
                expected="格式正确的XML",
                message=message,
                severity=severity,
                duration_ms=int((time.monotonic() - start) * 1000),
            )
        except Exception as e:
            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="xml",
                passed=False,
                message=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )
