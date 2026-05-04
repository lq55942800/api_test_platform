"""
基础模型 - Team and User
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class Team(Base):
    """团队表"""
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    environments = relationship("Environment", back_populates="team")
    apis = relationship("ApiDefinition", back_populates="team")
    test_cases = relationship("TestCase", back_populates="team")
    modules = relationship("TestCaseModule", back_populates="team")


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    last_login_at = Column(DateTime, nullable=True)
    login_fail_count = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    apis_created = relationship("ApiDefinition", foreign_keys="ApiDefinition.created_by", back_populates="creator")
    apis_updated = relationship("ApiDefinition", foreign_keys="ApiDefinition.updated_by", back_populates="updater")
    test_cases_created = relationship("TestCase", back_populates="creator")


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    role = Column(String(20), default="tester")
    status = Column(String(20), default="active")
    joined_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("team_id", "user_id", name="uq_team_user"),
    )
