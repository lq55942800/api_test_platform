"""
接口导入引擎
"""
import json
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.api import ApiDefinition, ApiStatus, BodyType
from app.utils.path_validator import PathValidator
from app.core.config import settings


class ImportParser(ABC):
    """导入解析器基类"""
    @abstractmethod
    def parse(self, content: str) -> List[Dict[str, Any]]:
        pass


class Swagger2Parser(ImportParser):
    """Swagger 2.0 解析器"""

    def parse(self, content: str) -> List[Dict[str, Any]]:
        try:
            spec = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Swagger文件JSON解析失败")

        if "swagger" not in spec:
            raise HTTPException(status_code=400, detail="不是有效的Swagger 2.0文件")

        results = []
        base_path = spec.get("basePath", "")
        definitions = spec.get("definitions", {})

        for path, methods in spec.get("paths", {}).items():
            full_path = f"{base_path}{path}" if base_path else path
            for method, operation in methods.items():
                if method.lower() not in ("get", "post", "put", "patch", "delete", "head", "options"):
                    continue
                api_def = self._convert_operation(full_path, method.upper(), operation, definitions)
                results.append(api_def)

        return results

    def _convert_operation(self, path: str, method: str, operation: Dict, definitions: Dict) -> Dict[str, Any]:
        """转换Swagger操作为内部模型"""
        path_params = self._extract_params(operation.get("parameters", []), "path", definitions)
        query_params = self._extract_params(operation.get("parameters", []), "query", definitions)
        header_params = self._extract_params(operation.get("parameters", []), "header", definitions)
        cookie_params = self._extract_params(operation.get("parameters", []), "cookie", definitions)

        body_type = BodyType.NONE
        body_definition = None
        for param in operation.get("parameters", []):
            if param.get("in") == "body" and param.get("schema"):
                body_type = BodyType.JSON
                body_definition = self._resolve_schema(param["schema"], definitions)

        responses = []
        for code, resp in operation.get("responses", {}).items():
            try:
                status_code = int(code)
            except ValueError:
                continue
            resp_def = {
                "status_code": status_code,
                "description": resp.get("description", ""),
            }
            if resp.get("schema"):
                resp_def["body_schema"] = self._resolve_schema(resp["schema"], definitions)
            responses.append(resp_def)

        return {
            "name": operation.get("summary", operation.get("operationId", f"{method} {path}")),
            "method": method,
            "path": path,
            "description": operation.get("description", ""),
            "path_params": path_params,
            "query_params": query_params,
            "header_params": header_params,
            "cookie_params": cookie_params,
            "body_type": body_type.value,
            "body_definition": body_definition,
            "responses": responses,
        }

    def _extract_params(self, parameters: List[Dict], location: str, definitions: Dict) -> List[Dict]:
        """提取指定位置的参数"""
        result = []
        for param in parameters:
            if param.get("in") == location:
                p = {
                    "name": param.get("name", ""),
                    "param_type": self._map_type(param.get("type", "string")),
                    "required": param.get("required", location == "path"),
                    "description": param.get("description", ""),
                    "default_value": param.get("default"),
                }
                if param.get("enum"):
                    p["validation_rules"] = {"enum": param["enum"]}
                result.append(p)
        return result

    def _map_type(self, swagger_type: str) -> str:
        """Swagger类型映射"""
        mapping = {
            "string": "String",
            "integer": "Integer",
            "number": "Float",
            "boolean": "Boolean",
            "array": "Array",
            "object": "Object",
            "file": "File",
        }
        return mapping.get(swagger_type, "String")

    def _resolve_schema(self, schema: Dict, definitions: Dict) -> Dict:
        """解析Schema引用"""
        if "$ref" in schema:
            ref_name = schema["$ref"].split("/")[-1]
            if ref_name in definitions:
                return self._resolve_schema(definitions[ref_name], definitions)
            return {"type": "object", "description": f"未解析的引用: {ref_name}"}

        result = {"type": schema.get("type", "object")}
        if schema.get("properties"):
            result["properties"] = {}
            for name, prop in schema["properties"].items():
                result["properties"][name] = self._resolve_schema(prop, definitions)
        if schema.get("items"):
            result["items"] = self._resolve_schema(schema["items"], definitions)
        if schema.get("required"):
            result["required"] = schema["required"]
        return result


class OpenAPI3Parser(ImportParser):
    """OpenAPI 3.0 解析器"""

    def parse(self, content: str) -> List[Dict[str, Any]]:
        try:
            spec = json.loads(content)
        except json.JSONDecodeError:
            try:
                import yaml
                spec = yaml.safe_load(content)
            except Exception:
                raise HTTPException(status_code=400, detail="OpenAPI文件解析失败")

        if "openapi" not in spec:
            raise HTTPException(status_code=400, detail="不是有效的OpenAPI 3.0文件")

        results = []
        components = spec.get("components", {})

        for path, methods in spec.get("paths", {}).items():
            for method, operation in methods.items():
                if method.lower() not in ("get", "post", "put", "patch", "delete", "head", "options"):
                    continue
                api_def = self._convert_operation(path, method.upper(), operation, components)
                results.append(api_def)

        return results

    def _convert_operation(self, path: str, method: str, operation: Dict, components: Dict) -> Dict[str, Any]:
        """转换OpenAPI3操作为内部模型"""
        path_params = self._extract_params(operation.get("parameters", []), "path")
        query_params = self._extract_params(operation.get("parameters", []), "query")
        header_params = self._extract_params(operation.get("parameters", []), "header")
        cookie_params = self._extract_params(operation.get("parameters", []), "cookie")

        body_type = BodyType.NONE
        body_definition = None
        request_body = operation.get("requestBody")
        if request_body:
            content = request_body.get("content", {})
            if "application/json" in content:
                body_type = BodyType.JSON
                body_definition = content["application/json"].get("schema", {})
            elif "multipart/form-data" in content:
                body_type = BodyType.FORM_DATA
                body_definition = content["multipart/form-data"].get("schema", {})
            elif "application/x-www-form-urlencoded" in content:
                body_type = BodyType.X_WWW_FORM_URLENCODED
                body_definition = content["application/x-www-form-urlencoded"].get("schema", {})
            elif "application/xml" in content:
                body_type = BodyType.XML
                body_definition = content["application/xml"].get("schema", {})
            else:
                body_type = BodyType.RAW
                for ct, schema_data in content.items():
                    body_definition = schema_data.get("schema", {})
                    break

        responses = []
        for code, resp in operation.get("responses", {}).items():
            try:
                status_code = int(code)
            except ValueError:
                continue
            resp_def = {
                "status_code": status_code,
                "description": resp.get("description", ""),
            }
            resp_content = resp.get("content", {})
            if "application/json" in resp_content:
                resp_def["body_schema"] = resp_content["application/json"].get("schema", {})
            responses.append(resp_def)

        return {
            "name": operation.get("summary", operation.get("operationId", f"{method} {path}")),
            "method": method,
            "path": path,
            "description": operation.get("description", ""),
            "path_params": path_params,
            "query_params": query_params,
            "header_params": header_params,
            "cookie_params": cookie_params,
            "body_type": body_type.value,
            "body_definition": body_definition,
            "responses": responses,
        }

    def _extract_params(self, parameters: List[Dict], location: str) -> List[Dict]:
        """提取指定位置的参数"""
        result = []
        for param in parameters:
            if param.get("in") == location:
                schema = param.get("schema", {})
                p = {
                    "name": param.get("name", ""),
                    "param_type": self._map_type(schema.get("type", "string")),
                    "required": param.get("required", location == "path"),
                    "description": param.get("description", ""),
                    "default_value": schema.get("default"),
                }
                if schema.get("enum"):
                    p["validation_rules"] = {"enum": schema["enum"]}
                result.append(p)
        return result

    def _map_type(self, oas_type: str) -> str:
        """OpenAPI3类型映射"""
        mapping = {
            "string": "String",
            "integer": "Integer",
            "number": "Float",
            "boolean": "Boolean",
            "array": "Array",
            "object": "Object",
        }
        return mapping.get(oas_type, "String")


class HARParser(ImportParser):
    """HAR 1.2 解析器"""

    def parse(self, content: str) -> List[Dict[str, Any]]:
        try:
            har = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="HAR文件JSON解析失败")

        log = har.get("log", {})
        entries = log.get("entries", [])
        if not entries:
            raise HTTPException(status_code=400, detail="HAR文件中无请求记录")

        results = []
        for entry in entries:
            api_def = self._convert_entry(entry)
            if api_def:
                results.append(api_def)

        return results

    def _convert_entry(self, entry: Dict) -> Optional[Dict[str, Any]]:
        """转换HAR条目为内部模型"""
        request = entry.get("request", {})
        method = request.get("method", "GET").upper()
        url = request.get("url", "")

        if not url:
            return None

        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(url)
        path = parsed.path or "/"

        query_params = []
        for name, values in parse_qs(parsed.query).items():
            for value in values:
                query_params.append({
                    "name": name,
                    "param_type": "String",
                    "required": False,
                    "default_value": value,
                })

        header_params = []
        for header in request.get("headers", []):
            name = header.get("name", "")
            if name.lower() not in ("host", "content-length", "accept", "user-agent", "connection"):
                header_params.append({
                    "name": name,
                    "param_type": "String",
                    "required": False,
                    "default_value": header.get("value", ""),
                })

        body_type = BodyType.NONE
        body_definition = None
        post_data = request.get("postData")
        if post_data:
            mime = post_data.get("mimeType", "")
            if "application/json" in mime:
                body_type = BodyType.JSON
                try:
                    body_definition = json.loads(post_data.get("text", "{}"))
                except json.JSONDecodeError:
                    body_definition = post_data.get("text", "")
            elif "multipart/form-data" in mime:
                body_type = BodyType.FORM_DATA
            elif "application/x-www-form-urlencoded" in mime:
                body_type = BodyType.X_WWW_FORM_URLENCODED
            elif "application/xml" in mime:
                body_type = BodyType.XML
                body_definition = post_data.get("text", "")
            else:
                body_type = BodyType.RAW
                body_definition = post_data.get("text", "")

        return {
            "name": f"{method} {path}",
            "method": method,
            "path": path,
            "description": f"从HAR导入: {url}",
            "path_params": [],
            "query_params": query_params,
            "header_params": header_params,
            "cookie_params": [],
            "body_type": body_type.value,
            "body_definition": body_definition,
            "responses": [],
        }


class ImportEngine:
    """导入引擎"""

    PARSER_MAP = {
        "swagger2": Swagger2Parser,
        "openapi3": OpenAPI3Parser,
        "har": HARParser,
    }

    def __init__(self, db: Session):
        self.db = db

    def fetch_from_url(self, url: str) -> str:
        """从URL获取导入内容"""
        import httpx
        try:
            response = httpx.get(url, timeout=30.0)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as e:
            raise HTTPException(status_code=400, detail=f"从URL获取内容失败: {str(e)}")

    def preview(
        self,
        content: str,
        team_id: int,
        format: Optional[str] = None
    ) -> Dict[str, Any]:
        """预览导入内容，不实际创建接口"""
        fmt = format or self.detect_format(content)
        parser_cls = self.PARSER_MAP.get(fmt)
        if not parser_cls:
            raise HTTPException(status_code=400, detail=f"不支持的格式: {fmt}")

        parser = parser_cls()
        api_defs = parser.parse(content)

        if len(api_defs) > settings.MAX_IMPORT_APIS:
            raise HTTPException(status_code=400, detail=f"单次导入接口数不超过{settings.MAX_IMPORT_APIS}个")

        new_count = 0
        duplicate_count = 0
        failed_count = 0
        preview_items = []

        for api_def in api_defs:
            try:
                is_dup = self._check_duplicate(team_id, api_def["method"], api_def["path"])
                if is_dup:
                    duplicate_count += 1
                    preview_items.append({
                        "method": api_def["method"],
                        "path": api_def["path"],
                        "name": api_def["name"],
                        "status": "duplicate",
                        "error": None,
                        "module_name": None,
                        "selected": True,
                    })
                else:
                    new_count += 1
                    preview_items.append({
                        "method": api_def["method"],
                        "path": api_def["path"],
                        "name": api_def["name"],
                        "status": "new",
                        "error": None,
                        "module_name": None,
                        "selected": True,
                    })
            except Exception as e:
                failed_count += 1
                preview_items.append({
                    "method": api_def.get("method", "GET"),
                    "path": api_def.get("path", "/"),
                    "name": api_def.get("name", "unknown"),
                    "status": "failed",
                    "error": str(e),
                    "module_name": None,
                    "selected": False,
                })

        return {
            "total": len(api_defs),
            "new_count": new_count,
            "duplicate_count": duplicate_count,
            "failed_count": failed_count,
            "apis": preview_items,
        }

    def detect_format(self, content: str) -> str:
        """检测文件格式"""
        try:
            data = json.loads(content)
            if "swagger" in data:
                return "swagger2"
            elif "openapi" in data:
                return "openapi3"
            elif "log" in data and "entries" in data.get("log", {}):
                return "har"
        except json.JSONDecodeError:
            try:
                import yaml
                data = yaml.safe_load(content)
                if isinstance(data, dict):
                    if "swagger" in data:
                        return "swagger2"
                    elif "openapi" in data:
                        return "openapi3"
            except Exception:
                pass

        raise HTTPException(status_code=400, detail="不支持的文件格式，请上传Swagger2/OpenAPI3/HAR文件")

    def import_from_content(
        self,
        content: str,
        team_id: int,
        module_id: Optional[int],
        conflict_strategy: str,
        user_id: int,
        format: Optional[str] = None
    ) -> Dict[str, Any]:
        """从内容导入接口"""
        fmt = format or self.detect_format(content)
        parser_cls = self.PARSER_MAP.get(fmt)
        if not parser_cls:
            raise HTTPException(status_code=400, detail=f"不支持的格式: {fmt}")

        parser = parser_cls()
        api_defs = parser.parse(content)

        if len(api_defs) > settings.MAX_IMPORT_APIS:
            raise HTTPException(status_code=400, detail=f"单次导入接口数不超过{settings.MAX_IMPORT_APIS}个")

        created = 0
        skipped = 0
        failed = 0
        details = []

        for api_def in api_defs:
            try:
                is_dup = self._check_duplicate(team_id, api_def["method"], api_def["path"])
                if is_dup:
                    if conflict_strategy == "skip":
                        skipped += 1
                        details.append({"name": api_def["name"], "status": "skipped", "reason": "重复接口"})
                        continue
                    elif conflict_strategy == "overwrite":
                        self._overwrite_api(team_id, api_def, user_id)
                        created += 1
                        details.append({"name": api_def["name"], "status": "overwritten"})
                        continue
                    elif conflict_strategy == "copy":
                        api_def["name"] = f"{api_def['name']}（副本）"

                self._create_api_from_def(team_id, module_id, api_def, user_id)
                created += 1
                details.append({"name": api_def["name"], "status": "created"})
            except Exception as e:
                failed += 1
                details.append({"name": api_def.get("name", "unknown"), "status": "failed", "reason": str(e)})

        self.db.commit()

        return {
            "total": len(api_defs),
            "created": created,
            "skipped": skipped,
            "failed": failed,
            "details": details,
        }

    def _check_duplicate(self, team_id: int, method: str, path: str) -> bool:
        """检查重复接口"""
        normalized = PathValidator.normalize_path(path)
        existing = self.db.query(ApiDefinition).filter(
            ApiDefinition.team_id == team_id,
            ApiDefinition.method == method,
            ApiDefinition.is_deleted == False
        ).all()
        for api in existing:
            if PathValidator.normalize_path(api.path) == normalized:
                return True
        return False

    def _create_api_from_def(self, team_id: int, module_id: Optional[int], api_def: Dict, user_id: int) -> ApiDefinition:
        """从解析结果创建接口"""
        body_type_val = api_def.get("body_type", "none")
        try:
            body_type_enum = BodyType(body_type_val)
        except ValueError:
            body_type_enum = BodyType.NONE

        api = ApiDefinition(
            team_id=team_id,
            module_id=module_id,
            name=api_def.get("name", ""),
            method=api_def.get("method", "GET"),
            path=api_def.get("path", "/"),
            description=api_def.get("description", ""),
            status=ApiStatus.DRAFT,
            protocol="http",
            path_params=json.dumps(api_def.get("path_params", []), ensure_ascii=False),
            query_params=json.dumps(api_def.get("query_params", []), ensure_ascii=False),
            header_params=json.dumps(api_def.get("header_params", []), ensure_ascii=False),
            cookie_params=json.dumps(api_def.get("cookie_params", []), ensure_ascii=False),
            body_type=body_type_enum,
            body_definition=json.dumps(api_def.get("body_definition"), ensure_ascii=False) if api_def.get("body_definition") else None,
            responses=json.dumps(api_def.get("responses", []), ensure_ascii=False),
            owner_id=user_id,
            created_by=user_id,
            updated_by=user_id,
        )
        self.db.add(api)
        self.db.flush()
        return api

    def _overwrite_api(self, team_id: int, api_def: Dict, user_id: int):
        """覆盖已有接口"""
        normalized = PathValidator.normalize_path(api_def["path"])
        existing = self.db.query(ApiDefinition).filter(
            ApiDefinition.team_id == team_id,
            ApiDefinition.method == api_def["method"],
            ApiDefinition.is_deleted == False
        ).all()
        for api in existing:
            if PathValidator.normalize_path(api.path) == normalized:
                api.name = api_def.get("name", api.name)
                api.description = api_def.get("description", api.description)
                api.path_params = json.dumps(api_def.get("path_params", []), ensure_ascii=False)
                api.query_params = json.dumps(api_def.get("query_params", []), ensure_ascii=False)
                api.header_params = json.dumps(api_def.get("header_params", []), ensure_ascii=False)
                api.cookie_params = json.dumps(api_def.get("cookie_params", []), ensure_ascii=False)
                if api_def.get("body_type"):
                    try:
                        api.body_type = BodyType(api_def["body_type"])
                    except ValueError:
                        pass
                api.body_definition = json.dumps(api_def.get("body_definition"), ensure_ascii=False) if api_def.get("body_definition") else None
                api.responses = json.dumps(api_def.get("responses", []), ensure_ascii=False)
                api.updated_by = user_id
                self.db.flush()
                return
