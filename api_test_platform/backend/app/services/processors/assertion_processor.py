from typing import Any, Dict, List
from app.services.processors.base_processor import BaseProcessor, ActionResult


class AssertionProcessor(BaseProcessor):
    async def execute(self, action: Dict[str, Any], context: Dict[str, Any]) -> ActionResult:
        import time
        start = time.monotonic()
        config = self._get_config(action)
        try:
            assertions = config.get("assertions", [])
            response_data = context.get("response_data", {})
            results: List[Dict[str, Any]] = []
            all_passed = True
            for asrt in assertions:
                asrt_type = asrt.get("type", "status_code")
                operator = asrt.get("operator", "eq")
                expected = asrt.get("expected")
                path = asrt.get("path", "")
                message = asrt.get("message", "")
                actual = self._get_actual_value(asrt_type, path, response_data, context)
                passed = self._compare(actual, expected, operator)
                if not passed:
                    all_passed = False
                results.append({
                    "type": asrt_type,
                    "path": path,
                    "operator": operator,
                    "expected": expected,
                    "actual": actual,
                    "passed": passed,
                    "message": message or self._build_message(asrt_type, operator, expected, actual, passed),
                })
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type="assertion",
                success=all_passed,
                duration_ms=int((time.monotonic() - start) * 1000),
                output={"assertions": results, "passed": sum(1 for r in results if r["passed"]), "failed": sum(1 for r in results if not r["passed"])},
                error=None if all_passed else f"{sum(1 for r in results if not r['passed'])} assertion(s) failed",
            )
        except Exception as e:
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type="assertion",
                success=False,
                error=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )

    def _get_actual_value(self, asrt_type: str, path: str, response_data: Dict, context: Dict) -> Any:
        if asrt_type == "status_code":
            return response_data.get("status_code", 0)
        elif asrt_type == "jsonpath":
            if not path or not self.extractor_engine:
                return None
            from app.services.extractors.base_extractor import ExtractConfig
            result = self.extractor_engine.extract_from_response(
                response_data, "body", ExtractConfig(extract_type="jsonpath", expression=path)
            )
            return result.value if result.success else None
        elif asrt_type == "header":
            headers = response_data.get("headers", {})
            if path:
                return headers.get(path, headers.get(path.lower(), ""))
            return headers
        elif asrt_type == "response_time":
            return response_data.get("elapsed_ms", 0)
        elif asrt_type == "body_contains":
            body = response_data.get("body", "")
            return body
        elif asrt_type == "regex":
            body = response_data.get("body", "")
            return body
        elif asrt_type == "json_schema":
            body = response_data.get("body", "")
            return body
        elif asrt_type == "script":
            return None
        return None

    def _compare(self, actual: Any, expected: Any, operator: str) -> bool:
        try:
            if operator == "eq":
                return actual == expected
            elif operator == "neq":
                return actual != expected
            elif operator == "gt":
                return float(actual) > float(expected)
            elif operator == "lt":
                return float(actual) < float(expected)
            elif operator == "gte":
                return float(actual) >= float(expected)
            elif operator == "lte":
                return float(actual) <= float(expected)
            elif operator == "contains":
                return str(expected) in str(actual)
            elif operator == "not_contains":
                return str(expected) not in str(actual)
            elif operator == "starts_with":
                return str(actual).startswith(str(expected))
            elif operator == "ends_with":
                return str(actual).endswith(str(expected))
            elif operator == "matches":
                import re
                return bool(re.search(str(expected), str(actual)))
            elif operator == "is_empty":
                return not actual
            elif operator == "not_empty":
                return bool(actual)
            elif operator == "length_eq":
                return len(actual if hasattr(actual, '__len__') else str(actual)) == int(expected)
            elif operator == "length_gt":
                return len(actual if hasattr(actual, '__len__') else str(actual)) > int(expected)
            elif operator == "length_lt":
                return len(actual if hasattr(actual, '__len__') else str(actual)) < int(expected)
            elif operator == "in":
                return actual in (expected if isinstance(expected, list) else [expected])
            elif operator == "between":
                if isinstance(expected, (list, tuple)) and len(expected) == 2:
                    return float(expected[0]) <= float(actual) <= float(expected[1])
                return False
            elif operator == "type_eq":
                type_map = {"string": str, "integer": int, "float": float, "boolean": bool, "list": list, "dict": dict, "null": type(None)}
                expected_type = type_map.get(str(expected), str)
                return isinstance(actual, expected_type)
            elif operator == "has_key":
                if isinstance(actual, dict):
                    return str(expected) in actual
                return False
            return False
        except (ValueError, TypeError):
            return False

    def _build_message(self, asrt_type: str, operator: str, expected: Any, actual: Any, passed: bool) -> str:
        op_labels = {
            "eq": "等于", "neq": "不等于", "gt": "大于", "lt": "小于",
            "gte": "大于等于", "lte": "小于等于", "contains": "包含",
            "not_contains": "不包含", "matches": "匹配正则",
            "is_empty": "为空", "not_empty": "不为空",
        }
        if passed:
            return f"断言通过: {asrt_type} {op_labels.get(operator, operator)} {expected}"
        return f"断言失败: 期望 {expected}, 实际 {actual}"
