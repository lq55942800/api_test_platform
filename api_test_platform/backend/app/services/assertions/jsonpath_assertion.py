import logging
import time
from typing import Any
from app.services.assertions.base_assertion import BaseAssertion, AssertionResult, OPERATOR_ALIASES
from app.services.extractors.base_extractor import ExtractConfig

logger = logging.getLogger(__name__)


class JSONPathAssertion(BaseAssertion):
    async def execute(self, assertion: dict, context: dict) -> AssertionResult:
        start = time.monotonic()
        config = self._get_config(assertion)
        try:
            response_data = context.get("response_data", {})
            expression = config.get("expression", "")
            assert_value = config.get("assert_value", True)
            raw_operator = config.get("operator", "eq")
            operator = OPERATOR_ALIASES.get(raw_operator, "eq")
            expected = config.get("expected")
            message = config.get("message", "")
            severity = config.get("severity", "critical")

            if not expression:
                return AssertionResult(
                    id=assertion.get("id", ""),
                    name=assertion.get("name", ""),
                    type="jsonpath",
                    passed=False,
                    message="JSONPath表达式不能为空",
                    severity=severity,
                    duration_ms=int((time.monotonic() - start) * 1000),
                )

            if not self.extractor_engine:
                return AssertionResult(
                    id=assertion.get("id", ""),
                    name=assertion.get("name", ""),
                    type="jsonpath",
                    passed=False,
                    message="提取引擎不可用",
                    severity=severity,
                    duration_ms=int((time.monotonic() - start) * 1000),
                )

            extract_config = ExtractConfig(
                extract_type="jsonpath",
                expression=expression,
            )
            body = response_data.get("body", "")
            result = self.extractor_engine.extract(body, extract_config)

            if not result.success:
                msg = f"JSONPath路径不存在: {expression}"
                if not message:
                    message = msg
                logger.debug(f"JSONPath assertion: path not found, expression={expression}")
                return AssertionResult(
                    id=assertion.get("id", ""),
                    name=assertion.get("name", ""),
                    type="jsonpath",
                    passed=False,
                    actual=None,
                    expected=expected,
                    operator=operator,
                    message=message,
                    severity=severity,
                    duration_ms=int((time.monotonic() - start) * 1000),
                )

            actual = result.value

            if not assert_value:
                passed = True
                if not message:
                    message = f"JSONPath路径存在: {expression}, 值={actual}"
                return AssertionResult(
                    id=assertion.get("id", ""),
                    name=assertion.get("name", ""),
                    type="jsonpath",
                    passed=passed,
                    actual=actual,
                    expected=expected,
                    operator=operator,
                    message=message,
                    severity=severity,
                    duration_ms=int((time.monotonic() - start) * 1000),
                )

            passed = self._compare(actual, expected, operator)

            if not message:
                status = "通过" if passed else "失败"
                message = f"JSONPath断言{status}: {expression}={actual}, 期望{self._operator_label(operator)} {expected}"

            duration_ms = int((time.monotonic() - start) * 1000)
            logger.debug(f"JSONPath assertion: expression={expression}, actual={actual}, operator={operator}, expected={expected}, passed={passed}, duration={duration_ms}ms")

            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="jsonpath",
                passed=passed,
                actual=actual,
                expected=expected,
                operator=operator,
                message=message,
                severity=severity,
                duration_ms=duration_ms,
            )
        except Exception as e:
            logger.error(f"JSONPath assertion error: {e}")
            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="jsonpath",
                passed=False,
                message=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )
