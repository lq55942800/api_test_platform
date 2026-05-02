"""
接口调试引擎 - 集成变量管理器、超时管理器、前置/后置操作引擎、断言引擎
"""
import json
import re
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
import httpx

from app.models.api import ApiDefinition, ApiDebugHistory
from app.models.environment import Environment, EnvServer, EnvService
from app.services.variable_resolver import VariableResolver
from app.services.engines.variable_manager import VariableManager
from app.services.engines.timeout_manager import TimeoutManager, TimeoutConfig
from app.services.engines.pre_processor_engine import PreProcessorEngine
from app.services.engines.post_processor_engine import PostProcessorEngine
from app.services.engines.assertion_engine import AssertionEngine
from app.services.extractors.extractor_engine import ExtractorEngine
from app.core.logging import get_logger

logger = get_logger(__name__)


class DebugEngine:
    """接口调试引擎"""

    MAX_RESPONSE_SIZE = 10 * 1024 * 1024

    def __init__(self, db: Session):
        self.db = db
        self.resolver = VariableResolver(db)
        self.variable_manager = VariableManager()
        self.extractor_engine = ExtractorEngine()
        self.timeout_manager = TimeoutManager()
        self.pre_processor_engine = PreProcessorEngine(self.variable_manager, self.extractor_engine)
        self.post_processor_engine = PostProcessorEngine(self.variable_manager, self.extractor_engine)
        self.assertion_engine = AssertionEngine(self.variable_manager, self.extractor_engine)

    async def execute(
        self,
        api_id: int,
        environment_id: Optional[int],
        service_id: Optional[int] = None,
        param_overrides: Optional[Dict[str, Any]] = None,
        header_overrides: Optional[Dict[str, Any]] = None,
        body_overrides: Optional[str] = None,
        body_type: Optional[str] = None,
        cookie_overrides: Optional[List[Dict[str, Any]]] = None,
        pre_request_actions_overrides: Optional[List[Dict[str, Any]]] = None,
        post_request_actions_overrides: Optional[List[Dict[str, Any]]] = None,
        assertions_overrides: Optional[List[Dict[str, Any]]] = None,
        timeout_config_overrides: Optional[Dict[str, Any]] = None,
        user_id: int = 0,
    ) -> Dict[str, Any]:
        """执行调试请求"""
        logger.info(f"执行调试请求: api_id={api_id}, environment_id={environment_id}, service_id={service_id}, user_id={user_id}")

        api = self.db.query(ApiDefinition).filter(
            ApiDefinition.id == api_id,
            ApiDefinition.is_deleted == False
        ).first()
        if not api:
            logger.warning(f"调试请求失败，接口不存在: api_id={api_id}")
            raise HTTPException(status_code=404, detail="接口不存在")

        self.variable_manager.clear_scope("request")

        base_url = ""
        env_headers = {}
        env_config = {}
        if environment_id:
            env = self.db.query(Environment).filter(Environment.id == environment_id).first()
            if not env:
                logger.warning(f"调试请求失败，环境不存在: environment_id={environment_id}")
                raise HTTPException(status_code=404, detail="环境不存在")
            base_url, env_headers = self._get_base_url_and_headers(service_id or api.service_id, environment_id)
            env_vars = self.resolver.load_environment(environment_id)
            self.variable_manager.load_environment_vars(env_vars)
            logger.debug(f"环境配置加载完成: environment_id={environment_id}, base_url={base_url}, env_header_count={len(env_headers)}")

        timeout_config = self.timeout_manager.resolve_timeout(
            api_config={
                "connect_timeout": api.connect_timeout,
                "read_timeout": api.read_timeout,
                "write_timeout": api.write_timeout,
                "pool_timeout": api.pool_timeout,
                "sample_timeout": api.sample_timeout,
                "sql_timeout": api.sql_timeout,
                "script_timeout": api.script_timeout,
                "timeout_enabled": api.timeout_enabled,
            },
            env_config=env_config,
        )

        if timeout_config_overrides:
            if timeout_config_overrides.get("connect_timeout") is not None:
                timeout_config.connect_timeout = timeout_config_overrides["connect_timeout"]
            if timeout_config_overrides.get("read_timeout") is not None:
                timeout_config.read_timeout = timeout_config_overrides["read_timeout"]
            if timeout_config_overrides.get("write_timeout") is not None:
                timeout_config.write_timeout = timeout_config_overrides["write_timeout"]
            if timeout_config_overrides.get("pool_timeout") is not None:
                timeout_config.pool_timeout = timeout_config_overrides["pool_timeout"]
            if timeout_config_overrides.get("sample_timeout") is not None:
                timeout_config.sample_timeout = timeout_config_overrides["sample_timeout"]
            if timeout_config_overrides.get("sql_timeout") is not None:
                timeout_config.sql_timeout = timeout_config_overrides["sql_timeout"]
            if timeout_config_overrides.get("script_timeout") is not None:
                timeout_config.script_timeout = timeout_config_overrides["script_timeout"]
            if timeout_config_overrides.get("timeout_enabled") is not None:
                timeout_config.timeout_enabled = timeout_config_overrides["timeout_enabled"]
            logger.debug(f"超时配置已覆盖: api_id={api_id}")

        context = {
            "api": api,
            "environment_id": environment_id,
            "service_id": service_id,
            "timeout_config": timeout_config,
            "request_params": {},
            "db_session": self.db,
        }

        pre_request_actions = pre_request_actions_overrides if pre_request_actions_overrides is not None else []
        if not pre_request_actions_overrides and api.pre_request_actions:
            try:
                pre_request_actions = json.loads(api.pre_request_actions)
            except json.JSONDecodeError:
                logger.warning(f"前置操作JSON解析失败: api_id={api_id}")
                pre_request_actions = []

        pre_result = await self.pre_processor_engine.execute(pre_request_actions, context)
        pre_request_results = [
            {
                "id": r.get("id", ""),
                "name": r.get("name", ""),
                "type": r.get("type", ""),
                "success": r.get("success", True),
                "error": r.get("error"),
                "duration_ms": r.get("duration_ms", 0),
                "output": r.get("output"),
            }
            for r in pre_result.get("results", [])
        ]

        if not pre_result["success"]:
            error_msg = "前置操作执行失败"
            for r in pre_result.get("results", []):
                if not r.get("success") and r.get("error"):
                    error_msg = r["error"]
                    break
            logger.error(f"前置操作执行失败: api_id={api_id}, error={error_msg}")
            history = self._save_history(
                api_id=api_id, environment_id=environment_id, user_id=user_id,
                request_method=api.method, request_url=base_url + api.path,
                request_headers=json.dumps(env_headers, ensure_ascii=False),
                request_body=None, response_status=None,
                response_headers=None, response_body=None,
                elapsed_ms=None, error_message=error_msg,
            )
            return {
                "status_code": None,
                "headers": None,
                "body": None,
                "elapsed_ms": None,
                "error_message": error_msg,
                "history_id": history.id,
                "request_url": base_url + api.path,
                "request_headers": env_headers,
                "pre_request_results": pre_request_results,
                "post_request_results": None,
                "assertion_results": None,
                "assertion_summary": None,
                "variables_snapshot": self.variable_manager.get_all("request"),
                "timeout_config": {
                    "connect_timeout": timeout_config.connect_timeout,
                    "read_timeout": timeout_config.read_timeout,
                    "write_timeout": timeout_config.write_timeout,
                    "pool_timeout": timeout_config.pool_timeout,
                    "sample_timeout": timeout_config.sample_timeout,
                    "sql_timeout": timeout_config.sql_timeout,
                    "script_timeout": timeout_config.script_timeout,
                },
            }

        resolved = self._resolve_params(api, environment_id, param_overrides or {}, header_overrides or {}, body_overrides, body_type, cookie_overrides)
        request_params = context.get("request_params", {})
        if request_params.get("header"):
            resolved["header_params"].update(request_params["header"])
        if request_params.get("query"):
            resolved["query_params"].update(request_params["query"])
        if request_params.get("cookie"):
            resolved["cookie_params"].update(request_params["cookie"])
        if request_params.get("body"):
            resolved["body"] = request_params["body"]

        url = self._build_url(base_url, api.path, resolved.get("query_params", {}), resolved.get("path_params", {}))
        final_headers = {**env_headers, **resolved.get("header_params", {})}

        if not url.startswith(("http://", "https://")):
            logger.warning(f"请求URL缺少协议前缀: api_id={api_id}, url={url}")
            return self._handle_error(
                api_id, environment_id, user_id, api.method, url, env_headers, None,
                "请求URL缺少协议前缀，请检查接口是否关联了正确的服务，或环境配置中的服务器地址是否正确设置",
                pre_request_results=pre_request_results,
            )

        headers = {**env_headers, **resolved.get("header_params", {})}
        cookies = resolved.get("cookie_params", {})
        body = resolved.get("body")

        httpx_timeout = self.timeout_manager.to_httpx_timeout(timeout_config)

        logger.debug(f"发送HTTP请求: api_id={api_id}, method={api.method}, url={url}")

        try:
            async with httpx.AsyncClient(
                timeout=httpx_timeout,
                follow_redirects=True,
                max_redirects=10,
                verify=True
            ) as client:
                request = self._build_request(api.method, url, headers, cookies, body, api.body_type)
                start_time = datetime.utcnow()
                response = await client.send(request)
                elapsed_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

                response_body = response.text
                if len(response_body.encode('utf-8', errors='replace')) > self.MAX_RESPONSE_SIZE:
                    response_body = response_body[:self.MAX_RESPONSE_SIZE]
                    logger.warning(f"响应体过大已截断: api_id={api_id}, max_size={self.MAX_RESPONSE_SIZE}")

                response_headers = dict(response.headers)

                response_cookies = {}
                for cookie_name in response.cookies.jar:
                    response_cookies[cookie_name.name] = cookie_name.value

                context["response_data"] = {
                    "status_code": response.status_code,
                    "headers": response_headers,
                    "body": response_body,
                    "cookies": response_cookies,
                    "elapsed_ms": elapsed_ms,
                    "url": str(response.url),
                }

                post_request_actions = post_request_actions_overrides if post_request_actions_overrides is not None else []
                if not post_request_actions_overrides and api.post_request_actions:
                    try:
                        post_request_actions = json.loads(api.post_request_actions)
                    except json.JSONDecodeError:
                        logger.warning(f"后置操作JSON解析失败: api_id={api_id}")
                        post_request_actions = []

                post_result = await self.post_processor_engine.execute(post_request_actions, context)
                post_request_results = [
                    {
                        "id": r.get("id", ""),
                        "name": r.get("name", ""),
                        "type": r.get("type", ""),
                        "success": r.get("success", True),
                        "error": r.get("error"),
                        "duration_ms": r.get("duration_ms", 0),
                        "output": r.get("output"),
                    }
                    for r in post_result.get("results", [])
                ]

                assertions = assertions_overrides if assertions_overrides is not None else []
                if not assertions_overrides and api.assertions:
                    try:
                        assertions = json.loads(api.assertions)
                    except json.JSONDecodeError:
                        logger.warning(f"断言JSON解析失败: api_id={api_id}")
                        assertions = []

                assertion_result = await self.assertion_engine.execute(assertions, context)
                assertion_results = assertion_result.get("results", [])
                assertion_summary = assertion_result.get("summary", {})

                logger.debug(f"断言执行完成: api_id={api_id}, total={assertion_summary.get('total', 0)}, passed={assertion_summary.get('passed', 0)}, failed={assertion_summary.get('failed', 0)}")

                history = self._save_history(
                    api_id=api_id, environment_id=environment_id, user_id=user_id,
                    request_method=api.method, request_url=url,
                    request_headers=json.dumps(headers, ensure_ascii=False),
                    request_body=json.dumps(body, ensure_ascii=False) if body else None,
                    response_status=response.status_code,
                    response_headers=json.dumps(response_headers, ensure_ascii=False),
                    response_body=response_body,
                    elapsed_ms=elapsed_ms,
                    error_message=None,
                )

                api.last_debug_at = datetime.utcnow()
                api.last_debug_status = "success" if response.status_code < 400 else "fail"
                self.db.commit()

                logger.info(f"调试请求完成: api_id={api_id}, status_code={response.status_code}, elapsed_ms={elapsed_ms}")
                return {
                    "status_code": response.status_code,
                    "headers": response_headers,
                    "body": response_body,
                    "elapsed_ms": elapsed_ms,
                    "error_message": None,
                    "history_id": history.id,
                    "request_url": url,
                    "request_headers": final_headers,
                    "request_body": body,
                    "pre_request_results": pre_request_results,
                    "post_request_results": post_request_results,
                    "assertion_results": assertion_results,
                    "assertion_summary": assertion_summary,
                    "variables_snapshot": self.variable_manager.get_all("request"),
                    "timeout_config": {
                        "connect_timeout": timeout_config.connect_timeout,
                        "read_timeout": timeout_config.read_timeout,
                        "write_timeout": timeout_config.write_timeout,
                        "pool_timeout": timeout_config.pool_timeout,
                        "sample_timeout": timeout_config.sample_timeout,
                        "sql_timeout": timeout_config.sql_timeout,
                        "script_timeout": timeout_config.script_timeout,
                    },
                }

        except httpx.TimeoutException as e:
            error_type = "连接超时" if isinstance(e, httpx.ConnectTimeout) else \
                         "读取超时" if isinstance(e, httpx.ReadTimeout) else \
                         "发送超时" if isinstance(e, httpx.WriteTimeout) else \
                         "连接池超时" if isinstance(e, httpx.PoolTimeout) else "请求超时"
            logger.error(f"调试请求超时: api_id={api_id}, error_type={error_type}, timeout={timeout_config.read_timeout}ms")
            return self._handle_error(
                api_id, environment_id, user_id, api.method, url, headers, body,
                f"{error_type}({timeout_config.read_timeout}ms)",
                pre_request_results=pre_request_results,
            )
        except httpx.ConnectError:
            logger.error(f"调试请求连接失败: api_id={api_id}, url={url}")
            return self._handle_error(
                api_id, environment_id, user_id, api.method, url, headers, body,
                "无法连接到目标服务器",
                pre_request_results=pre_request_results,
            )
        except httpx.TooManyRedirects:
            logger.warning(f"调试请求重定向过多: api_id={api_id}, url={url}")
            return self._handle_error(
                api_id, environment_id, user_id, api.method, url, headers, body,
                "重定向次数超过限制(10次)",
                pre_request_results=pre_request_results,
            )
        except Exception as e:
            logger.error(f"调试请求异常: api_id={api_id}, url={url}, error={str(e)}")
            return self._handle_error(
                api_id, environment_id, user_id, api.method, url, headers, body,
                str(e),
                pre_request_results=pre_request_results,
            )

    def get_debug_histories(
        self,
        api_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[list, int]:
        """获取调试历史"""
        logger.info(f"获取调试历史: api_id={api_id}, page={page}, page_size={page_size}")

        query = self.db.query(ApiDebugHistory).filter(ApiDebugHistory.api_id == api_id)
        total = query.count()
        items = query.order_by(ApiDebugHistory.created_at.desc()) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()

        logger.debug(f"调试历史查询结果: api_id={api_id}, total={total}, returned={len(items)}")
        return items, total

    def _resolve_params(self, api: ApiDefinition, environment_id: Optional[int], overrides: Dict, header_overrides: Dict, body_overrides: Optional[str], body_type: Optional[str], cookie_overrides: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """解析参数，替换变量"""
        logger.debug(f"解析参数: api_id={api.id}, environment_id={environment_id}")

        result = {"query_params": {}, "header_params": {}, "cookie_params": {}, "path_params": {}}

        for field, target_key in [
            ("query_params", "query_params"),
            ("header_params", "header_params"),
            ("cookie_params", "cookie_params"),
            ("path_params", "path_params"),
        ]:
            raw = getattr(api, field)
            if raw:
                params = json.loads(raw)
                for p in params:
                    name = p.get("name", "")
                    value = p.get("default_value", p.get("example", ""))
                    if name in overrides:
                        value = overrides[name]
                    if environment_id and isinstance(value, str):
                        value, _, _ = self.resolver.resolve(value, environment_id)
                    if isinstance(value, str):
                        value = self.variable_manager.resolve(value)
                    result[target_key][name] = value

        if header_overrides:
            for name, value in header_overrides.items():
                if value is not None and value != "":
                    result["header_params"][name] = value

        if cookie_overrides:
            for cookie in cookie_overrides:
                name = cookie.get("name", "")
                value = cookie.get("default_value", cookie.get("example", ""))
                if name and value:
                    if environment_id and isinstance(value, str):
                        value, _, _ = self.resolver.resolve(value, environment_id)
                    if isinstance(value, str):
                        value = self.variable_manager.resolve(value)
                    result["cookie_params"][name] = value

        body = None
        if body_overrides:
            if isinstance(body_overrides, str):
                try:
                    body = json.loads(body_overrides)
                except json.JSONDecodeError:
                    body = body_overrides
            else:
                body = body_overrides
        elif api.body_definition:
            body_raw = api.body_definition
            if isinstance(body_raw, str):
                try:
                    body = json.loads(body_raw)
                except json.JSONDecodeError:
                    body = body_raw
            else:
                body = body_raw

            if environment_id and isinstance(body, str):
                body, _, _ = self.resolver.resolve(body, environment_id)
            elif environment_id and isinstance(body, dict):
                body_str = json.dumps(body, ensure_ascii=False)
                body_str, _, _ = self.resolver.resolve(body_str, environment_id)
                try:
                    body = json.loads(body_str)
                except json.JSONDecodeError:
                    body = body_str

            if isinstance(body, str):
                body = self.variable_manager.resolve(body)
            elif isinstance(body, dict):
                body_str = json.dumps(body, ensure_ascii=False)
                body_str = self.variable_manager.resolve(body_str)
                try:
                    body = json.loads(body_str)
                except json.JSONDecodeError:
                    body = body_str

        result["body"] = body
        logger.debug(f"参数解析完成: api_id={api.id}, param_count={sum(len(v) for v in result.values() if isinstance(v, dict))}, has_body={body is not None}")
        return result

    def _build_url(self, base_url: str, path: str, query_params: Dict, path_params: Dict) -> str:
        """构建请求URL"""
        url_path = path
        for name, value in path_params.items():
            url_path = url_path.replace(f"{{{name}}}", str(value))

        url = f"{base_url}{url_path}" if base_url else url_path

        if query_params:
            query_parts = []
            for name, value in query_params.items():
                if value is not None:
                    query_parts.append(f"{name}={value}")
            if query_parts:
                url += "?" + "&".join(query_parts)

        logger.debug(f"构建URL: base_url={base_url}, path={path}, final_url={url}")
        return url

    def _build_request(self, method: str, url: str, headers: Dict, cookies: Dict, body: Any, body_type) -> httpx.Request:
        """构建httpx请求"""
        kwargs = {"method": method, "url": url, "headers": headers, "cookies": cookies}

        body_type_str = body_type.value if hasattr(body_type, 'value') else str(body_type) if body_type else None

        if method not in ("GET", "HEAD", "DELETE") and body is not None:
            if body_type_str == "json":
                kwargs["json"] = body if isinstance(body, (dict, list)) else body
            elif body_type_str in ("form-data", "x-www-form-urlencoded"):
                kwargs["data"] = body if isinstance(body, dict) else body
            else:
                kwargs["content"] = json.dumps(body, ensure_ascii=False) if isinstance(body, (dict, list)) else str(body)

        logger.debug(f"构建请求: method={method}, url={url}, body_type={body_type_str}, has_body={body is not None}")
        return httpx.Request(**kwargs)

    def _save_history(self, **kwargs) -> ApiDebugHistory:
        """保存调试历史"""
        history = ApiDebugHistory(**kwargs)
        self.db.add(history)
        self.db.flush()
        logger.debug(f"保存调试历史: history_id={history.id}, api_id={kwargs.get('api_id')}")
        return history

    def _handle_error(
        self, api_id, environment_id, user_id, method, url, headers, body, error_msg,
        pre_request_results=None,
    ) -> Dict[str, Any]:
        """处理调试错误"""
        logger.error(f"调试错误: api_id={api_id}, method={method}, url={url}, error={error_msg}")

        history = self._save_history(
            api_id=api_id,
            environment_id=environment_id,
            user_id=user_id,
            request_method=method,
            request_url=url,
            request_headers=json.dumps(headers, ensure_ascii=False) if headers else None,
            request_body=json.dumps(body, ensure_ascii=False) if body else None,
            response_status=None,
            response_headers=None,
            response_body=None,
            elapsed_ms=None,
            error_message=error_msg,
        )
        self.db.commit()

        return {
            "status_code": None,
            "headers": None,
            "body": None,
            "elapsed_ms": None,
            "error_message": error_msg,
            "history_id": history.id,
            "request_url": url,
            "request_headers": headers,
            "request_body": body,
            "pre_request_results": pre_request_results,
            "post_request_results": None,
            "assertion_results": None,
            "assertion_summary": None,
            "variables_snapshot": self.variable_manager.get_all("request"),
            "timeout_config": None,
        }

    def _get_base_url_and_headers(self, service_id: Optional[int], environment_id: int) -> tuple[str, Dict[str, str]]:
        """根据服务ID和环境ID获取基础URL和公共请求头"""
        logger.debug(f"获取基础URL和请求头: service_id={service_id}, environment_id={environment_id}")

        base_url = ""
        headers = {}

        if service_id:
            service = self.db.query(EnvService).filter(EnvService.id == service_id).first()
            if service and service.environment_id == environment_id:
                for server in service.servers:
                    url = f"{server.protocol}://{server.host}"
                    if server.port:
                        url += f":{server.port}"
                    if server.base_path:
                        url += server.base_path
                    base_url = url
                    if server.headers:
                        try:
                            headers.update(json.loads(server.headers))
                        except json.JSONDecodeError:
                            logger.warning(f"服务器headers JSON解析失败: service_id={service_id}, server_id={server.id}")
                    if server.is_default or not base_url:
                        break
                    if base_url:
                        break

        if not base_url:
            env = self.db.query(Environment).filter(Environment.id == environment_id).first()
            if env:
                first_server = None
                for service in env.services:
                    for server in service.servers:
                        if first_server is None:
                            first_server = server
                        if server.is_default:
                            url = f"{server.protocol}://{server.host}"
                            if server.port:
                                url += f":{server.port}"
                            if server.base_path:
                                url += server.base_path
                            base_url = url
                            if server.headers:
                                try:
                                    headers.update(json.loads(server.headers))
                                except json.JSONDecodeError:
                                    logger.warning(f"服务器headers JSON解析失败: environment_id={environment_id}, server_id={server.id}")
                            break
                    if base_url:
                        break

                if not base_url and first_server:
                    url = f"{first_server.protocol}://{first_server.host}"
                    if first_server.port:
                        url += f":{first_server.port}"
                    if first_server.base_path:
                        url += first_server.base_path
                    base_url = url
                    if first_server.headers:
                        try:
                            headers.update(json.loads(first_server.headers))
                        except json.JSONDecodeError:
                            logger.warning(f"服务器headers JSON解析失败: environment_id={environment_id}, server_id={first_server.id}")

        if not base_url:
            logger.warning(f"未找到有效的服务器配置: service_id={service_id}, environment_id={environment_id}")

        logger.debug(f"获取基础URL完成: service_id={service_id}, environment_id={environment_id}, base_url={base_url}, header_count={len(headers)}")
        return base_url, headers
