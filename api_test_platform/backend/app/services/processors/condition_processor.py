import re
import ast
import signal
import threading
from typing import Any, Dict, List, Optional
from app.services.processors.base_processor import BaseProcessor, ActionResult


class ScriptExecutionTimeout(Exception):
    """脚本执行超时异常"""
    pass


class ScriptSecurityError(Exception):
    """脚本安全违规异常"""
    pass


def _create_safe_builtins() -> Dict[str, Any]:
    """
    创建安全的内置函数字典
    只包含必要的、安全的内置函数
    """
    return {
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "list": list,
        "dict": dict,
        "tuple": tuple,
        "len": len,
        "range": range,
        "abs": abs,
        "min": min,
        "max": max,
        "sum": sum,
        "any": any,
        "all": all,
        "sorted": sorted,
        "reversed": reversed,
        "enumerate": enumerate,
        "zip": zip,
        "map": map,
        "filter": filter,
        "isinstance": isinstance,
        "hasattr": hasattr,
        "getattr": getattr,
        "round": round,
        "pow": pow,
        "divmod": divmod,
        "hex": hex,
        "oct": oct,
        "bin": bin,
        "ord": ord,
        "chr": chr,
        # 禁止的危险函数：open, exec, eval, compile, __import__, input, print等
    }


def _validate_script(script: str) -> None:
    """
    验证脚本是否包含危险操作
    
    Args:
        script: 要验证的脚本代码
        
    Raises:
        ScriptSecurityError: 如果脚本包含危险操作
    """
    # 检查危险关键字
    dangerous_keywords = [
        '__import__', 'import ', 'from ', 'exec', 'compile',
        'open(', 'file(', 'input(', 'raw_input(',
        'os.', 'sys.', 'subprocess.', 'socket.',
        'eval(', 'globals()', 'locals()', 'vars()',
        'delattr', 'setattr', '__class__', '__bases__',
        '__subclasses__', '__mro__', '__builtins__',
    ]
    
    script_lower = script.lower()
    for keyword in dangerous_keywords:
        if keyword.lower() in script_lower:
            raise ScriptSecurityError(f"脚本包含禁止的操作: {keyword}")


def _execute_with_timeout(func, args=(), kwargs=None, timeout: float = 5.0):
    """
    带超时限制的函数执行
    
    Args:
        func: 要执行的函数
        args: 位置参数
        kwargs: 关键字参数
        timeout: 超时时间（秒）
        
    Returns:
        函数执行结果
        
    Raises:
        ScriptExecutionTimeout: 执行超时
        Exception: 函数执行中的其他异常
    """
    if kwargs is None:
        kwargs = {}
    
    result = [None]
    exception = [None]
    
    def target():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            exception[0] = e
    
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout=timeout)
    
    if thread.is_alive():
        # 线程仍在运行，表示超时
        raise ScriptExecutionTimeout(f"脚本执行超时（超过 {timeout} 秒）")
    
    if exception[0] is not None:
        raise exception[0]
    
    return result[0]


class StepConditionEvaluator:
    """步骤条件评估器，用于判断是否执行某个测试步骤或测试用例"""
    
    SUPPORTED_OPERATORS = {
        # 比较运算符
        "==": lambda a, b: str(a) == str(b),
        "!=": lambda a, b: str(a) != str(b),
        ">": lambda a, b: float(a) > float(b),
        "<": lambda a, b: float(a) < float(b),
        ">=": lambda a, b: float(a) >= float(b),
        "<=": lambda a, b: float(a) <= float(b),
        # 包含和匹配
        "contains": lambda a, b: str(b) in str(a),
        "not_contains": lambda a, b: str(b) not in str(a),
        "matches": lambda a, b: bool(re.match(str(b), str(a))),
        "in": lambda a, b: str(a) in (b if isinstance(b, list) else [x.strip() for x in str(b).split(',')]),
        "not_in": lambda a, b: str(a) not in (b if isinstance(b, list) else [x.strip() for x in str(b).split(',')]),
    }
    
    def __init__(self, variable_manager=None):
        """
        初始化条件评估器
        
        Args:
            variable_manager: 变量管理器实例
        """
        self.variable_manager = variable_manager
    
    def evaluate(self, condition_config: Dict[str, Any]) -> tuple:
        """
        评估条件配置
        
        Args:
            condition_config: 条件配置字典，包含：
                - enabled: 是否启用条件（可选，默认True）
                - condition_type: 条件类型 (variable/expression/script)
                - variable: 变量名（condition_type=variable时）
                - operator: 操作符（condition_type=variable时）
                - expected_value: 期望值（condition_type=variable时）
                - expression: 表达式（condition_type=expression时）
                - script: Python脚本（condition_type=script时）
        
        Returns:
            Tuple[bool, str]: (条件评估结果, 跳过原因)
        """
        # 如果条件未启用或配置为空，默认通过
        if not condition_config or not condition_config.get("enabled", True):
            return True, ""
        
        condition_type = condition_config.get("condition_type", "expression")
        
        try:
            if condition_type == "variable":
                return self._evaluate_variable_condition(condition_config)
            elif condition_type == "expression":
                return self._evaluate_expression(condition_config)
            elif condition_type == "script":
                return self._evaluate_script(condition_config)
            else:
                return False, f"不支持的条件类型: {condition_type}"
        except Exception as e:
            # 条件评估失败时返回False，避免意外执行
            return False, f"条件评估失败: {str(e)}"
    
    def _evaluate_variable_condition(self, config: Dict[str, Any]) -> tuple:
        """
        评估变量条件
        
        Args:
            config: 包含variable, operator, expected_value的配置
        
        Returns:
            Tuple[bool, str]: (条件结果, 跳过原因)
        """
        var_name = config.get("variable", "")
        operator = config.get("operator", "==")
        expected = config.get("expected_value")
        
        # 从变量管理器获取实际值
        actual = self._get_variable_value(var_name)
        
        # 解析期望值中的变量引用
        expected = self._resolve_value(expected)
        
        # 获取操作符函数
        op_func = self.SUPPORTED_OPERATORS.get(operator)
        if not op_func:
            return False, f"不支持的操作符: {operator}"
        
        try:
            result = op_func(actual, expected)
            if not result:
                return False, f"变量 {var_name}={actual}, 期望 {operator} {expected}"
            return True, ""
        except (ValueError, TypeError) as e:
            return False, f"条件评估错误: {str(e)}"
    
    def _evaluate_expression(self, config: Dict[str, Any]) -> tuple:
        """
        评估表达式条件
        支持 && 和 || 逻辑运算符
        
        Args:
            config: 包含expression的配置
        
        Returns:
            Tuple[bool, str]: (表达式结果, 跳过原因)
        """
        expression = config.get("expression", "")
        
        if not expression:
            return True, ""
        
        # 解析表达式中的变量
        resolved = self._resolve_variables(expression)
        
        # 将逻辑运算符转换为Python语法
        resolved = resolved.replace("&&", " and ").replace("||", " or ")
        
        try:
            # 验证表达式不包含危险操作
            _validate_script(resolved)
            
            # 使用安全的执行环境
            safe_builtins = _create_safe_builtins()
            
            # 使用eval执行表达式，限制builtins
            result = eval(resolved, {"__builtins__": safe_builtins}, {})
            if not result:
                return False, f"表达式 {expression} 计算结果为 False"
            return True, ""
        except ScriptSecurityError as e:
            return False, f"表达式包含不安全操作: {str(e)}"
        except ScriptExecutionTimeout as e:
            return False, f"表达式执行超时: {str(e)}"
        except Exception as e:
            return False, f"表达式评估失败: {str(e)}"
    
    def _evaluate_script(self, config: Dict[str, Any]) -> tuple:
        """
        执行Python脚本并返回布尔结果
        
        Args:
            config: 包含script的配置，可选timeout参数（默认5秒）
        
        Returns:
            Tuple[bool, str]: (脚本执行结果, 跳过原因)
        """
        script = config.get("script", "")
        timeout = config.get("timeout", 5.0)  # 默认5秒超时
        
        if not script:
            return True, ""
        
        # 验证脚本安全性
        try:
            _validate_script(script)
        except ScriptSecurityError as e:
            return False, f"脚本安全验证失败: {str(e)}"
        
        # 准备安全的执行环境
        safe_builtins = _create_safe_builtins()
        
        # 添加re模块（只读访问）
        safe_builtins["re"] = re
        
        exec_globals = {
            "__builtins__": safe_builtins,
        }
        
        # 添加变量管理器的所有变量
        if self.variable_manager:
            variables = self.variable_manager.get_all()
            exec_globals["variables"] = variables
            # 将变量直接注入到执行环境中
            exec_globals.update(variables)
        
        exec_locals = {}
        
        def execute_script():
            """在独立函数中执行脚本，便于超时控制"""
            exec(script, exec_globals, exec_locals)
            return exec_locals.get("__result", False)
        
        try:
            # 使用超时限制执行脚本
            result = _execute_with_timeout(execute_script, timeout=timeout)
            if not result:
                return False, "脚本返回 False"
            return True, ""
        except ScriptExecutionTimeout as e:
            return False, f"脚本执行超时: {str(e)}"
        except ScriptSecurityError as e:
            return False, f"脚本包含不安全操作: {str(e)}"
        except Exception as e:
            return False, f"脚本执行失败: {str(e)}"
    
    def _get_variable_value(self, var_name: str) -> Any:
        """
        获取变量值
        
        Args:
            var_name: 变量名
        
        Returns:
            Any: 变量值
        """
        if not self.variable_manager:
            return None
        
        # 支持嵌套属性访问，如 response.data.status
        parts = var_name.split(".")
        value = self.variable_manager.get(parts[0])
        
        # 处理嵌套属性
        for part in parts[1:]:
            if isinstance(value, dict):
                value = value.get(part)
            elif hasattr(value, part):
                value = getattr(value, part)
            else:
                return None
        
        return value
    
    def _resolve_value(self, value: Any) -> Any:
        """
        解析值中的变量引用
        
        Args:
            value: 可能包含变量引用的值
        
        Returns:
            Any: 解析后的值
        """
        if not isinstance(value, str):
            return value
        
        if not self.variable_manager:
            return value
        
        # 使用变量管理器的resolve方法
        return self.variable_manager.resolve(value)
    
    def _resolve_variables(self, expression: str) -> str:
        """
        解析表达式中的变量引用
        支持 {{variable}} 和 ${variable} 两种格式
        
        Args:
            expression: 包含变量的表达式
        
        Returns:
            str: 解析后的表达式
        """
        if not expression:
            return expression
        
        if not self.variable_manager:
            return expression
        
        # 先使用变量管理器解析 ${variable} 格式
        resolved = self.variable_manager.resolve(expression)
        
        # 再解析 {{variable}} 格式
        pattern = r'\{\{([^}]+)\}\}'
        
        def replace_var(match):
            var_name = match.group(1).strip()
            value = self.variable_manager.get(var_name)
            if isinstance(value, str):
                return f"'{value}'"
            elif value is None:
                return "None"
            return str(value)
        
        return re.sub(pattern, replace_var, resolved)
    
    def evaluate_multiple(self, conditions: List[Dict[str, Any]], logic: str = "and") -> tuple:
        """
        评估多个条件
        
        Args:
            conditions: 条件列表
            logic: 逻辑关系 (and/or)
        
        Returns:
            Tuple[bool, str]: (组合条件结果, 跳过原因)
        """
        if not conditions:
            return True, ""
        
        results = []
        reasons = []
        
        for cond in conditions:
            result, reason = self.evaluate(cond)
            results.append(result)
            if reason:
                reasons.append(reason)
        
        if logic == "and":
            final_result = all(results)
        elif logic == "or":
            final_result = any(results)
        else:
            return False, f"不支持的逻辑运算符: {logic}"
        
        # 组合跳过原因
        skip_reason = "; ".join(reasons) if reasons else ""
        
        return final_result, skip_reason


class ConditionProcessor(BaseProcessor):
    OPERATORS = {
        "equals": lambda a, b: str(a) == str(b),
        "not_equals": lambda a, b: str(a) != str(b),
        "contains": lambda a, b: str(b) in str(a),
        "not_contains": lambda a, b: str(b) not in str(a),
        "starts_with": lambda a, b: str(a).startswith(str(b)),
        "ends_with": lambda a, b: str(a).endswith(str(b)),
        "greater_than": lambda a, b: float(a) > float(b),
        "less_than": lambda a, b: float(a) < float(b),
        "is_empty": lambda a, b: not a,
        "not_empty": lambda a, b: bool(a),
        "matches": lambda a, b: bool(re.match(str(b), str(a))),
        "in": lambda a, b: a in (b if isinstance(b, list) else [b]),
    }

    async def execute(self, action: Dict[str, Any], context: Dict[str, Any]) -> ActionResult:
        import time
        start = time.monotonic()
        config = self._get_config(action)
        try:
            condition_type = config.get("condition_type", "variable")
            result = False
            if condition_type == "variable":
                result = self._evaluate_variable_condition(config)
            elif condition_type == "expression":
                result = self._evaluate_expression(config)
            elif condition_type == "script":
                result = self._evaluate_script(config)
            actions_to_execute = config.get("then_actions", []) if result else config.get("else_actions", [])
            sub_results = []
            for sub_action in actions_to_execute:
                from app.services.engines.pre_processor_engine import PreProcessorEngine
                sub_result = ActionResult(
                    id=sub_action.get("type", ""),
                    name=sub_action.get("type", ""),
                    type=sub_action.get("type", ""),
                    success=True,
                    duration_ms=0,
                )
                sub_results.append(sub_result)
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type="condition",
                success=True,
                duration_ms=int((time.monotonic() - start) * 1000),
                output={"condition_result": result, "branch": "then" if result else "else"},
            )
        except Exception as e:
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type="condition",
                success=False,
                error=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )

    def _evaluate_variable_condition(self, config: Dict) -> bool:
        var_name = config.get("variable_name", "")
        operator = config.get("operator", "equals")
        expected = config.get("expected_value")
        actual = self.variable_manager.get(var_name) if self.variable_manager else None
        op_func = self.OPERATORS.get(operator)
        if not op_func:
            return False
        try:
            return op_func(actual, expected)
        except (ValueError, TypeError):
            return False

    def _evaluate_expression(self, config: Dict) -> bool:
        """评估表达式条件"""
        expression = config.get("expression", "")
        resolved = self._resolve_expression(expression)
        
        try:
            # 验证表达式安全性
            _validate_script(resolved)
            
            # 使用安全的执行环境
            safe_builtins = _create_safe_builtins()
            return bool(eval(resolved, {"__builtins__": safe_builtins}, {}))
        except ScriptSecurityError as e:
            print(f"表达式安全验证失败: {str(e)}")
            return False
        except Exception as e:
            print(f"表达式评估失败: {str(e)}")
            return False

    def _evaluate_script(self, config: Dict) -> bool:
        """执行Python脚本"""
        script = config.get("script", "")
        timeout = config.get("timeout", 5.0)
        
        if not script:
            return True
        
        # 验证脚本安全性
        try:
            _validate_script(script)
        except ScriptSecurityError as e:
            print(f"脚本安全验证失败: {str(e)}")
            return False
        
        # 准备安全的执行环境
        safe_builtins = _create_safe_builtins()
        safe_builtins["re"] = re
        
        local_vars = {}
        if self.variable_manager:
            local_vars["variables"] = self.variable_manager.get_all()
            local_vars.update(self.variable_manager.get_all())
        
        exec_globals = {"__builtins__": safe_builtins}
        exec_globals.update(local_vars)
        
        exec_locals = {}
        
        def execute_script():
            exec(script, exec_globals, exec_locals)
            return exec_locals.get("__result", False)
        
        try:
            result = _execute_with_timeout(execute_script, timeout=timeout)
            return bool(result)
        except ScriptExecutionTimeout as e:
            print(f"脚本执行超时: {str(e)}")
            return False
        except ScriptSecurityError as e:
            print(f"脚本包含不安全操作: {str(e)}")
            return False
        except Exception as e:
            print(f"脚本执行失败: {str(e)}")
            return False
