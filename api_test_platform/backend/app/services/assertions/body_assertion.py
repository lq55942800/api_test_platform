import re
import logging
import time
from typing import Any
from app.services.assertions.base_assertion import BaseAssertion, AssertionResult, OPERATOR_ALIASES
from app.services.extractors.base_extractor import ExtractConfig

logger = logging.getLogger(__name__)


class BodyAssertion(BaseAssertion):
    async def execute(self, assertion: dict, context: dict) -> AssertionResult:
        start = time.monotonic()
        config = self._get_config(assertion)
        try:
            response_data = context.get("response_data", {})
            mode = config.get("mode", "contains")
            message = config.get("message", "")
            severity = config.get("severity", "critical")
            body = response_data.get("body", "")

            if mode == "jsonpath":
                return await self._execute_jsonpath(assertion, config, context, body, message, severity, start)
            elif mode == "regex":
                return self._execute_regex(assertion, config, body, message, severity, start)
            else:
                return self._execute_contains(assertion, config, body, message, severity, start)

        except Exception as e:
            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="body",
                passed=False,
                message=str(e),
                severity=config.get("severity", "critical"),
                duration_ms=int((time.monotonic() - start) * 1000),
            )

    async def _execute_jsonpath(self, assertion, config, context, body, message, severity, start):
        expression = config.get("expression", "")
        raw_operator = config.get("operator", "eq")
        operator = OPERATOR_ALIASES.get(raw_operator, "eq")
        expected = config.get("expected")

        if not expression:
            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="body",
                passed=False,
                message="JSONPath表达式不能为空",
                severity=severity,
                duration_ms=int((time.monotonic() - start) * 1000),
            )

        if not self.extractor_engine:
            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="body",
                passed=False,
                message="提取引擎不可用",
                severity=severity,
                duration_ms=int((time.monotonic() - start) * 1000),
            )

        extract_config = ExtractConfig(
            extract_type="jsonpath",
            expression=expression,
        )
        result = self.extractor_engine.extract(body, extract_config)

        if not result.success:
            if not message:
                message = f"JSONPath路径不存在: {expression}"
            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="body",
                passed=False,
                actual=None,
                expected=expected,
                operator=operator,
                message=message,
                severity=severity,
                duration_ms=int((time.monotonic() - start) * 1000),
            )

        actual = result.value
        passed = self._compare(actual, expected, operator)

        if not message:
            status = "通过" if passed else "失败"
            message = f"JSONPath断言{status}: {expression}={actual}, 期望{self._operator_label(operator)} {expected}"

        return AssertionResult(
            id=assertion.get("id", ""),
            name=assertion.get("name", ""),
            type="body",
            passed=passed,
            actual=actual,
            expected=expected,
            operator=operator,
            message=message,
            severity=severity,
            duration_ms=int((time.monotonic() - start) * 1000),
        )

    def _execute_regex(self, assertion, config, body, message, severity, start):
        pattern = config.get("pattern", "")
        match_rule = config.get("match_rule", "contains")

        if not pattern:
            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="body",
                passed=False,
                message="正则表达式不能为空",
                severity=severity,
                duration_ms=int((time.monotonic() - start) * 1000),
            )

        try:
            compiled = re.compile(pattern, re.DOTALL)
        except re.error as e:
            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="body",
                passed=False,
                message=f"正则表达式错误: {e}",
                severity=severity,
                duration_ms=int((time.monotonic() - start) * 1000),
            )

        search_result = compiled.search(body)
        if match_rule == "contains":
            passed = bool(search_result)
        elif match_rule == "not_contains":
            passed = not bool(search_result)
        else:
            passed = bool(search_result)

        actual = search_result.group(0) if search_result else None
        if not message:
            message = f"正则断言{'通过' if passed else '失败'}: 模式={pattern}, 规则={match_rule}"

        return AssertionResult(
            id=assertion.get("id", ""),
            name=assertion.get("name", ""),
            type="body",
            passed=passed,
            actual=actual,
            expected=pattern,
            operator=match_rule,
            message=message,
            severity=severity,
            duration_ms=int((time.monotonic() - start) * 1000),
        )

    def _execute_contains(self, assertion, config, body, message, severity, start):
        expected = config.get("expected", "")

        if not expected:
            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="body",
                passed=False,
                message="期望内容不能为空",
                severity=severity,
                duration_ms=int((time.monotonic() - start) * 1000),
            )

        passed = expected in body

        if not message:
            message = f"包含断言{'通过' if passed else '失败'}: 期望包含 \"{expected}\""

        return AssertionResult(
            id=assertion.get("id", ""),
            name=assertion.get("name", ""),
            type="body",
            passed=passed,
            actual=body[:200] if body else "",
            expected=expected,
            operator="contains",
            message=message,
            severity=severity,
            duration_ms=int((time.monotonic() - start) * 1000),
        )
