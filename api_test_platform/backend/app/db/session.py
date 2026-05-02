"""
Database Session Configuration
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator
import os

# 数据库URL配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./autotest.db")

# 创建引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=os.getenv("SQL_ECHO", "false").lower() == "true"
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    """
    获取数据库会话
    用于FastAPI依赖注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
