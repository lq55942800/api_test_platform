from typing import Any, Dict
from app.services.processors.base_processor import BaseProcessor, ActionResult


class ResultStatusProcessor(BaseProcessor):
    async def execute(self, action: Dict[str, Any], context: Dict[str, Any]) -> ActionResult:
        import time
        start = time.monotonic()
        config = self._get_config(action)
        try:
            condition = config.get("condition", "always")
            action_type = config.get("action", "continue")
            max_retries = config.get("max_retries", 0)
            retry_interval = config.get("retry_interval", 1000)
            custom_message = config.get("custom_message", "")
            response_data = context.get("response_data", {})
            status_code = response_data.get("status_code", 0)
            is_failure = status_code >= 400 or context.get("error_message")
            should_trigger = False
            if condition == "on_failure" and is_failure:
                should_trigger = True
            elif condition == "on_success" and not is_failure:
                should_trigger = True
            elif condition == "always":
                should_trigger = True
            output = {
                "condition": condition,
                "triggered": should_trigger,
                "action": action_type if should_trigger else "none",
            }
            if should_trigger:
                context["result_status_action"] = action_type
                context["result_status_max_retries"] = max_retries
                context["result_status_retry_interval"] = retry_interval
                if custom_message:
                    context["result_status_message"] = custom_message
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type="result_status_handler",
                success=True,
                duration_ms=int((time.monotonic() - start) * 1000),
                output=output,
            )
        except Exception as e:
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type="result_status_handler",
                success=False,
                error=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )
