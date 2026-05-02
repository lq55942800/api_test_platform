import asyncio
from typing import Any
from app.services.assertions.base_assertion import BaseAssertion, AssertionResult
from app.services.processors.script_processor import _normalize_js_literals


class ScriptAssertion(BaseAssertion):
    async def execute(self, assertion: dict, context: dict) -> AssertionResult:
        import time
        start = time.monotonic()
        config = self._get_config(assertion)
        try:
            script = config.get("script", "")
            timeout = config.get("timeout", 10000)
            message = config.get("message", "")
            severity = config.get("severity", "critical")
            if not script.strip():
                return AssertionResult(
                    id=assertion.get("id", ""),
                    name=assertion.get("name", ""),
                    type="script",
                    passed=True,
                    message="Empty script, skipped",
                    severity=severity,
                    duration_ms=int((time.monotonic() - start) * 1000),
                )
            normalized_script = _normalize_js_literals(script)
            wrapped_script = "def __assert_execute__(context):\n" + "\n".join(
                "    " + line for line in normalized_script.split("\n")
            ) + "\n__result__ = __assert_execute__(context)"
            from app.services.processors.script_processor import ScriptContext
            script_context = ScriptContext(self.variable_manager, context)
            local_ns = {
                "context": script_context,
                "AssertionResult": AssertionResult,
                "__builtins__": __builtins__,
            }
            try:
                result = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None, lambda: self._exec_assertion_script(wrapped_script, local_ns)
                    ),
                    timeout=timeout / 1000.0,
                )
                if isinstance(result, AssertionResult):
                    result.id = assertion.get("id", "")
                    result.name = assertion.get("name", "")
                    result.type = "script"
                    result.severity = severity
                    result.duration_ms = int((time.monotonic() - start) * 1000)
                    return result
                passed = bool(result)
                if not message:
                    message = f"Python脚本断言{'通过' if passed else '失败'}"
                return AssertionResult(
                    id=assertion.get("id", ""),
                    name=assertion.get("name", ""),
                    type="script",
                    passed=passed,
                    message=message,
                    severity=severity,
                    duration_ms=int((time.monotonic() - start) * 1000),
                )
            except asyncio.TimeoutError:
                return AssertionResult(
                    id=assertion.get("id", ""),
                    name=assertion.get("name", ""),
                    type="script",
                    passed=False,
                    message=f"脚本执行超时({timeout}ms)",
                    severity=severity,
                    duration_ms=int((time.monotonic() - start) * 1000),
                )
        except Exception as e:
            return AssertionResult(
                id=assertion.get("id", ""),
                name=assertion.get("name", ""),
                type="script",
                passed=False,
                message=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )

    def _exec_assertion_script(self, script: str, local_ns: dict) -> Any:
        exec(script, local_ns)
        if "__result__" in local_ns:
            return local_ns["__result__"]
        return True
