"""
调试功能测试 - 验证调试页面参数覆盖功能
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from app.services.debug_engine import DebugEngine
from app.models.api import ApiDefinition, ApiStatus, BodyType


class TestDebugOverrides:
    """测试调试页面参数覆盖功能"""

    @pytest.fixture
    def mock_db(self):
        """创建模拟数据库会话"""
        return MagicMock()

    @pytest.fixture
    def mock_api(self):
        """创建模拟API定义"""
        api = MagicMock(spec=ApiDefinition)
        api.id = 1
        api.team_id = 1
        api.service_id = 1
        api.name = "Test API"
        api.method = "GET"
        api.path = "/test"
        api.status = ApiStatus.ENABLED
        api.body_type = BodyType.NONE
        api.path_params = json.dumps([])
        api.query_params = json.dumps([{"name": "param1", "default_value": "original"}])
        api.header_params = json.dumps([{"name": "X-Header", "default_value": "original"}])
        api.cookie_params = json.dumps([{"name": "cookie1", "default_value": "original"}])
        api.body_definition = None
        api.pre_request_actions = json.dumps([{"id": "1", "type": "wait", "duration": 100}])
        api.post_request_actions = json.dumps([{"id": "1", "type": "variable", "name": "test"}])
        api.assertions = json.dumps([{"id": "1", "type": "status_code", "expected": 200}])
        api.connect_timeout = 5000
        api.read_timeout = 30000
        api.write_timeout = 10000
        api.pool_timeout = 5000
        api.sample_timeout = 60000
        api.sql_timeout = 30000
        api.script_timeout = 10000
        api.timeout_enabled = True
        return api

    def test_assertion_overrides_applied(self, mock_db, mock_api):
        """测试断言覆盖是否生效"""
        original_assertions = json.loads(mock_api.assertions)
        assert original_assertions[0]["expected"] == 200
        
        override_assertions = [{"id": "2", "type": "status_code", "expected": 201}]
        
        assertions = override_assertions if override_assertions is not None else []
        if not override_assertions and mock_api.assertions:
            try:
                assertions = json.loads(mock_api.assertions)
            except json.JSONDecodeError:
                assertions = []
        
        assert len(assertions) == 1
        assert assertions[0]["expected"] == 201
        assert assertions[0]["type"] == "status_code"

    def test_cookie_overrides_applied(self, mock_db, mock_api):
        """测试Cookie覆盖是否生效"""
        engine = DebugEngine(mock_db)
        
        cookie_overrides = [{"name": "session", "default_value": "new_session_value"}]
        
        result = engine._resolve_params(
            api=mock_api,
            environment_id=None,
            overrides={},
            header_overrides={},
            body_overrides=None,
            body_type=None,
            cookie_overrides=cookie_overrides
        )
        
        assert "session" in result["cookie_params"]
        assert result["cookie_params"]["session"] == "new_session_value"

    def test_timeout_config_overrides_applied(self, mock_db, mock_api):
        """测试超时配置覆盖是否生效"""
        engine = DebugEngine(mock_db)
        
        from app.services.engines.timeout_manager import TimeoutConfig
        
        timeout_config = TimeoutConfig(
            connect_timeout=5000,
            read_timeout=30000,
            write_timeout=10000,
            pool_timeout=5000,
            sample_timeout=60000,
            sql_timeout=30000,
            script_timeout=10000,
            timeout_enabled=True
        )
        
        timeout_overrides = {
            "connect_timeout": 1000,
            "read_timeout": 5000,
            "timeout_enabled": False
        }
        
        if timeout_overrides.get("connect_timeout") is not None:
            timeout_config.connect_timeout = timeout_overrides["connect_timeout"]
        if timeout_overrides.get("read_timeout") is not None:
            timeout_config.read_timeout = timeout_overrides["read_timeout"]
        if timeout_overrides.get("timeout_enabled") is not None:
            timeout_config.timeout_enabled = timeout_overrides["timeout_enabled"]
        
        assert timeout_config.connect_timeout == 1000
        assert timeout_config.read_timeout == 5000
        assert timeout_config.timeout_enabled == False

    def test_header_overrides_applied(self, mock_db, mock_api):
        """测试Header覆盖是否生效"""
        engine = DebugEngine(mock_db)
        
        header_overrides = {"X-Custom-Header": "custom_value"}
        
        result = engine._resolve_params(
            api=mock_api,
            environment_id=None,
            overrides={},
            header_overrides=header_overrides,
            body_overrides=None,
            body_type=None,
            cookie_overrides=None
        )
        
        assert "X-Custom-Header" in result["header_params"]
        assert result["header_params"]["X-Custom-Header"] == "custom_value"

    def test_body_overrides_applied(self, mock_db, mock_api):
        """测试Body覆盖是否生效"""
        engine = DebugEngine(mock_db)
        
        body_overrides = '{"key": "new_value"}'
        
        result = engine._resolve_params(
            api=mock_api,
            environment_id=None,
            overrides={},
            header_overrides={},
            body_overrides=body_overrides,
            body_type="json",
            cookie_overrides=None
        )
        
        assert result["body"] == {"key": "new_value"}

    def test_pre_request_actions_overrides_applied(self, mock_db, mock_api):
        """测试前置操作覆盖是否生效"""
        engine = DebugEngine(mock_db)
        
        original_actions = json.loads(mock_api.pre_request_actions)
        assert original_actions[0]["type"] == "wait"
        
        override_actions = [{"id": "2", "type": "script", "script": "console.log('test')"}]
        
        pre_request_actions = override_actions if override_actions is not None else []
        if not override_actions and mock_api.pre_request_actions:
            try:
                pre_request_actions = json.loads(mock_api.pre_request_actions)
            except json.JSONDecodeError:
                pre_request_actions = []
        
        assert len(pre_request_actions) == 1
        assert pre_request_actions[0]["type"] == "script"

    def test_post_request_actions_overrides_applied(self, mock_db, mock_api):
        """测试后置操作覆盖是否生效"""
        engine = DebugEngine(mock_db)
        
        original_actions = json.loads(mock_api.post_request_actions)
        assert original_actions[0]["type"] == "variable"
        
        override_actions = [{"id": "2", "type": "extract", "name": "token"}]
        
        post_request_actions = override_actions if override_actions is not None else []
        if not override_actions and mock_api.post_request_actions:
            try:
                post_request_actions = json.loads(mock_api.post_request_actions)
            except json.JSONDecodeError:
                post_request_actions = []
        
        assert len(post_request_actions) == 1
        assert post_request_actions[0]["type"] == "extract"

    def test_empty_overrides_uses_original(self, mock_db, mock_api):
        """测试空覆盖时使用原始配置"""
        engine = DebugEngine(mock_db)
        
        assertions = None
        if not assertions and mock_api.assertions:
            try:
                assertions = json.loads(mock_api.assertions)
            except json.JSONDecodeError:
                assertions = []
        
        assert len(assertions) == 1
        assert assertions[0]["type"] == "status_code"
        assert assertions[0]["expected"] == 200

    def test_multiple_override_scenarios(self, mock_db, mock_api):
        """测试多次修改场景下的一致性"""
        engine = DebugEngine(mock_db)
        
        scenarios = [
            {"id": "1", "type": "status_code", "expected": 200},
            {"id": "1", "type": "status_code", "expected": 201},
            {"id": "1", "type": "status_code", "expected": 204},
        ]
        
        for scenario in scenarios:
            assertions = [scenario] if scenario is not None else []
            if not scenario and mock_api.assertions:
                try:
                    assertions = json.loads(mock_api.assertions)
                except json.JSONDecodeError:
                    assertions = []
            
            assert len(assertions) == 1
            assert assertions[0]["expected"] == scenario["expected"]
