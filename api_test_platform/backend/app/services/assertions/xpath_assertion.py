from typing import Any
from app.services.assertions.base_assertion import BaseAssertion, AssertionResult
from app.services.extractors.base_extractor import ExtractConfig


class XPathAssertion(BaseAssertion):
    async def execute(self, assertion: dict, context: dict) -> AssertionResult:
        import time
        start = time.monotonic()
        config = self._get_config(assertion)
        try:
            response_data = context.get("response_data", {})
            expression = config.get("expression", "")
            expected = config.get("expected", "")
            operator = config.get("operator", "equals")
            use_tidy = config.get("use_tidy", True)
            use_namespaces = config.get("use_namespaces", False)
            validate_xml = config.get("validate_xml", False)
            true_if_no_match = config.get("true_if_no_match", False)
            message = config.get("message", "")
            severity = config.get("severity", "critical")
            if not self.extractor_engine:
                return AssertionResult(
                    id=assertion.get("id", ""),
                    name=assertion.get("name", ""),
                    type="xpath",
                    passed=False,
                    message="No extractor engine available",
                    severity=severity,
                    duration_ms=int((time.monotonic() - start) * 1000),
                )
            extract_config = ExtractConfig(
                extract_type="xpath",
                expression=expression,
                use_tidy=use_tidy,
                use_namespaces=use_namespaces,
                validate_xml=validate_xml,
            )
            body = response_data.get("body", "")
            result = self.extractor_engine.extract(body, extract_config)
            if not result.success:
                if true_if_no_match:
                    return AssertionResult(
                        id=assertion.get("id", ""),
                        name=assertion.get("name", ""),
                        type="xpath",
                        passed=True,
                        actual=None,
                        expected=expected,
                        operator=operator,
                        message=message or f"XPath无匹配(允许通过): {expression}",
                        severity=severity,
                        duration_ms=int((time.monotonic() - start) * 1000),
                    )
                return AssertionResult(
                    id=assertion.get("id", ""),
                    name=assertion.get("name", ""),
                    type="xpath",
                    passed=False,
                    actual=None,
                    expected=expected,
                    operator=operator,
                    message=message or f"XPath提取失败: {expression}",
                    severity=severity,
                    duration_ms=int((time.monotonic() - start) * 1000),
                )
            actual = result.value
            if not expected:
                return AssertionResult(
                    id=assertion.get("id", ""),
                    name=assertion.get("name", ""),
                    type="xpath",
                    passed=True,
                    actual=actual,
                    expected=None,
                    operator=operator,
                    message=message or f"XPath路径存在: {expression}",
                    severity=severity,
                    duration_ms=int((time.monotonic() - start) * 1000),
                )
            passed = self._compare(actual, expected, operator)
            if not message:
                message = f"XPath断言{'通过' if passed else '失败'}: {expression}={actual}, 期望{operator} {expected}"
            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="xpath",
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
                type="xpath",
                passed=False,
                message=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )
