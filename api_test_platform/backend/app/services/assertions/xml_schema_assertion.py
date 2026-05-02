from typing import Any
from app.services.assertions.base_assertion import BaseAssertion, AssertionResult


class XMLSchemaAssertion(BaseAssertion):
    async def execute(self, assertion: dict, context: dict) -> AssertionResult:
        import time
        start = time.monotonic()
        config = self._get_config(assertion)
        try:
            response_data = context.get("response_data", {})
            schema_source = config.get("schema_source", "file")
            message = config.get("message", "")
            severity = config.get("severity", "critical")
            body = response_data.get("body", "")
            from lxml import etree
            try:
                xml_doc = etree.fromstring(body.encode('utf-8') if isinstance(body, str) else body)
            except etree.XMLSyntaxError as e:
                return AssertionResult(
                    id=assertion.get("id", ""),
                    name=assertion.get("name", ""),
                    type="xml_schema",
                    passed=False,
                    message=f"响应体不是有效的XML: {e}",
                    severity=severity,
                    duration_ms=int((time.monotonic() - start) * 1000),
                )
            schema = None
            if schema_source == "file":
                import os
                schema_file = config.get("schema_file", "")
                if os.path.exists(schema_file):
                    schema_doc = etree.parse(schema_file)
                    schema = etree.XMLSchema(schema_doc)
                else:
                    return AssertionResult(
                        id=assertion.get("id", ""),
                        name=assertion.get("name", ""),
                        type="xml_schema",
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
                    schema_doc = etree.fromstring(resp.content)
                    schema = etree.XMLSchema(etree.ElementTree(schema_doc))
            if not schema:
                return AssertionResult(
                    id=assertion.get("id", ""),
                    name=assertion.get("name", ""),
                    type="xml_schema",
                    passed=False,
                    message="未提供XML Schema",
                    severity=severity,
                    duration_ms=int((time.monotonic() - start) * 1000),
                )
            passed = schema.validate(xml_doc)
            if not passed:
                error_detail = "\n".join(str(e) for e in schema.error_log)
            else:
                error_detail = ""
            if not message:
                message = f"XML Schema断言{'通过' if passed else '失败'}" + (f": {error_detail}" if error_detail else "")
            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="xml_schema",
                passed=passed,
                actual="XML" + ("符合" if passed else "不符合") + "Schema",
                expected="符合Schema定义",
                message=message,
                severity=severity,
                duration_ms=int((time.monotonic() - start) * 1000),
            )
        except Exception as e:
            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="xml_schema",
                passed=False,
                message=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )
