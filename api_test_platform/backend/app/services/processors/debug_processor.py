import re
from typing import Any, Dict
from app.services.processors.base_processor import BaseProcessor, ActionResult


class DebugProcessor(BaseProcessor):
    async def execute(self, action: Dict[str, Any], context: Dict[str, Any]) -> ActionResult:
        import time
        import json
        start = time.monotonic()
        config = self._get_config(action)
        try:
            output_variables = config.get("output_variables", True)
            output_environment_vars = config.get("output_environment_vars", False)
            output_global_vars = config.get("output_global_vars", False)
            output_response_info = config.get("output_response_info", True)
            filter_pattern = config.get("filter_pattern", "")
            debug_output = {}
            if output_variables and self.variable_manager:
                vars_data = self.variable_manager.get_all("request")
                if filter_pattern:
                    pattern = re.compile(filter_pattern)
                    vars_data = {k: v for k, v in vars_data.items() if pattern.search(k)}
                debug_output["request_variables"] = vars_data
            if output_environment_vars and self.variable_manager:
                env_vars = self.variable_manager.get_all("environment")
                if filter_pattern:
                    pattern = re.compile(filter_pattern)
                    env_vars = {k: v for k, v in env_vars.items() if pattern.search(k)}
                debug_output["environment_variables"] = env_vars
            if output_global_vars and self.variable_manager:
                global_vars = self.variable_manager.get_all("global")
                if filter_pattern:
                    pattern = re.compile(filter_pattern)
                    global_vars = {k: v for k, v in global_vars.items() if pattern.search(k)}
                debug_output["global_variables"] = global_vars
            if output_response_info:
                response_data = context.get("response_data", {})
                debug_output["response_info"] = {
                    "status_code": response_data.get("status_code"),
                    "elapsed_ms": response_data.get("elapsed_ms"),
                    "body_length": len(response_data.get("body", "")),
                }
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type="debug_output",
                success=True,
                duration_ms=int((time.monotonic() - start) * 1000),
                output=debug_output,
            )
        except Exception as e:
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type="debug_output",
                success=False,
                error=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )
