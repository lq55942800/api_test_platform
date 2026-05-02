from typing import Any, Dict
from app.services.processors.base_processor import BaseProcessor, ActionResult


class ParamBuilderProcessor(BaseProcessor):
    async def execute(self, action: Dict[str, Any], context: Dict[str, Any]) -> ActionResult:
        import time
        start = time.monotonic()
        config = self._get_config(action)
        try:
            params = config.get("params", [])
            output = {}
            for param in params:
                if not param.get("enabled", True):
                    continue
                location = param.get("location", "query")
                name = param.get("name", "")
                value = param.get("value", "")
                if not name:
                    continue
                resolved_value = self._resolve_expression(str(value))
                request_params = context.setdefault("request_params", {})
                location_params = request_params.setdefault(location, {})
                if isinstance(location_params, dict):
                    location_params[name] = resolved_value
                output[f"{location}.{name}"] = resolved_value
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type="param_builder",
                success=True,
                duration_ms=int((time.monotonic() - start) * 1000),
                output=output,
            )
        except Exception as e:
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type="param_builder",
                success=False,
                error=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )
