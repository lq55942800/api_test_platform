import json
from typing import Any
from app.services.assertions.base_assertion import BaseAssertion, AssertionResult


class JSONSchemaAssertion(BaseAssertion):
    async def execute(self, assertion: dict, context: dict) -> AssertionResult:
        import time
        start = time.monotonic()
        config = self._get_config(assertion)
        try:
            response_data = context.get("response_data", {})
            schema_source = config.get("schema_source", "inline")
            message = config.get("message", "")
            severity = config.get("severity", "critical")
            body = response_data.get("body", "")
            try:
                body_data = json.loads(body) if isinstance(body, str) else body
            except json.JSONDecodeError:
                return AssertionResult(
                    id=assertion.get("id", ""),
                    name=assertion.get("name", ""),
                    type="json_schema",
                    passed=False,
                    message="响应体不是有效的JSON",
                    severity=severity,
                    duration_ms=int((time.monotonic() - start) * 1000),
                )
            schema = None
            if schema_source == "inline":
                schema_str = config.get("schema_text") or config.get("schema")
                if schema_str:
                    try:
                        schema = json.loads(schema_str) if isinstance(schema_str, str) else schema_str
                    except json.JSONDecodeError:
                        return AssertionResult(
                            id=assertion.get("id", ""),
                            name=assertion.get("name", ""),
                            type="json_schema",
                            passed=False,
                            message="JSON Schema文本格式错误，不是有效的JSON",
                            severity=severity,
                            duration_ms=int((time.monotonic() - start) * 1000),
                        )
            elif schema_source == "file":
                import os
                schema_file = config.get("schema_file", "")
                if os.path.exists(schema_file):
                    with open(schema_file, 'r', encoding='utf-8') as f:
                        schema = json.load(f)
                else:
                    return AssertionResult(
                        id=assertion.get("id", ""),
                        name=assertion.get("name", ""),
                        type="json_schema",
                        passed=False,
                        message=f"Schema文件不存在: {schema_file}",
                        severity=severity,
                        duration_ms=int((time.monotonic() - start) * 1000),
                    )
            elif schema_source == "url":
                import httpx
                schema_url = config.get("schema_url", "")
                async with httpx.AsyncClient() as client:
                    resp = await client.get(schema_url)
                    schema = resp.json()
            if not schema:
                return AssertionResult(
                    id=assertion.get("id", ""),
                    name=assertion.get("name", ""),
                    type="json_schema",
                    passed=False,
                    message="未提供JSON Schema",
                    severity=severity,
                    duration_ms=int((time.monotonic() - start) * 1000),
                )
            import jsonschema
            try:
                jsonschema.validate(instance=body_data, schema=schema)
                passed = True
                error_detail = ""
            except jsonschema.ValidationError as e:
                passed = False
                error_detail = str(e.message)
            if not message:
                message = f"JSON Schema断言{'通过' if passed else '失败'}" + (f": {error_detail}" if error_detail else "")
            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="json_schema",
                passed=passed,
                actual="body_data",
                expected="schema",
                message=message,
                severity=severity,
                duration_ms=int((time.monotonic() - start) * 1000),
            )
        except Exception as e:
            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="json_schema",
                passed=False,
                message=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )
