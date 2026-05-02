from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TestCaseModuleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="模块名称")
    parent_id: Optional[int] = Field(None, description="父模块ID")
    description: Optional[str] = Field(None, max_length=500, description="模块描述")
    sort_order: int = Field(0, ge=0, description="排序顺序")


class TestCaseModuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="模块名称")
    parent_id: Optional[int] = Field(None, description="父模块ID")
    description: Optional[str] = Field(None, max_length=500, description="模块描述")
    sort_order: Optional[int] = Field(None, ge=0, description="排序顺序")


class TestCaseModuleResponse(BaseModel):
    id: int
    team_id: int
    name: str
    parent_id: Optional[int]
    description: Optional[str]
    sort_order: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TestCaseModuleTreeResponse(TestCaseModuleResponse):
    """带子模块的树形结构响应"""
    children: List['TestCaseModuleTreeResponse'] = []
    test_case_count: int = 0


# 更新forward reference
TestCaseModuleTreeResponse.model_rebuild()
