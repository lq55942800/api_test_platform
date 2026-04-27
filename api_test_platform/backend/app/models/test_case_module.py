"""
Test Case Module Model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class TestCaseModule(Base):
    """Test case module table"""
    __tablename__ = "test_case_modules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    name = Column(String(50), nullable=False)
    parent_id = Column(Integer, ForeignKey("test_case_modules.id"), nullable=True)
    description = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    test_cases = relationship("TestCase", back_populates="module")
    children = relationship("TestCaseModule", backref="parent", remote_side=[id])
