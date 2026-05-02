from typing import Any, Dict
from app.services.processors.base_processor import BaseProcessor, ActionResult


class HeaderProcessor(BaseProcessor):
    async def execute(self, action: Dict[str, Any], context: Dict[str, Any]) -> ActionResult:
        import time
        start = time.monotonic()
        config = self._get_config(action)
        try:
            merge_action = config.get("action", "merge")
            headers = config.get("headers", [])
            request_params = context.setdefault("request_params", {})
            header_params = request_params.setdefault("header", {})
            applied = {}
            if merge_action == "replace":
                header_params.clear()
            for h in headers:
                if not h.get("enabled", True):
                    continue
                name = h.get("name", "")
                value = h.get("value", "")
                if name:
                    resolved_value = self._resolve_expression(value)
                    if merge_action == "append" and name in header_params:
                        existing = header_params[name]
                        header_params[name] = f"{existing}, {resolved_value}"
                    else:
                        header_params[name] = resolved_value
                    applied[name] = resolved_value
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type="header_modifier",
                success=True,
                duration_ms=int((time.monotonic() - start) * 1000),
                output={"action": merge_action, "headers_applied": applied},
            )
        except Exception as e:
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type="header_modifier",
                success=False,
                error=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )
