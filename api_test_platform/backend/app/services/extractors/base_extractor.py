from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ExtractConfig(BaseModel):
    extract_type: str = Field(default="jsonpath", description="提取方式")
    expression: str = Field(default="", description="提取表达式")
    source: str = Field(default="body", description="提取源: body, headers, cookies, url")
    default_value: str = Field(default="", description="默认值，提取结果为空时使用")
    template: str = Field(default="$1$", description="捕获组模板")
    attribute: Optional[str] = Field(None, description="HTML属性名")
    left_boundary: Optional[str] = Field(None, description="左边界")
    right_boundary: Optional[str] = Field(None, description="右边界")
    use_tidy: bool = Field(default=False, description="HTML是否使用Tidy解析")
    use_namespaces: bool = Field(default=False, description="是否使用命名空间")
    validate_xml: bool = Field(default=False, description="是否验证XML")
    return_fragment: bool = Field(default=False, description="是否返回片段")


class ExtractResult(BaseModel):
    success: bool = Field(default=False, description="是否成功")
    value: Any = Field(None, description="提取的值")
    all_matches: List[Any] = Field(default_factory=list, description="所有匹配项")
    match_count: int = Field(default=0, description="匹配数量")
    error: Optional[str] = Field(None, description="错误信息")


class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, source_data: Any, config: ExtractConfig) -> ExtractResult:
        pass
