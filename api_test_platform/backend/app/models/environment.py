"""
Environment Management Models
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
import enum


class ServiceType(str, enum.Enum):
    MICROSERVICE = "microservice"
    MODULE = "module"
    THIRD_PARTY = "third_party"


class ValueType(str, enum.Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"


class Environment(Base):
    __tablename__ = "environments"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False, index=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    team = relationship("Team", back_populates="environments")
    services = relationship("EnvService", back_populates="environment", cascade="all, delete-orphan")
    variables = relationship("EnvVariable", back_populates="environment", cascade="all, delete-orphan")


class EnvService(Base):
    __tablename__ = "env_services"

    id = Column(Integer, primary_key=True, index=True)
    environment_id = Column(Integer, ForeignKey("environments.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    service_type = Column(SQLEnum(ServiceType), default=ServiceType.MICROSERVICE)
    description = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    environment = relationship("Environment", back_populates="services")
    servers = relationship("EnvServer", back_populates="service", cascade="all, delete-orphan")
    databases = relationship("EnvDatabase", back_populates="service", cascade="all, delete-orphan")
    variables = relationship("EnvServiceVariable", back_populates="service", cascade="all, delete-orphan")


class EnvServer(Base):
    __tablename__ = "env_servers"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("env_services.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=True)
    protocol = Column(String(20), default="https")
    base_path = Column(String(255), default="")
    ssl_config = Column(Text, nullable=True)
    headers = Column(Text, nullable=True)
    timeout = Column(Integer, default=30000)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    service = relationship("EnvService", back_populates="servers")


class EnvDatabase(Base):
    __tablename__ = "env_databases"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("env_services.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    db_type = Column(String(50), nullable=False)
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=True)
    database = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False)
    password = Column(Text, nullable=False)
    charset = Column(String(20), default="utf8mb4")
    extra_config = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    service = relationship("EnvService", back_populates="databases")


class EnvVariable(Base):
    __tablename__ = "env_variables"

    id = Column(Integer, primary_key=True, index=True)
    environment_id = Column(Integer, ForeignKey("environments.id", ondelete="CASCADE"), nullable=False, index=True)
    key = Column(String(100), nullable=False, index=True)
    value = Column(Text, nullable=True)
    value_type = Column(SQLEnum(ValueType), default=ValueType.STRING)
    is_encrypted = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    environment = relationship("Environment", back_populates="variables")


class EnvServiceVariable(Base):
    __tablename__ = "env_service_variables"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("env_services.id", ondelete="CASCADE"), nullable=False, index=True)
    key = Column(String(100), nullable=False, index=True)
    value = Column(Text, nullable=True)
    value_type = Column(SQLEnum(ValueType), default=ValueType.STRING)
    is_encrypted = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    service = relationship("EnvService", back_populates="variables")
