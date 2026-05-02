"""
Test Case Step Model
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class TestCaseStep(Base):
    """Test case step table"""
    __tablename__ = "test_case_steps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False)
    api_id = Column(Integer, ForeignKey("api_definitions.id"), nullable=True)
    step_type = Column(String(20), default="api")
    parent_step_id = Column(Integer, ForeignKey("test_case_steps.id", ondelete="CASCADE"), nullable=True)
    step_name = Column(String(100), nullable=True)
    sort_order = Column(Integer, default=0)
    enabled = Column(Boolean, default=True)
    override_headers = Column(Text, nullable=True)
    override_params = Column(Text, nullable=True)
    override_body = Column(Text, nullable=True)
    override_body_type = Column(String(20), nullable=True)
    override_cookies = Column(Text, nullable=True)
    assertions = Column(Text, nullable=True)
    extractors = Column(Text, nullable=True)
    pre_script = Column(Text, nullable=True)
    post_script = Column(Text, nullable=True)
    timeout_config = Column(Text, nullable=True)
    execution_condition = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    test_case = relationship("TestCase", back_populates="steps")
    api = relationship("ApiDefinition")
    parent_step = relationship("TestCaseStep", remote_side=[id], backref="children_steps")
