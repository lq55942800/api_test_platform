"""
Environment Management Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ServiceType(str, Enum):
    MICROSERVICE = "microservice"
    MODULE = "module"
    THIRD_PARTY = "third_party"


class ValueType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"


class ServerBase(BaseModel):
    name: str = Field(..., max_length=100)
    host: str = Field(..., max_length=255)
    port: Optional[int] = None
    protocol: str = Field(default="https", max_length=20)
    base_path: str = Field(default="", max_length=255)
    ssl_config: Optional[str] = None
    headers: Optional[str] = None
    timeout: int = Field(default=30000)
    is_default: bool = False


class ServerCreate(ServerBase):
    pass


class ServerUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    host: Optional[str] = Field(None, max_length=255)
    port: Optional[int] = None
    protocol: Optional[str] = Field(None, max_length=20)
    base_path: Optional[str] = Field(None, max_length=255)
    ssl_config: Optional[str] = None
    headers: Optional[str] = None
    timeout: Optional[int] = None
    is_default: Optional[bool] = None


class ServerResponse(ServerBase):
    id: int
    service_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DatabaseBase(BaseModel):
    name: str = Field(..., max_length=100)
    db_type: str = Field(..., max_length=50)
    host: str = Field(..., max_length=255)
    port: Optional[int] = None
    database: str = Field(..., max_length=100)
    username: str = Field(..., max_length=100)
    password: str = Field(..., max_length=255)
    charset: str = Field(default="utf8mb4", max_length=20)
    extra_config: Optional[str] = None
    is_default: bool = False


class DatabaseCreate(DatabaseBase):
    pass


class DatabaseUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    db_type: Optional[str] = Field(None, max_length=50)
    host: Optional[str] = Field(None, max_length=255)
    port: Optional[int] = None
    database: Optional[str] = Field(None, max_length=100)
    username: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, max_length=255)
    charset: Optional[str] = Field(None, max_length=20)
    extra_config: Optional[str] = None
    is_default: Optional[bool] = None


class DatabaseResponse(BaseModel):
    id: int
    service_id: int
    name: str
    db_type: str
    host: str
    port: Optional[int]
    database: str
    username: str
    password: str
    charset: str
    extra_config: Optional[str]
    is_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ServiceBase(BaseModel):
    name: str = Field(..., max_length=100)
    service_type: ServiceType = ServiceType.MICROSERVICE
    description: Optional[str] = None
    sort_order: int = 0


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    service_type: Optional[ServiceType] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None


class ServiceResponse(ServiceBase):
    id: int
    environment_id: int
    created_at: datetime
    updated_at: datetime
    servers: List[ServerResponse] = []
    databases: List[DatabaseResponse] = []

    class Config:
        from_attributes = True


class ServiceListResponse(BaseModel):
    items: List[ServiceResponse]
    total: int
    page: int
    page_size: int


class VariableBase(BaseModel):
    key: str = Field(..., max_length=100)
    value: Optional[str] = None
    value_type: ValueType = ValueType.STRING
    is_encrypted: bool = False
    description: Optional[str] = None


class VariableCreate(VariableBase):
    pass


class VariableUpdate(BaseModel):
    key: Optional[str] = Field(None, max_length=100)
    value: Optional[str] = None
    value_type: Optional[ValueType] = None
    is_encrypted: Optional[bool] = None
    description: Optional[str] = None


class VariableResponse(VariableBase):
    id: int
    environment_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EnvironmentBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    is_default: bool = False


class EnvironmentCreate(EnvironmentBase):
    team_id: Optional[int] = None
    services: Optional[List[ServiceCreate]] = None
    variables: Optional[List[VariableCreate]] = None


class EnvironmentUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class EnvironmentResponse(EnvironmentBase):
    id: int
    team_id: Optional[int]
    is_active: bool
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    services: List[ServiceResponse] = []
    variables: List[VariableResponse] = []

    class Config:
        from_attributes = True


class EnvironmentListResponse(BaseModel):
    items: List[EnvironmentResponse]
    total: int
    page: int
    page_size: int


class EnvironmentSummary(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_default: bool
    is_active: bool
    service_count: int
    variable_count: int

    class Config:
        from_attributes = True


class VariableResolveRequest(BaseModel):
    environment_id: int
    text: str
    case_variables: Optional[dict] = None
    scenario_variables: Optional[dict] = None


class VariableResolveResponse(BaseModel):
    original_text: str
    resolved_text: str
    resolved_variables: dict
    unresolved_variables: List[str]
