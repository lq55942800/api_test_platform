import re
from typing import Any, Dict
from app.services.processors.base_processor import BaseProcessor, ActionResult


class RegexParamProcessor(BaseProcessor):
    async def execute(self, action: Dict[str, Any], context: Dict[str, Any]) -> ActionResult:
        import time
        start = time.monotonic()
        config = self._get_config(action)
        try:
            regex_pattern = config.get("regex", "")
            param_name_group = config.get("param_name_group", 1)
            param_value_group = config.get("param_value_group", 2)
            apply_to = config.get("apply_to", "all")
            source = ""
            response_data = context.get("response_data", {})
            if response_data:
                source = response_data.get("body", "")
            if not source:
                previous_responses = context.get("previous_responses", {})
                for resp in previous_responses.values():
                    if resp.get("body"):
                        source = resp.get("body", "")
                        break
            pattern = re.compile(regex_pattern, re.DOTALL)
            matches = list(pattern.finditer(source))
            if not matches:
                return ActionResult(
                    id=action.get("id", ""),
                    name=action.get("name", ""),
                    type="regex_param",
                    success=True,
                    duration_ms=int((time.monotonic() - start) * 1000),
                    output={"matches_found": 0},
                )
            output = {}
            request_params = context.setdefault("request_params", {})
            for m in matches:
                try:
                    param_name = m.group(param_name_group)
                    param_value = m.group(param_value_group)
                    if apply_to in ("body", "all"):
                        body_params = request_params.setdefault("body", {})
                        body_params[param_name] = param_value
                    if apply_to in ("query", "all"):
                        query_params = request_params.setdefault("query", {})
                        query_params[param_name] = param_value
                    if apply_to in ("header", "all"):
                        header_params = request_params.setdefault("header", {})
                        header_params[param_name] = param_value
                    output[param_name] = param_value
                except IndexError:
                    continue
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type="regex_param",
                success=True,
                duration_ms=int((time.monotonic() - start) * 1000),
                output=output,
            )
        except re.error as e:
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type="regex_param",
                success=False,
                error=f"Regex error: {e}",
                duration_ms=int((time.monotonic() - start) * 1000),
            )
        except Exception as e:
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type="regex_param",
                success=False,
                error=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )
