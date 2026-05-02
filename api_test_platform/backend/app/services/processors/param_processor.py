from typing import Any, Dict
from app.services.processors.base_processor import BaseProcessor, ActionResult


class ParamProcessor(BaseProcessor):
    async def execute(self, action: Dict[str, Any], context: Dict[str, Any]) -> ActionResult:
        import time
        start = time.monotonic()
        config = self._get_config(action)
        try:
            target_param = config.get("target_param", "")
            target_location = config.get("target_location", "body")
            expression = config.get("expression", "")
            resolved = self._resolve_expression(expression)
            request_params = context.setdefault("request_params", {})
            location_params = request_params.setdefault(target_location, {})
            location_params[target_param] = resolved
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type="param_process",
                success=True,
                duration_ms=int((time.monotonic() - start) * 1000),
                output={"target_param": target_param, "value": resolved},
            )
        except Exception as e:
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type="param_process",
                success=False,
                error=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )
