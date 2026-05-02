from typing import Any, Dict
from app.services.processors.base_processor import BaseProcessor, ActionResult


class CookieProcessor(BaseProcessor):
    async def execute(self, action: Dict[str, Any], context: Dict[str, Any]) -> ActionResult:
        import time
        start = time.monotonic()
        config = self._get_config(action)
        try:
            policy = config.get("policy", "standard")
            custom_cookies = config.get("custom_cookies", [])
            request_params = context.setdefault("request_params", {})
            cookie_params = request_params.setdefault("cookie", {})
            if policy == "ignore_cookies":
                context["cookie_policy"] = "ignore"
                cookie_params.clear()
            elif policy == "custom_only":
                context["cookie_policy"] = "custom_only"
                cookie_params.clear()
                for c in custom_cookies:
                    name = c.get("name", "")
                    value = c.get("value", "")
                    if name:
                        resolved_value = self._resolve_expression(value)
                        cookie_params[name] = resolved_value
            else:
                context["cookie_policy"] = "standard"
                for c in custom_cookies:
                    name = c.get("name", "")
                    value = c.get("value", "")
                    if name:
                        resolved_value = self._resolve_expression(value)
                        cookie_params[name] = resolved_value
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type="cookie_manager",
                success=True,
                duration_ms=int((time.monotonic() - start) * 1000),
                output={"policy": policy, "cookies_applied": len(custom_cookies)},
            )
        except Exception as e:
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type="cookie_manager",
                success=False,
                error=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )
