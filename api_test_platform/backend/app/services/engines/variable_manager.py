import re
import uuid
import hashlib
import base64
import random
import string
import time
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from app.core.logging import get_logger

logger = get_logger(__name__)


class VariableManager:
    SCOPES = ["temp", "module", "env", "global"]
    SCOPE_PRIORITY = {"temp": 0, "module": 1, "env": 2, "global": 3}
    LEGACY_SCOPE_MAP = {"request": "temp", "scenario": "temp", "environment": "env", "test_case": "temp"}
    VAR_PATTERN = re.compile(r'\$\{([^}]+)\}')
    FUNC_PATTERN = re.compile(r'\$\{__([a-zA-Z0-9_]+)\(([^)]*)\)\}')
    NESTED_VAR_PATTERN = re.compile(r'\$\{([^}]*\$\{[^}]+\}[^}]*)\}')
    MAX_RESOLVE_DEPTH = 10

    def __init__(self):
        self._scopes: Dict[str, Dict[str, Any]] = {
            "temp": {},
            "module": {},
            "env": {},
            "global": {},
        }
        self._counters: Dict[str, int] = {}
        logger.debug("VariableManager initialized")

    def _normalize_scope(self, scope: str) -> str:
        return self.LEGACY_SCOPE_MAP.get(scope, scope)

    def get(self, name: str, scope: Optional[str] = None) -> Any:
        if scope:
            scope = self._normalize_scope(scope)
            value = self._scopes.get(scope, {}).get(name)
            logger.debug(f"Variable get: name={name}, scope={scope}, found={value is not None}")
            return value
        for s in self.SCOPES:
            if name in self._scopes.get(s, {}):
                value = self._scopes[s][name]
                logger.debug(f"Variable get: name={name}, scope={s}, found=True")
                return value
        prefix, _, var_name = name.partition(".")
        if prefix in self.SCOPES and var_name:
            value = self._scopes.get(prefix, {}).get(var_name)
            logger.debug(f"Variable get (dotted): name={name}, prefix={prefix}, var_name={var_name}, found={value is not None}")
            return value
        logger.debug(f"Variable get: name={name}, found=False")
        return None

    def set(self, name: str, value: Any, scope: str = "temp") -> None:
        scope = self._normalize_scope(scope)
        if scope not in self._scopes:
            self._scopes[scope] = {}
        self._scopes[scope][name] = value
        logger.debug(f"Variable set: name={name}, scope={scope}, value_type={type(value).__name__}")

    def delete(self, name: str, scope: Optional[str] = None) -> None:
        if scope:
            scope = self._normalize_scope(scope)
            self._scopes.get(scope, {}).pop(name, None)
            logger.debug(f"Variable deleted: name={name}, scope={scope}")
        else:
            for s in self.SCOPES:
                self._scopes.get(s, {}).pop(name, None)
            logger.debug(f"Variable deleted from all scopes: name={name}")

    def exists(self, name: str, scope: Optional[str] = None) -> bool:
        if scope:
            scope = self._normalize_scope(scope)
            return name in self._scopes.get(scope, {})
        for s in self.SCOPES:
            if name in self._scopes.get(s, {}):
                return True
        return False

    def resolve(self, expression: str) -> str:
        if not expression or not isinstance(expression, str):
            return str(expression) if expression is not None else ""
        logger.debug(f"Resolving expression: expression_length={len(expression)}")
        result = str(expression)
        depth = 0
        while depth < self.MAX_RESOLVE_DEPTH:
            prev = result
            result = self._resolve_functions(result)
            result = self._resolve_variables(result)
            if result == prev:
                break
            depth += 1
        if depth > 0:
            logger.debug(f"Expression resolved in {depth} iterations")
        if depth >= self.MAX_RESOLVE_DEPTH:
            logger.warning(f"Variable resolution reached max depth ({self.MAX_RESOLVE_DEPTH}), possible circular reference")
        return result

    def get_all(self, scope: Optional[str] = None) -> Dict[str, Any]:
        if scope:
            return dict(self._scopes.get(scope, {}))
        result = {}
        for s in reversed(self.SCOPES):
            result.update(self._scopes.get(s, {}))
        return result

    def clear_scope(self, scope: str) -> None:
        if scope in self._scopes:
            self._scopes[scope] = {}
            logger.debug(f"Variable scope cleared: scope={scope}")

    def load_environment_vars(self, env_vars: Dict[str, Any]) -> None:
        for key, value in env_vars.items():
            self.set(key, value, "env")
        logger.info(f"Loaded environment variables: count={len(env_vars)}")

    def load_global_vars(self, global_vars: Dict[str, Any]) -> None:
        for key, value in global_vars.items():
            self.set(key, value, "global")
        logger.info(f"Loaded global variables: count={len(global_vars)}")

    def _resolve_variables(self, text: str) -> str:
        def replace_var(match):
            expr = match.group(1)
            if expr.startswith("__"):
                return match.group(0)
            var_name, _, default = expr.partition(":")
            value = self.get(var_name.strip())
            if value is not None:
                return str(value)
            if default:
                logger.debug(f"Variable not found, using default: var_name={var_name.strip()}, default={default}")
                return default
            logger.debug(f"Variable not resolved: var_name={var_name.strip()}")
            return match.group(0)

        return self.VAR_PATTERN.sub(replace_var, text)

    def _resolve_functions(self, text: str) -> str:
        def replace_func(match):
            func_name = match.group(1)
            args_str = match.group(2).strip()
            args = [a.strip() for a in args_str.split(",")] if args_str else []
            try:
                result = self._execute_builtin_function(func_name, args)
                return str(result) if result is not None else match.group(0)
            except Exception as e:
                logger.warning(f"Function resolution failed: func_name={func_name}, error={str(e)}")
                return match.group(0)

        return self.FUNC_PATTERN.sub(replace_func, text)

    def _execute_builtin_function(self, name: str, args: List[str]) -> Any:
        logger.debug(f"Executing builtin function: name={name}, args_count={len(args)}")
        resolved_args = []
        for a in args:
            resolved = self.resolve(a) if a.startswith("${") else a
            resolved_args.append(resolved)

        func_map = {
            "timestamp": self._func_timestamp,
            "uuid": self._func_uuid,
            "randomInt": self._func_random_int,
            "randomString": self._func_random_string,
            "md5": self._func_md5,
            "sha256": self._func_sha256,
            "base64Encode": self._func_base64_encode,
            "base64Decode": self._func_base64_decode,
            "dateFormat": self._func_date_format,
            "concat": self._func_concat,
            "substring": self._func_substring,
            "upper": self._func_upper,
            "lower": self._func_lower,
            "counter": self._func_counter,
            "property": self._func_property,
            "V": self._func_v,
        }
        handler = func_map.get(name)
        if handler:
            return handler(resolved_args)
        logger.warning(f"Unknown builtin function: name={name}")
        raise ValueError(f"Unknown function: {name}")

    def _func_timestamp(self, args: List[str]) -> str:
        return str(int(time.time() * 1000))

    def _func_uuid(self, args: List[str]) -> str:
        return str(uuid.uuid4())

    def _func_random_int(self, args: List[str]) -> str:
        min_val = int(args[0]) if len(args) > 0 else 0
        max_val = int(args[1]) if len(args) > 1 else 100
        return str(random.randint(min_val, max_val))

    def _func_random_string(self, args: List[str]) -> str:
        length = int(args[0]) if len(args) > 0 else 8
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    def _func_md5(self, args: List[str]) -> str:
        value = args[0] if len(args) > 0 else ""
        return hashlib.md5(value.encode('utf-8')).hexdigest()

    def _func_sha256(self, args: List[str]) -> str:
        value = args[0] if len(args) > 0 else ""
        return hashlib.sha256(value.encode('utf-8')).hexdigest()

    def _func_base64_encode(self, args: List[str]) -> str:
        value = args[0] if len(args) > 0 else ""
        return base64.b64encode(value.encode('utf-8')).decode('utf-8')

    def _func_base64_decode(self, args: List[str]) -> str:
        value = args[0] if len(args) > 0 else ""
        return base64.b64decode(value.encode('utf-8')).decode('utf-8')

    def _func_date_format(self, args: List[str]) -> str:
        fmt = args[0] if len(args) > 0 else "YYYY-MM-DD"
        fmt = fmt.replace("YYYY", "%Y").replace("MM", "%m").replace("DD", "%d") \
                 .replace("HH", "%H").replace("mm", "%M").replace("ss", "%S")
        return datetime.now().strftime(fmt)

    def _func_concat(self, args: List[str]) -> str:
        return "".join(args)

    def _func_substring(self, args: List[str]) -> str:
        s = args[0] if len(args) > 0 else ""
        start = int(args[1]) if len(args) > 1 else 0
        end = int(args[2]) if len(args) > 2 else len(s)
        return s[start:end]

    def _func_upper(self, args: List[str]) -> str:
        return (args[0] if len(args) > 0 else "").upper()

    def _func_lower(self, args: List[str]) -> str:
        return (args[0] if len(args) > 0 else "").lower()

    def _func_counter(self, args: List[str]) -> str:
        name = args[0] if len(args) > 0 else "default"
        self._counters[name] = self._counters.get(name, 0) + 1
        return str(self._counters[name])

    def _func_property(self, args: List[str]) -> str:
        name = args[0] if len(args) > 0 else ""
        default = args[1] if len(args) > 1 else ""
        return os.environ.get(name, default)

    def _func_v(self, args: List[str]) -> str:
        var_expr = args[0] if len(args) > 0 else ""
        inner = self.resolve(var_expr)
        return self.resolve(inner) if inner != var_expr else inner
