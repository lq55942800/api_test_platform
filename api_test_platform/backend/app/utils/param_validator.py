"""
参数校验器
"""
import re
from typing import List, Optional, Dict, Any, Tuple


class ParamValidator:
    """接口参数校验"""

    VALID_TYPES = {"String", "Integer", "Float", "Boolean", "Array", "Object", "File"}
    MAX_NESTING_DEPTH = 5
    MAX_PARAM_COUNT = 200

    @classmethod
    def validate_param_definition(cls, param: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """校验单个参数定义"""
        name = param.get("name")
        if not name:
            return False, "参数名称不能为空"
        if len(name) > 100:
            return False, f"参数名称 '{name}' 长度超过100字符"

        param_type = param.get("param_type", "String")
        if param_type not in cls.VALID_TYPES:
            return False, f"参数类型 '{param_type}' 不合法，允许类型: {cls.VALID_TYPES}"

        desc = param.get("description", "")
        if desc and len(desc) > 500:
            return False, f"参数 '{name}' 描述长度超过500字符"

        rules = param.get("validation_rules")
        if rules:
            valid, err = cls._validate_rules(param_type, rules)
            if not valid:
                return False, f"参数 '{name}' 校验规则错误: {err}"

        return True, None

    @classmethod
    def validate_params_list(cls, params: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
        """校验参数列表"""
        if len(params) > cls.MAX_PARAM_COUNT:
            return False, f"参数总数超过限制({cls.MAX_PARAM_COUNT})"

        names = set()
        for param in params:
            valid, err = cls.validate_param_definition(param)
            if not valid:
                return False, err
            name = param.get("name")
            if name in names:
                return False, f"参数名称 '{name}' 重复"
            names.add(name)

        total_count = cls._count_nested_params(params)
        if total_count > cls.MAX_PARAM_COUNT:
            return False, f"参数总数(含嵌套)超过限制({cls.MAX_PARAM_COUNT})"

        return True, None

    @classmethod
    def validate_body_type_method_match(cls, method: str, body_type: str) -> Tuple[bool, Optional[str]]:
        """校验请求体类型与HTTP方法的匹配"""
        if method in ("GET", "HEAD", "DELETE") and body_type != "none":
            return False, f"{method} 请求不应定义请求体"
        if method in ("POST", "PUT", "PATCH") and body_type == "none":
            return False, f"{method} 请求必须定义请求体类型"
        return True, None

    @classmethod
    def _validate_rules(cls, param_type: str, rules: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """校验参数校验规则"""
        if param_type == "String":
            if "minLength" in rules and not isinstance(rules["minLength"], int):
                return False, "minLength 必须为整数"
            if "maxLength" in rules and not isinstance(rules["maxLength"], int):
                return False, "maxLength 必须为整数"
            if "pattern" in rules:
                try:
                    re.compile(rules["pattern"])
                except re.error as e:
                    return False, f"正则表达式无效: {e}"
            if "format" in rules and rules["format"] not in ("email", "url", "date", "datetime", "uuid"):
                return False, f"不支持的格式: {rules['format']}"

        elif param_type in ("Integer", "Float"):
            for key in ("minimum", "maximum", "multipleOf"):
                if key in rules and not isinstance(rules[key], (int, float)):
                    return False, f"{key} 必须为数值"

        elif param_type == "Array":
            if "minItems" in rules and not isinstance(rules["minItems"], int):
                return False, "minItems 必须为整数"
            if "maxItems" in rules and not isinstance(rules["maxItems"], int):
                return False, "maxItems 必须为整数"

        elif param_type == "Object":
            if "properties" in rules and not isinstance(rules["properties"], dict):
                return False, "properties 必须为对象"
            if "required" in rules and not isinstance(rules["required"], list):
                return False, "required 必须为数组"

        return True, None

    @classmethod
    def _count_nested_params(cls, params: List[Dict[str, Any]], depth: int = 1) -> int:
        """递归计算嵌套参数总数"""
        if depth > cls.MAX_NESTING_DEPTH:
            return 0
        count = len(params)
        for param in params:
            rules = param.get("validation_rules", {})
            if param.get("param_type") == "Object" and "properties" in rules:
                nested = [{"name": k, **v} for k, v in rules["properties"].items()]
                count += cls._count_nested_params(nested, depth + 1)
            elif param.get("param_type") == "Array" and "items" in rules:
                count += cls._count_nested_params([rules["items"]], depth + 1)
        return count
