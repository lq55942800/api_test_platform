"""
API Management Models
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, Enum as SQLEnum, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
import enum


class ApiStatus(str, enum.Enum):
    DRAFT = "draft"
    ENABLED = "enabled"
    DISABLED = "disabled"
    DEPRECATED = "deprecated"


class BodyType(str, enum.Enum):
    NONE = "none"
    JSON = "json"
    FORM_DATA = "form-data"
    X_WWW_FORM_URLENCODED = "x-www-form-urlencoded"
    RAW = "raw"
    XML = "xml"
    BINARY = "binary"


class Protocol(str, enum.Enum):
    HTTP = "http"
    HTTPS = "https"


class ChangeType(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ROLLBACK = "rollback"


class AuditAction(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    DEBUG = "debug"
    IMPORT = "import"
    EXPORT = "export"
    STATUS_CHANGE = "status_change"
    ROLLBACK = "rollback"


class ApiDefinition(Base):
    """接口定义表"""
    __tablename__ = "api_definitions"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    module_id = Column(Integer, ForeignKey("api_modules.id", ondelete="SET NULL"), nullable=True, index=True)
    service_id = Column(Integer, ForeignKey("env_services.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(100), nullable=False)
    method = Column(String(10), nullable=False)
    path = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(ApiStatus), default=ApiStatus.DRAFT, index=True)
    protocol = Column(String(20), default="http")
    path_params = Column(Text, nullable=True)
    query_params = Column(Text, nullable=True)
    header_params = Column(Text, nullable=True)
    cookie_params = Column(Text, nullable=True)
    body_type = Column(SQLEnum(BodyType), default=BodyType.NONE)
    body_definition = Column(Text, nullable=True)
    responses = Column(Text, nullable=True)
    pre_request_actions = Column(Text, nullable=True)
    post_request_actions = Column(Text, nullable=True)
    assertions = Column(Text, nullable=True)
    connect_timeout = Column(Integer, default=5000, nullable=True)
    read_timeout = Column(Integer, default=30000, nullable=True)
    write_timeout = Column(Integer, default=10000, nullable=True)
    pool_timeout = Column(Integer, default=5000, nullable=True)
    sample_timeout = Column(Integer, default=60000, nullable=True)
    sql_timeout = Column(Integer, default=30000, nullable=True)
    script_timeout = Column(Integer, default=10000, nullable=True)
    timeout_enabled = Column(Boolean, default=True, nullable=True)
    owner_id = Column(Integer, nullable=True, index=True)
    lock_user_id = Column(Integer, nullable=True)
    lock_time = Column(DateTime, nullable=True)
    last_debug_at = Column(DateTime, nullable=True)
    last_debug_status = Column(String(20), nullable=True)
    reference_count = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    team = relationship("Team", back_populates="apis")
    creator = relationship("User", foreign_keys=[created_by], back_populates="apis_created")
    updater = relationship("User", foreign_keys=[updated_by], back_populates="apis_updated")
    module = relationship("ApiModule", back_populates="apis")
    service = relationship("EnvService")
    tag_relations = relationship("ApiTagRelation", back_populates="api", cascade="all, delete-orphan")
    versions = relationship("ApiVersion", back_populates="api", cascade="all, delete-orphan")
    debug_histories = relationship("ApiDebugHistory", back_populates="api", cascade="all, delete-orphan")
    audit_logs = relationship("ApiAuditLog", back_populates="api", cascade="all, delete-orphan")
    recent_visits = relationship("ApiRecentVisit", back_populates="api", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_api_def_team_method_path", "team_id", "method", "path"),
        Index("idx_api_definitions_team_status", "team_id", "status"),
    )


class ApiModule(Base):
    """接口模块表"""
    __tablename__ = "api_modules"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("api_modules.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(50), nullable=False)
    description = Column(String(200), nullable=True)
    sort_order = Column(Integer, default=0)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    apis = relationship("ApiDefinition", back_populates="module")
    children = relationship("ApiModule", backref="parent", remote_side=[id])

    __table_args__ = (
        UniqueConstraint("team_id", "parent_id", "name", name="uq_api_modules_team_parent_name"),
    )


class ApiTag(Base):
    """接口标签表"""
    __tablename__ = "api_tags"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, nullable=False, index=True)
    name = Column(String(20), nullable=False)
    color = Column(String(7), nullable=True)
    tag_group = Column(String(50), nullable=True)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    tag_relations = relationship("ApiTagRelation", back_populates="tag", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("team_id", "name", name="uq_api_tags_team_name"),
    )


class ApiTagRelation(Base):
    """接口标签关联表"""
    __tablename__ = "api_tag_relations"

    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, ForeignKey("api_definitions.id", ondelete="CASCADE"), nullable=False, index=True)
    tag_id = Column(Integer, ForeignKey("api_tags.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    api = relationship("ApiDefinition", back_populates="tag_relations")
    tag = relationship("ApiTag", back_populates="tag_relations")

    __table_args__ = (
        UniqueConstraint("api_id", "tag_id", name="uq_api_tag_relations_api_tag"),
    )


class ApiVersion(Base):
    """接口版本表"""
    __tablename__ = "api_versions"

    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, ForeignKey("api_definitions.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    snapshot = Column(Text, nullable=False)
    change_type = Column(SQLEnum(ChangeType), default=ChangeType.UPDATE)
    change_summary = Column(Text, nullable=True)
    affected_fields = Column(Text, nullable=True)
    changed_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    api = relationship("ApiDefinition", back_populates="versions")

    __table_args__ = (
        Index("idx_api_versions_api_id", "api_id", "version_number"),
    )


class ApiDebugHistory(Base):
    """接口调试历史表"""
    __tablename__ = "api_debug_histories"

    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, ForeignKey("api_definitions.id", ondelete="CASCADE"), nullable=False, index=True)
    environment_id = Column(Integer, nullable=True)
    user_id = Column(Integer, nullable=False)
    request_method = Column(String(10), nullable=False)
    request_url = Column(Text, nullable=False)
    request_headers = Column(Text, nullable=True)
    request_body = Column(Text, nullable=True)
    response_status = Column(Integer, nullable=True)
    response_headers = Column(Text, nullable=True)
    response_body = Column(Text, nullable=True)
    elapsed_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    api = relationship("ApiDefinition", back_populates="debug_histories")

    __table_args__ = (
        Index("idx_debug_histories_api_id", "api_id", "created_at"),
    )


class ApiAuditLog(Base):
    """接口审计日志表"""
    __tablename__ = "api_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, nullable=False, index=True)
    api_id = Column(Integer, ForeignKey("api_definitions.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(Integer, nullable=False)
    action = Column(SQLEnum(AuditAction), nullable=False)
    resource_type = Column(String(20), default="api")
    resource_name = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    change_summary = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    api = relationship("ApiDefinition", back_populates="audit_logs")

    __table_args__ = (
        Index("idx_api_audit_logs_team_id", "team_id", "created_at"),
        Index("idx_api_audit_logs_api_id", "api_id", "created_at"),
    )


class ApiRecentVisit(Base):
    """接口最近访问表"""
    __tablename__ = "api_recent_visits"

    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, ForeignKey("api_definitions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    visited_at = Column(DateTime, default=datetime.utcnow)

    api = relationship("ApiDefinition", back_populates="recent_visits")

    __table_args__ = (
        UniqueConstraint("api_id", "user_id", name="uq_api_recent_visits_api_user"),
        Index("idx_api_recent_visits_user", "user_id", "visited_at"),
    )
