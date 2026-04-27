"""
Test Case Models
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base


class TestCaseStatus(str, enum.Enum):
    """Test case status enumeration"""
    enabled = "enabled"
    disabled = "disabled"


class TestCasePriority(str, enum.Enum):
    """Test case priority enumeration"""
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class TestCase(Base):
    """Test case table"""
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    name = Column(String(100), nullable=False)
    module_id = Column(Integer, ForeignKey("test_case_modules.id"), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="enabled")
    priority = Column(String(5), default="P2")
    tags = Column(Text, nullable=True)
    variables = Column(Text, nullable=True)
    execution_condition = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    module = relationship("TestCaseModule", back_populates="test_cases")
    steps = relationship("TestCaseStep", back_populates="test_case", cascade="all, delete-orphan")
    data_sources = relationship("DataSource", back_populates="test_case", cascade="all, delete-orphan")
