from typing import Any, Dict
from app.services.processors.base_processor import BaseProcessor, ActionResult


class VariableProcessor(BaseProcessor):
    async def execute(self, action: Dict[str, Any], context: Dict[str, Any]) -> ActionResult:
        import time
        start = time.monotonic()
        config = self._get_config(action)
        action_type = action.get("type", "set_variable")
        try:
            if action_type == "set_variable":
                return await self._handle_set_variable(action, config, context, start)
            else:
                return ActionResult(
                    id=action.get("id", ""),
                    name=action.get("name", ""),
                    type=action_type,
                    success=False,
                    error=f"Unknown variable action type: {action_type}",
                    duration_ms=int((time.monotonic() - start) * 1000),
                )
        except Exception as e:
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type=action_type,
                success=False,
                error=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )

    async def _handle_set_variable(self, action: Dict, config: Dict, context: Dict, start: float) -> ActionResult:
        variables = config.get("variables", [])
        output = {}
        for var in variables:
            name = var.get("name", "")
            value = var.get("value", "")
            scope = var.get("scope", "temp")
            overwrite = var.get("overwrite", True)
            resolved_value = self._resolve_expression(str(value))
            if self.variable_manager:
                if overwrite or not self.variable_manager.exists(name, scope):
                    self.variable_manager.set(name, resolved_value, scope)
            output[name] = resolved_value
        return ActionResult(
            id=action.get("id", ""),
            name=action.get("name", ""),
            type="set_variable",
            success=True,
            duration_ms=int((time.monotonic() - start) * 1000),
            output=output,
        )
