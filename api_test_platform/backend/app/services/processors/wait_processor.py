import asyncio
from typing import Any, Dict
from app.services.processors.base_processor import BaseProcessor, ActionResult


class WaitProcessor(BaseProcessor):
    async def execute(self, action: Dict[str, Any], context: Dict[str, Any]) -> ActionResult:
        import time
        start = time.monotonic()
        config = self._get_config(action)
        try:
            wait_type = config.get("wait_type", "fixed")
            if wait_type == "fixed":
                duration = config.get("duration", 1000)
                unit = config.get("unit", "ms")
                if unit == "s":
                    duration = duration * 1000
                await asyncio.sleep(duration / 1000.0)
                return ActionResult(
                    id=action.get("id", ""),
                    name=action.get("name", ""),
                    type="wait",
                    success=True,
                    duration_ms=int((time.monotonic() - start) * 1000),
                    output={"waited_ms": duration},
                )
            elif wait_type == "conditional":
                max_wait = config.get("max_wait", 30000)
                poll_interval = config.get("poll_interval", 1000)
                condition = config.get("condition", {})
                elapsed = 0
                while elapsed < max_wait:
                    if self._check_condition(condition):
                        return ActionResult(
                            id=action.get("id", ""),
                            name=action.get("name", ""),
                            type="wait",
                            success=True,
                            duration_ms=int((time.monotonic() - start) * 1000),
                            output={"waited_ms": elapsed, "condition_met": True},
                        )
                    await asyncio.sleep(poll_interval / 1000.0)
                    elapsed += poll_interval
                return ActionResult(
                    id=action.get("id", ""),
                    name=action.get("name", ""),
                    type="wait",
                    success=True,
                    duration_ms=int((time.monotonic() - start) * 1000),
                    output={"waited_ms": elapsed, "condition_met": False},
                )
            else:
                return ActionResult(
                    id=action.get("id", ""),
                    name=action.get("name", ""),
                    type="wait",
                    success=False,
                    error=f"Unknown wait type: {wait_type}",
                    duration_ms=int((time.monotonic() - start) * 1000),
                )
        except Exception as e:
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type="wait",
                success=False,
                error=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )

    def _check_condition(self, condition: Dict) -> bool:
        var_name = condition.get("variable_name", "")
        operator = condition.get("operator", "equals")
        expected = condition.get("expected_value")
        if self.variable_manager:
            actual = self.variable_manager.get(var_name)
            from app.services.processors.condition_processor import ConditionProcessor
            op_func = ConditionProcessor.OPERATORS.get(operator)
            if op_func:
                try:
                    return op_func(actual, expected)
                except (ValueError, TypeError):
                    return False
        return False
