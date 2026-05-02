"""
路径校验器
"""
import re
from typing import List, Tuple, Optional


class PathValidator:
    """接口路径校验"""

    PATH_PATTERN = re.compile(r'^/[a-zA-Z0-9\-_{}./]*$')
    PARAM_PATTERN = re.compile(r'\{(\w+)\}')
    TRAILING_SLASH_PATTERN = re.compile(r'.+/$')
    QUERY_STRING_PATTERN = re.compile(r'\?.+')

    @classmethod
    def validate(cls, path: str) -> Tuple[bool, Optional[str]]:
        """校验接口路径格式"""
        if not path:
            return False, "路径不能为空"

        if len(path) > 255:
            return False, "路径长度不能超过255字符"

        if not path.startswith('/'):
            return False, "路径必须以 / 开头"

        if cls.QUERY_STRING_PATTERN.search(path):
            return False, "路径中禁止包含查询参数"

        if not cls.PATH_PATTERN.match(path):
            return False, "路径包含非法字符，仅允许字母、数字、连字符、花括号、下划线、正斜杠"

        if len(path) > 1 and cls.TRAILING_SLASH_PATTERN.match(path):
            return False, "路径末尾不添加 /"

        params = cls.extract_path_params(path)
        for param_name in params:
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', param_name):
                return False, f"路径参数 {{{param_name}}} 命名不规范，应以字母开头，仅允许字母、数字、下划线"

        return True, None

    @classmethod
    def extract_path_params(cls, path: str) -> List[str]:
        """提取路径中的参数名"""
        return cls.PARAM_PATTERN.findall(path)

    @classmethod
    def normalize_path(cls, path: str) -> str:
        """标准化路径：去除末尾斜杠、查询参数"""
        path = path.strip()
        if cls.QUERY_STRING_PATTERN.search(path):
            path = path.split('?')[0]
        if len(path) > 1 and path.endswith('/'):
            path = path.rstrip('/')
        return path

    @classmethod
    def validate_path_params_match(cls, path: str, defined_params: List[str]) -> Tuple[bool, Optional[str]]:
        """校验路径参数定义与路径中的占位符是否匹配"""
        path_params = cls.extract_path_params(path)
        defined_names = [p.get("name", p) if isinstance(p, dict) else p for p in defined_params]

        missing_in_def = set(path_params) - set(defined_names)
        extra_in_def = set(defined_names) - set(path_params)

        if missing_in_def:
            return False, f"路径参数 {missing_in_def} 未在参数定义中声明"
        if extra_in_def:
            return False, f"参数定义 {extra_in_def} 在路径中不存在对应占位符"

        return True, None
