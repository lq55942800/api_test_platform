"""
Data Source Model
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class DataSource(Base):
    """Test case data source table"""
    __tablename__ = "test_case_data_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    source_type = Column(String(20), nullable=False)
    source_config = Column(Text, nullable=False)
    enabled = Column(Boolean, default=True)
    iteration_mode = Column(String(20), default="sequential")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    test_case = relationship("TestCase", back_populates="data_sources")
