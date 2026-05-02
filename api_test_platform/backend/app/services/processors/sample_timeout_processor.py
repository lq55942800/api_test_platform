import asyncio
from typing import Any, Dict
from app.services.processors.base_processor import BaseProcessor, ActionResult


class SampleTimeoutProcessor(BaseProcessor):
    async def execute(self, action: Dict[str, Any], context: Dict[str, Any]) -> ActionResult:
        import time
        start = time.monotonic()
        config = self._get_config(action)
        try:
            timeout = config.get("timeout", 60000)
            on_timeout = config.get("on_timeout", "mark_failed")
            context["sample_timeout"] = timeout
            context["sample_timeout_action"] = on_timeout
            context["sample_timeout_start"] = time.monotonic()
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type="sample_timeout",
                success=True,
                duration_ms=int((time.monotonic() - start) * 1000),
                output={"timeout_ms": timeout, "on_timeout": on_timeout},
            )
        except Exception as e:
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type="sample_timeout",
                success=False,
                error=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )
