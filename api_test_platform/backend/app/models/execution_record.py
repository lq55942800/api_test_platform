"""
Execution Record Models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class TestCaseExecutionRecord(Base):
    """Test case execution record table"""
    __tablename__ = "test_case_execution_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False)
    test_case_name = Column(String(100), nullable=False)
    test_case_snapshot = Column(Text, nullable=True)
    environment_id = Column(Integer, ForeignKey("environments.id"), nullable=True)
    environment_name = Column(String(50), nullable=True)
    execution_type = Column(String(20), nullable=True)
    status = Column(String(20), nullable=False)
    total_steps = Column(Integer, default=0)
    passed_steps = Column(Integer, default=0)
    failed_steps = Column(Integer, default=0)
    skipped_steps = Column(Integer, default=0)
    data_iteration_count = Column(Integer, default=1)
    data_iteration_passed = Column(Integer, default=0)
    data_iteration_failed = Column(Integer, default=0)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)
    executor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    executor_name = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_case_exec_records_case", "test_case_id", "created_at"),
        Index("idx_case_exec_records_team", "team_id", "created_at"),
    )


class StepExecutionRecord(Base):
    """Step execution record table"""
    __tablename__ = "step_execution_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_execution_id = Column(Integer, ForeignKey("test_case_execution_records.id"), nullable=False)
    step_id = Column(Integer, nullable=True)
    step_name = Column(String(100), nullable=True)
    step_order = Column(Integer, nullable=True)
    api_id = Column(Integer, nullable=True)
    api_name = Column(String(100), nullable=True)
    status = Column(String(20), nullable=False)
    skip_reason = Column(Text, nullable=True)
    request_url = Column(Text, nullable=True)
    request_method = Column(String(10), nullable=True)
    request_headers = Column(Text, nullable=True)
    request_body = Column(Text, nullable=True)
    response_status = Column(Integer, nullable=True)
    response_headers = Column(Text, nullable=True)
    response_body = Column(Text, nullable=True)
    response_time = Column(Integer, nullable=True)
    assertions = Column(Text, nullable=True)
    extractors = Column(Text, nullable=True)
    pre_actions = Column(Text, nullable=True)
    post_actions = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)

    __table_args__ = (
        Index("idx_step_exec_records_case", "case_execution_id"),
    )
