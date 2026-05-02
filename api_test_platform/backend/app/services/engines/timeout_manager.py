from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import httpx


class TimeoutConfig(BaseModel):
    connect_timeout: int = Field(default=5000, ge=1, le=60000, description="连接超时(毫秒)")
    read_timeout: int = Field(default=30000, ge=1, le=300000, description="读取超时(毫秒)")
    write_timeout: int = Field(default=10000, ge=1, le=60000, description="发送超时(毫秒)")
    pool_timeout: int = Field(default=5000, ge=1, le=30000, description="连接池超时(毫秒)")
    sample_timeout: int = Field(default=60000, ge=1, le=600000, description="全局超时(毫秒)")
    sql_timeout: int = Field(default=30000, ge=1, le=300000, description="SQL超时(毫秒)")
    script_timeout: int = Field(default=10000, ge=1, le=120000, description="脚本超时(毫秒)")
    timeout_enabled: bool = Field(default=True, description="是否启用自定义超时")


PRESET_TEMPLATES = {
    "fast": {
        "connect_timeout": 3000,
        "read_timeout": 10000,
        "write_timeout": 5000,
        "pool_timeout": 3000,
        "sample_timeout": 15000,
        "sql_timeout": 10000,
        "script_timeout": 5000,
    },
    "standard": {
        "connect_timeout": 5000,
        "read_timeout": 30000,
        "write_timeout": 10000,
        "pool_timeout": 5000,
        "sample_timeout": 60000,
        "sql_timeout": 30000,
        "script_timeout": 10000,
    },
    "slow": {
        "connect_timeout": 10000,
        "read_timeout": 120000,
        "write_timeout": 30000,
        "pool_timeout": 5000,
        "sample_timeout": 180000,
        "sql_timeout": 60000,
        "script_timeout": 30000,
    },
    "file_upload": {
        "connect_timeout": 10000,
        "read_timeout": 300000,
        "write_timeout": 60000,
        "pool_timeout": 5000,
        "sample_timeout": 420000,
        "sql_timeout": 30000,
        "script_timeout": 10000,
    },
    "database_query": {
        "connect_timeout": 5000,
        "read_timeout": 30000,
        "write_timeout": 10000,
        "pool_timeout": 5000,
        "sample_timeout": 300000,
        "sql_timeout": 120000,
        "script_timeout": 10000,
    },
}


class TimeoutManager:
    SYSTEM_DEFAULTS = {
        "connect_timeout": 5000,
        "read_timeout": 30000,
        "write_timeout": 10000,
        "pool_timeout": 5000,
        "sample_timeout": 60000,
        "sql_timeout": 30000,
        "script_timeout": 10000,
    }

    TIMEOUT_KEYS = [
        "connect_timeout", "read_timeout", "write_timeout",
        "pool_timeout", "sample_timeout", "sql_timeout", "script_timeout",
    ]

    def resolve_timeout(
        self,
        api_config: Dict[str, Any],
        env_config: Optional[Dict[str, Any]] = None,
        project_config: Optional[Dict[str, Any]] = None,
        pre_sample_timeout: Optional[int] = None,
    ) -> TimeoutConfig:
        resolved = dict(self.SYSTEM_DEFAULTS)

        if project_config and project_config.get("timeout_defaults"):
            for key in self.TIMEOUT_KEYS:
                if project_config["timeout_defaults"].get(key) is not None:
                    resolved[key] = project_config["timeout_defaults"][key]

        if env_config and env_config.get("timeout_defaults"):
            for key in self.TIMEOUT_KEYS:
                if env_config["timeout_defaults"].get(key) is not None:
                    resolved[key] = env_config["timeout_defaults"][key]

        if api_config.get("timeout_enabled", True):
            for key in self.TIMEOUT_KEYS:
                if api_config.get(key) is not None:
                    resolved[key] = api_config[key]

        if pre_sample_timeout is not None:
            resolved["sample_timeout"] = pre_sample_timeout

        resolved["timeout_enabled"] = api_config.get("timeout_enabled", True)
        return TimeoutConfig(**resolved)

    def to_httpx_timeout(self, config: TimeoutConfig) -> httpx.Timeout:
        return httpx.Timeout(
            connect=config.connect_timeout / 1000.0,
            read=config.read_timeout / 1000.0,
            write=config.write_timeout / 1000.0,
            pool=config.pool_timeout / 1000.0,
        )

    def get_preset_template(self, name: str) -> Optional[Dict[str, int]]:
        return PRESET_TEMPLATES.get(name)

    def get_all_presets(self) -> Dict[str, Dict[str, int]]:
        return dict(PRESET_TEMPLATES)
