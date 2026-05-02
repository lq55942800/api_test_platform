import asyncio
import re
from typing import Any, Dict
from app.core.logging import get_logger
from app.services.processors.base_processor import BaseProcessor, ActionResult

logger = get_logger(__name__)

_JS_LITERAL_PATTERN = re.compile(
    r'(?<![a-zA-Z0-9_])'
    r'(?:true|false|null)'
    r'(?![a-zA-Z0-9_])'
)

_JS_TO_PYTHON = {
    'true': 'True',
    'false': 'False',
    'null': 'None',
}

_STRING_PATTERN = re.compile(
    r'(?:'
    r'"""[\s\S]*?"""'
    r"|'''[\s\S]*?'''"
    r'|"(?:[^"\\]|\\.)*"'
    r"|'(?:[^'\\]|\\.)*'"
    r')'
)


def _normalize_js_literals(script: str) -> str:
    parts = []
    last_end = 0
    for m in _STRING_PATTERN.finditer(script):
        if m.start() > last_end:
            chunk = script[last_end:m.start()]
            parts.append(_JS_LITERAL_PATTERN.sub(
                lambda x: _JS_TO_PYTHON.get(x.group(0), x.group(0)), chunk
            ))
        parts.append(m.group(0))
        last_end = m.end()
    if last_end < len(script):
        chunk = script[last_end:]
        parts.append(_JS_LITERAL_PATTERN.sub(
            lambda x: _JS_TO_PYTHON.get(x.group(0), x.group(0)), chunk
        ))
    return ''.join(parts) if parts else _JS_LITERAL_PATTERN.sub(
        lambda x: _JS_TO_PYTHON.get(x.group(0), x.group(0)), script
    )


class ScriptContext:
    def __init__(self, variable_manager=None, context: Dict = None):
        self._variable_manager = variable_manager
        self._context = context or {}
        self._logs = []

    def get_variable(self, name: str, scope: str = None) -> Any:
        if self._variable_manager:
            return self._variable_manager.get(name, scope)
        return None

    def set_variable(self, name: str, value: Any, scope: str = "temp") -> None:
        if self._variable_manager:
            self._variable_manager.set(name, value, scope)

    def delete_variable(self, name: str, scope: str = None) -> None:
        if self._variable_manager:
            self._variable_manager.delete(name, scope)

    def get_request_header(self, name: str) -> str:
        headers = self._context.get("request_params", {}).get("header", {})
        return headers.get(name, "")

    def set_request_header(self, name: str, value: str) -> None:
        headers = self._context.setdefault("request_params", {}).setdefault("header", {})
        headers[name] = value

    def get_request_param(self, name: str, location: str = "body") -> Any:
        params = self._context.get("request_params", {}).get(location, {})
        return params.get(name)

    def set_request_param(self, name: str, value: Any, location: str = "body") -> None:
        params = self._context.setdefault("request_params", {}).setdefault(location, {})
        params[name] = value

    def get_request_body(self) -> Any:
        return self._context.get("request_params", {}).get("body")

    def set_request_body(self, data: Any) -> None:
        self._context.setdefault("request_params", {})["body"] = data

    def get_request_url(self) -> str:
        return self._context.get("url", "")

    def set_request_url(self, url: str) -> None:
        self._context["url"] = url

    def get_request_method(self) -> str:
        return self._context.get("method", "")

    def get_request_headers(self) -> Dict[str, str]:
        return self._context.get("request_params", {}).get("header", {})

    def log(self, message: str, level: str = "info") -> None:
        self._logs.append({"level": level, "message": str(message)})

    def get_response_status_code(self) -> int:
        return self._context.get("response_data", {}).get("status_code", 0)

    def get_response_headers(self) -> Dict[str, str]:
        return self._context.get("response_data", {}).get("headers", {})

    def get_response_header(self, name: str) -> str:
        return self.get_response_headers().get(name, "")

    def get_response_body(self) -> str:
        return self._context.get("response_data", {}).get("body", "")

    def get_response_body_json(self) -> Any:
        import json
        body = self.get_response_body()
        try:
            return json.loads(body) if body else None
        except json.JSONDecodeError:
            return None

    def get_response_time(self) -> float:
        return self._context.get("response_data", {}).get("elapsed_ms", 0)

    def get_response_size(self) -> int:
        body = self.get_response_body()
        return len(body.encode('utf-8')) if body else 0

    def get_response_cookies(self) -> Dict[str, str]:
        return self._context.get("response_data", {}).get("cookies", {})


class ScriptProcessor(BaseProcessor):
    async def execute(self, action: Dict[str, Any], context: Dict[str, Any]) -> ActionResult:
        import time
        start = time.monotonic()
        config = self._get_config(action)
        action_id = action.get("id", "")
        action_name = action.get("name", "")
        logger.info(f"ScriptProcessor executing: action_id={action_id}, action_name={action_name}")
        try:
            script = config.get("script", "")
            timeout = config.get("timeout", 10000)
            if not script.strip():
                logger.debug(f"Script is empty, skipping execution: action_id={action_id}")
                return ActionResult(
                    id=action_id,
                    name=action_name,
                    type="script",
                    success=True,
                    duration_ms=int((time.monotonic() - start) * 1000),
                    output={"logs": []},
                )
            logger.debug(f"Script execution starting: action_id={action_id}, script_length={len(script)}, timeout={timeout}ms")
            normalized_script = _normalize_js_literals(script)
            wrapped_script = f"def __user_execute__(context):\n" + "\n".join(
                "    " + line for line in normalized_script.split("\n")
            ) + "\n__result__ = __user_execute__(context)"
            script_context = ScriptContext(self.variable_manager, context)
            local_ns = {"context": script_context, "__builtins__": __builtins__}
            try:
                result = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None, lambda: self._exec_script(wrapped_script, local_ns)
                    ),
                    timeout=timeout / 1000.0,
                )
            except asyncio.TimeoutError:
                logger.error(f"Script execution timeout: action_id={action_id}, timeout={timeout}ms")
                return ActionResult(
                    id=action_id,
                    name=action_name,
                    type="script",
                    success=False,
                    error=f"Script execution timeout ({timeout}ms)",
                    duration_ms=int((time.monotonic() - start) * 1000),
                )
            logger.info(f"Script execution completed: action_id={action_id}, duration_ms={int((time.monotonic() - start) * 1000)}")
            logger.debug(f"Script logs: action_id={action_id}, log_count={len(script_context._logs)}")
            return ActionResult(
                id=action_id,
                name=action_name,
                type="script",
                success=True,
                duration_ms=int((time.monotonic() - start) * 1000),
                output={"logs": script_context._logs},
            )
        except Exception as e:
            logger.error(f"ScriptProcessor error: action_id={action_id}, error={str(e)}", exc_info=True)
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type="script",
                success=False,
                error=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )

    def _exec_script(self, script: str, local_ns: Dict) -> Any:
        logger.debug(f"Executing script in executor")
        exec(script, local_ns)
