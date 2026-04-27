from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class DataSourceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    source_type: str = Field(..., description="csv, json, database")
    source_config: Dict[str, Any] = Field(..., description="数据源配置")
    enabled: bool = True
    iteration_mode: str = "sequential"


class DataSourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    source_type: Optional[str] = None
    source_config: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None
    iteration_mode: Optional[str] = None


class DataSourceResponse(BaseModel):
    id: int
    test_case_id: int
    name: str
    source_type: str
    source_config: Dict[str, Any]
    enabled: bool
    iteration_mode: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DataSourcePreviewResponse(BaseModel):
    total_rows: int
    columns: List[str]
    preview_data: List[Dict[str, Any]]
