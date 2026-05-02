"""
接口导出引擎
"""
import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.api import ApiDefinition, ApiModule, ApiStatus
from app.schemas.api import ExportFormat


class ExportEngine:
    """接口导出引擎"""

    def __init__(self, db: Session):
        self.db = db

    def export(
        self,
        team_id: int,
        format: ExportFormat,
        module_id: Optional[int] = None,
        api_ids: Optional[List[int]] = None,
        include_draft: bool = False,
        include_deprecated: bool = False,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """导出接口"""
        apis = self._get_apis(team_id, module_id, api_ids, include_draft, include_deprecated)

        if not apis:
            raise HTTPException(status_code=400, detail="无可导出的接口")

        if format == ExportFormat.OPENAPI3:
            return self._export_openapi3(apis, team_id, title, description)
        elif format == ExportFormat.SWAGGER2:
            return self._export_swagger2(apis, team_id, title, description)
        elif format == ExportFormat.POSTMAN:
            return self._export_postman(apis, team_id, title, description)
        else:
            raise HTTPException(status_code=400, detail=f"不支持的导出格式: {format}")

    def _get_apis(
        self,
        team_id: int,
        module_id: Optional[int],
        api_ids: Optional[List[int]],
        include_draft: bool,
        include_deprecated: bool
    ) -> List[ApiDefinition]:
        """获取要导出的接口列表"""
        query = self.db.query(ApiDefinition).filter(
            ApiDefinition.team_id == team_id,
            ApiDefinition.is_deleted == False
        )

        allowed_statuses = [ApiStatus.ENABLED, ApiStatus.DISABLED]
        if include_draft:
            allowed_statuses.append(ApiStatus.DRAFT)
        if include_deprecated:
            allowed_statuses.append(ApiStatus.DEPRECATED)
        query = query.filter(ApiDefinition.status.in_(allowed_statuses))

        if module_id:
            query = query.filter(ApiDefinition.module_id == module_id)
        if api_ids:
            query = query.filter(ApiDefinition.id.in_(api_ids))

        return query.order_by(ApiDefinition.path, ApiDefinition.method).all()

    def _export_openapi3(self, apis: List[ApiDefinition], team_id: int, title: Optional[str], description: Optional[str]) -> Dict[str, Any]:
        """导出OpenAPI 3.0格式"""
        doc = {
            "openapi": "3.0.3",
            "info": {
                "title": title or "API Documentation",
                "description": description or "",
                "version": "1.0.0",
            },
            "paths": {},
            "components": {"schemas": {}},
        }

        for api in apis:
            path = api.path
            if path not in doc["paths"]:
                doc["paths"][path] = {}

            method = api.method.lower()
            operation = {
                "summary": api.name,
                "description": api.description or "",
                "operationId": f"api_{api.id}",
                "parameters": [],
                "responses": {},
            }

            for param_list, location in [
                (api.path_params, "path"),
                (api.query_params, "query"),
                (api.header_params, "header"),
                (api.cookie_params, "cookie"),
            ]:
                if param_list:
                    params = json.loads(param_list) if isinstance(param_list, str) else param_list
                    for p in params:
                        param_obj = {
                            "name": p.get("name", ""),
                            "in": location,
                            "required": p.get("required", location == "path"),
                            "description": p.get("description", ""),
                            "schema": self._param_to_schema(p),
                        }
                        operation["parameters"].append(param_obj)

            if api.body_type and api.body_type.value != "none" and api.body_definition:
                body_def = json.loads(api.body_definition) if isinstance(api.body_definition, str) else api.body_definition
                content_type = self._get_content_type(api.body_type.value)
                operation["requestBody"] = {
                    "content": {
                        content_type: {
                            "schema": body_def if isinstance(body_def, dict) else {"type": "object"}
                        }
                    }
                }

            if api.responses:
                responses = json.loads(api.responses) if isinstance(api.responses, str) else api.responses
                for resp in responses:
                    code = str(resp.get("status_code", 200))
                    resp_obj = {"description": resp.get("description", "")}
                    if resp.get("body_schema"):
                        resp_obj["content"] = {
                            "application/json": {
                                "schema": resp["body_schema"]
                            }
                        }
                    operation["responses"][code] = resp_obj
            else:
                operation["responses"]["200"] = {"description": "成功"}

            doc["paths"][path][method] = operation

        return doc

    def _export_swagger2(self, apis: List[ApiDefinition], team_id: int, title: Optional[str], description: Optional[str]) -> Dict[str, Any]:
        """导出Swagger 2.0格式"""
        doc = {
            "swagger": "2.0",
            "info": {
                "title": title or "API Documentation",
                "description": description or "",
                "version": "1.0.0",
            },
            "paths": {},
            "definitions": {},
        }

        for api in apis:
            path = api.path
            if path not in doc["paths"]:
                doc["paths"][path] = {}

            method = api.method.lower()
            operation = {
                "summary": api.name,
                "description": api.description or "",
                "operationId": f"api_{api.id}",
                "parameters": [],
                "responses": {},
            }

            for param_list, location in [
                (api.path_params, "path"),
                (api.query_params, "query"),
                (api.header_params, "header"),
                (api.cookie_params, "cookie"),
            ]:
                if param_list:
                    params = json.loads(param_list) if isinstance(param_list, str) else param_list
                    for p in params:
                        param_obj = {
                            "name": p.get("name", ""),
                            "in": location,
                            "required": p.get("required", location == "path"),
                            "description": p.get("description", ""),
                            "type": self._param_to_swagger_type(p),
                        }
                        operation["parameters"].append(param_obj)

            if api.body_type and api.body_type.value in ("json",) and api.body_definition:
                body_def = json.loads(api.body_definition) if isinstance(api.body_definition, str) else api.body_definition
                operation["parameters"].append({
                    "name": "body",
                    "in": "body",
                    "schema": body_def if isinstance(body_def, dict) else {"type": "object"},
                })

            if api.responses:
                responses = json.loads(api.responses) if isinstance(api.responses, str) else api.responses
                for resp in responses:
                    code = str(resp.get("status_code", 200))
                    resp_obj = {"description": resp.get("description", "")}
                    if resp.get("body_schema"):
                        resp_obj["schema"] = resp["body_schema"]
                    operation["responses"][code] = resp_obj
            else:
                operation["responses"]["200"] = {"description": "成功"}

            doc["paths"][path][method] = operation

        return doc

    def _export_postman(self, apis: List[ApiDefinition], team_id: int, title: Optional[str], description: Optional[str]) -> Dict[str, Any]:
        """导出Postman Collection v2.1格式"""
        collection = {
            "info": {
                "name": title or "API Collection",
                "description": description or "",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            },
            "item": [],
        }

        module_groups: Dict[Optional[int], List[Dict]] = {}
        for api in apis:
            item = self._api_to_postman_item(api)
            module_id = api.module_id
            if module_id not in module_groups:
                module_groups[module_id] = []
            module_groups[module_id].append(item)

        for module_id, items in module_groups.items():
            if module_id:
                module = self.db.query(ApiModule).filter(ApiModule.id == module_id).first()
                folder_name = module.name if module else "未分类"
            else:
                folder_name = "未分类"
            collection["item"].append({
                "name": folder_name,
                "item": items,
            })

        return collection

    def _api_to_postman_item(self, api: ApiDefinition) -> Dict[str, Any]:
        """转换接口为Postman Item"""
        query_params = []
        if api.query_params:
            params = json.loads(api.query_params) if isinstance(api.query_params, str) else api.query_params
            for p in params:
                query_params.append({
                    "key": p.get("name", ""),
                    "value": p.get("default_value", p.get("example", "")),
                    "description": p.get("description", ""),
                })

        headers = []
        if api.header_params:
            params = json.loads(api.header_params) if isinstance(api.header_params, str) else api.header_params
            for p in params:
                headers.append({
                    "key": p.get("name", ""),
                    "value": p.get("default_value", p.get("example", "")),
                    "description": p.get("description", ""),
                })

        body = None
        if api.body_type and api.body_type.value != "none" and api.body_definition:
            body_def = json.loads(api.body_definition) if isinstance(api.body_definition, str) else api.body_definition
            body_mode = "raw"
            if api.body_type.value == "json":
                body_mode = "raw"
            elif api.body_type.value == "form-data":
                body_mode = "formdata"
            elif api.body_type.value == "x-www-form-urlencoded":
                body_mode = "urlencoded"

            body = {
                "mode": body_mode,
                "raw": json.dumps(body_def, ensure_ascii=False, indent=2) if isinstance(body_def, (dict, list)) else str(body_def),
            }

        item = {
            "name": api.name,
            "request": {
                "method": api.method,
                "header": headers,
                "url": {
                    "raw": api.path,
                    "path": api.path.strip("/").split("/"),
                    "query": query_params,
                },
            },
        }

        if body:
            item["request"]["body"] = body

        return item

    def _param_to_schema(self, param: Dict) -> Dict:
        """参数转OpenAPI3 Schema"""
        type_mapping = {
            "String": "string",
            "Integer": "integer",
            "Float": "number",
            "Boolean": "boolean",
            "Array": "array",
            "Object": "object",
            "File": "string",
        }
        param_type = param.get("param_type", "String")
        schema_type = type_mapping.get(param_type, "string")

        schema = {"type": schema_type}
        if param.get("default_value"):
            schema["default"] = param["default_value"]
        if param.get("example"):
            schema["example"] = param["example"]
        return schema

    def _param_to_swagger_type(self, param: Dict) -> str:
        """参数转Swagger2类型"""
        type_mapping = {
            "String": "string",
            "Integer": "integer",
            "Float": "number",
            "Boolean": "boolean",
            "Array": "array",
            "Object": "object",
            "File": "file",
        }
        return type_mapping.get(param.get("param_type", "String"), "string")

    def _get_content_type(self, body_type: str) -> str:
        """获取Content-Type"""
        content_types = {
            "json": "application/json",
            "form-data": "multipart/form-data",
            "x-www-form-urlencoded": "application/x-www-form-urlencoded",
            "raw": "text/plain",
            "xml": "application/xml",
            "binary": "application/octet-stream",
        }
        return content_types.get(body_type, "application/json")
