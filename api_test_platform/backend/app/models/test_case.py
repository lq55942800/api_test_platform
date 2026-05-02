"""
Test Case Models
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import json

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
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    team = relationship("Team", back_populates="test_cases")
    creator = relationship("User", back_populates="test_cases_created")
    module = relationship("TestCaseModule", back_populates="test_cases")
    steps = relationship("TestCaseStep", back_populates="test_case", cascade="all, delete-orphan")

    @property
    def tags_list(self):
        """获取tags列表"""
        if self.tags:
            try:
                return json.loads(self.tags)
            except:
                return []
        return []
    
    @tags_list.setter
    def tags_list(self, value):
        """设置tags列表"""
        self.tags = json.dumps(value, ensure_ascii=False) if value else None
    
    @property
    def variables_list(self):
        """获取variables列表"""
        if self.variables:
            try:
                return json.loads(self.variables)
            except:
                return []
        return []
    
    @variables_list.setter
    def variables_list(self, value):
        """设置variables列表"""
        self.variables = json.dumps(value, ensure_ascii=False) if value else None
