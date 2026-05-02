"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os
import secrets


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用信息
    APP_NAME: str = "AutoTest API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./autotest.db")
    
    # 安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ENCRYPTION_MASTER_KEY: str = os.getenv("ENCRYPTION_MASTER_KEY", secrets.token_urlsafe(32))
    
    # JWT配置
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS配置
    CORS_ORIGINS: list = ["*"]
    
    # 环境管理限制
    MAX_ENVIRONMENTS_PER_TEAM: int = 20
    MAX_SERVICES_PER_ENVIRONMENT: int = 50
    MAX_DATABASES_PER_SERVICE: int = 10
    MAX_SERVERS_PER_SERVICE: int = 5
    MAX_VARIABLES_PER_ENVIRONMENT: int = 100
    MAX_VARIABLES_PER_SERVICE: int = 50

    # 接口管理限制
    MAX_APIS_PER_TEAM: int = 5000
    MAX_APIS_PER_MODULE: int = 500
    MAX_MODULES_PER_TEAM: int = 100
    MAX_MODULE_DEPTH: int = 3
    MAX_TAGS_PER_API: int = 10
    MAX_VERSIONS_PER_API: int = 20
    MAX_DEBUG_HISTORIES_PER_API: int = 50
    MAX_RECENT_VISITS: int = 10
    MAX_IMPORT_APIS: int = 500
    MAX_BATCH_OPERATION: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()
