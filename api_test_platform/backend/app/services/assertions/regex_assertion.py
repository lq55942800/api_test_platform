import re
from typing import Any
from app.services.assertions.base_assertion import BaseAssertion, AssertionResult


class RegexAssertion(BaseAssertion):
    async def execute(self, assertion: dict, context: dict) -> AssertionResult:
        import time
        start = time.monotonic()
        config = self._get_config(assertion)
        try:
            response_data = context.get("response_data", {})
            source = config.get("source", "body")
            pattern = config.get("pattern", "")
            match_rule = config.get("match_rule", "contains")
            message = config.get("message", "")
            severity = config.get("severity", "critical")
            source_map = {
                "body": response_data.get("body", ""),
                "header": str(response_data.get("headers", {})),
                "status_code": str(response_data.get("status_code", "")),
                "url": response_data.get("url", ""),
            }
            source_text = source_map.get(source, response_data.get("body", ""))
            compiled = re.compile(pattern, re.DOTALL)
            search_result = compiled.search(source_text)
            if match_rule == "contains":
                passed = bool(search_result)
            elif match_rule == "matches":
                passed = bool(compiled.fullmatch(source_text))
            elif match_rule == "not_contains":
                passed = not bool(search_result)
            elif match_rule == "not_matches":
                passed = not bool(compiled.fullmatch(source_text))
            else:
                passed = False
            actual = search_result.group(0) if search_result else None
            if not message:
                message = f"正则断言{'通过' if passed else '失败'}: 规则={match_rule}, 模式={pattern}"
            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="regex",
                passed=passed,
                actual=actual,
                expected=pattern,
                operator=match_rule,
                message=message,
                severity=severity,
                duration_ms=int((time.monotonic() - start) * 1000),
            )
        except re.error as e:
            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="regex",
                passed=False,
                message=f"正则表达式错误: {e}",
                duration_ms=int((time.monotonic() - start) * 1000),
            )
        except Exception as e:
            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="regex",
                passed=False,
                message=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )
