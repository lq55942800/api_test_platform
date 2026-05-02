"""
接口管理服务
"""
import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException
from datetime import datetime

from app.models.api import (
    ApiDefinition, ApiModule, ApiTag, ApiTagRelation,
    ApiStatus, BodyType
)
from app.schemas.api import (
    ApiDefinitionCreate, ApiDefinitionUpdate, UpdateStatusRequest,
    HttpMethod
)
from app.utils.path_validator import PathValidator
from app.utils.param_validator import ParamValidator
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ApiService:
    def __init__(self, db: Session):
        self.db = db

    def create_api(self, data: ApiDefinitionCreate, user_id: int) -> ApiDefinition:
        """创建接口"""
        logger.info(f"创建接口: name={data.name}, method={data.method.value}, path={data.path}, team_id={data.team_id}, user_id={user_id}")

        path = PathValidator.normalize_path(data.path)
        valid, err = PathValidator.validate(path)
        if not valid:
            logger.warning(f"接口路径格式错误: path={data.path}, error={err}")
            raise HTTPException(status_code=400, detail=f"路径格式错误: {err}")

        valid, err = ParamValidator.validate_body_type_method_match(data.method.value, data.body_type.value)
        if not valid:
            logger.warning(f"请求体类型与HTTP方法不匹配: method={data.method.value}, body_type={data.body_type.value}, error={err}")
            raise HTTPException(status_code=400, detail=err)

        if data.query_params:
            params_dict = [p.model_dump() for p in data.query_params]
            valid, err = ParamValidator.validate_params_list(params_dict)
            if not valid:
                logger.warning(f"查询参数校验失败: error={err}")
                raise HTTPException(status_code=400, detail=err)

        api = ApiDefinition(
            team_id=data.team_id,
            module_id=data.module_id,
            name=data.name,
            method=data.method.value,
            path=path,
            description=data.description,
            status=ApiStatus.DRAFT,
            protocol=data.protocol,
            path_params=json.dumps([p.model_dump() for p in data.path_params], ensure_ascii=False) if data.path_params else None,
            query_params=json.dumps([p.model_dump() for p in data.query_params], ensure_ascii=False) if data.query_params else None,
            header_params=json.dumps([p.model_dump() for p in data.header_params], ensure_ascii=False) if data.header_params else None,
            cookie_params=json.dumps([p.model_dump() for p in data.cookie_params], ensure_ascii=False) if data.cookie_params else None,
            body_type=data.body_type,
            body_definition=json.dumps(data.body_definition, ensure_ascii=False) if data.body_definition else None,
            responses=json.dumps([r.model_dump() for r in data.responses], ensure_ascii=False) if data.responses else None,
            pre_request_actions=json.dumps([a.model_dump() for a in data.pre_request_actions], ensure_ascii=False) if data.pre_request_actions else None,
            post_request_actions=json.dumps([a.model_dump() for a in data.post_request_actions], ensure_ascii=False) if data.post_request_actions else None,
            assertions=json.dumps([a.model_dump() for a in data.assertions], ensure_ascii=False) if data.assertions else None,
            connect_timeout=data.connect_timeout or 5000,
            read_timeout=data.read_timeout or 30000,
            write_timeout=data.write_timeout or 10000,
            pool_timeout=data.pool_timeout or 5000,
            sample_timeout=data.sample_timeout or 60000,
            sql_timeout=data.sql_timeout or 30000,
            script_timeout=data.script_timeout or 10000,
            timeout_enabled=data.timeout_enabled if data.timeout_enabled is not None else True,
            owner_id=data.owner_id or user_id,
            created_by=user_id,
            updated_by=user_id,
        )
        self.db.add(api)
        self.db.flush()

        if data.tag_ids:
            self._set_tags(api.id, data.tag_ids)
            logger.debug(f"设置接口标签: api_id={api.id}, tag_ids={data.tag_ids}")

        self.db.commit()
        self.db.refresh(api)
        logger.info(f"接口创建成功: api_id={api.id}, name={api.name}")
        return api

    def get_api(self, api_id: int) -> Optional[ApiDefinition]:
        """获取接口详情"""
        logger.debug(f"获取接口详情: api_id={api_id}")
        api = self.db.query(ApiDefinition).filter(
            ApiDefinition.id == api_id,
            ApiDefinition.is_deleted == False
        ).first()
        if not api:
            logger.warning(f"接口不存在或已删除: api_id={api_id}")
        return api

    def get_api_list(
        self,
        team_id: int,
        module_id: Optional[int] = None,
        method: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        tag_id: Optional[int] = None,
        owner_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[ApiDefinition], int]:
        """获取接口列表"""
        logger.info(f"获取接口列表: team_id={team_id}, module_id={module_id}, method={method}, status={status}, keyword={keyword}, tag_id={tag_id}, owner_id={owner_id}, page={page}, page_size={page_size}")

        query = self.db.query(ApiDefinition).filter(
            ApiDefinition.team_id == team_id,
            ApiDefinition.is_deleted == False
        )

        if module_id is not None:
            if module_id == 0:
                query = query.filter(ApiDefinition.module_id == None)
            else:
                query = query.filter(ApiDefinition.module_id == module_id)
        if method:
            query = query.filter(ApiDefinition.method == method)
        if status:
            query = query.filter(ApiDefinition.status == status)
        if keyword:
            query = query.filter(
                or_(
                    ApiDefinition.name.ilike(f"%{keyword}%"),
                    ApiDefinition.path.ilike(f"%{keyword}%")
                )
            )
        if owner_id:
            query = query.filter(ApiDefinition.owner_id == owner_id)
        if tag_id:
            query = query.join(ApiTagRelation, ApiDefinition.id == ApiTagRelation.api_id).filter(
                ApiTagRelation.tag_id == tag_id
            )

        total = query.count()
        items = query.order_by(ApiDefinition.updated_at.desc()) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()

        logger.debug(f"接口列表查询结果: total={total}, returned={len(items)}")
        return items, total

    def update_api(self, api_id: int, data: ApiDefinitionUpdate, user_id: int) -> ApiDefinition:
        """更新接口"""
        logger.info(f"更新接口: api_id={api_id}, user_id={user_id}")

        api = self.get_api(api_id)
        if not api:
            logger.warning(f"更新接口失败，接口不存在: api_id={api_id}")
            raise HTTPException(status_code=404, detail="接口不存在")

        update_data = data.model_dump(exclude_unset=True)

        if "path" in update_data:
            path = PathValidator.normalize_path(update_data["path"])
            valid, err = PathValidator.validate(path)
            if not valid:
                logger.warning(f"更新接口路径格式错误: api_id={api_id}, path={update_data['path']}, error={err}")
                raise HTTPException(status_code=400, detail=f"路径格式错误: {err}")
            update_data["path"] = path

        method = update_data.get("method", api.method)
        body_type = update_data.get("body_type", api.body_type)
        method_val = method.value if isinstance(method, HttpMethod) else method
        body_val = body_type.value if isinstance(body_type, BodyType) else body_type
        valid, err = ParamValidator.validate_body_type_method_match(method_val, body_val)
        if not valid:
            logger.warning(f"更新接口请求体类型与HTTP方法不匹配: api_id={api_id}, method={method_val}, body_type={body_val}, error={err}")
            raise HTTPException(status_code=400, detail=err)

        if "method" in update_data or "path" in update_data:
            pass

        tag_ids = update_data.pop("tag_ids", None)

        json_fields = {
            "path_params": update_data.pop("path_params", None),
            "query_params": update_data.pop("query_params", None),
            "header_params": update_data.pop("header_params", None),
            "cookie_params": update_data.pop("cookie_params", None),
            "body_definition": update_data.pop("body_definition", None),
            "responses": update_data.pop("responses", None),
            "pre_request_actions": update_data.pop("pre_request_actions", None),
            "post_request_actions": update_data.pop("post_request_actions", None),
            "assertions": update_data.pop("assertions", None),
        }

        for key, value in update_data.items():
            if hasattr(api, key):
                setattr(api, key, value)

        for field, value in json_fields.items():
            if value is not None:
                if isinstance(value, list) and value and hasattr(value[0], 'model_dump'):
                    setattr(api, field, json.dumps([v.model_dump() for v in value], ensure_ascii=False))
                elif isinstance(value, (dict, list)):
                    setattr(api, field, json.dumps(value, ensure_ascii=False))
                else:
                    setattr(api, field, value)

        logger.debug(f"更新接口字段: api_id={api_id}, fields={list(update_data.keys()) + list(json_fields.keys())}")

        api.updated_by = user_id
        api.updated_at = datetime.utcnow()

        if tag_ids is not None:
            self._set_tags(api.id, tag_ids)
            logger.debug(f"更新接口标签: api_id={api_id}, tag_ids={tag_ids}")

        self.db.commit()
        self.db.refresh(api)
        logger.info(f"接口更新成功: api_id={api_id}")
        return api

    def delete_api(self, api_id: int, user_id: int) -> bool:
        """软删除接口"""
        logger.info(f"软删除接口: api_id={api_id}, user_id={user_id}")

        api = self.get_api(api_id)
        if not api:
            logger.warning(f"删除接口失败，接口不存在: api_id={api_id}")
            raise HTTPException(status_code=404, detail="接口不存在")

        api.is_deleted = True
        api.deleted_at = datetime.utcnow()
        api.deleted_by = user_id
        self.db.commit()
        logger.info(f"接口软删除成功: api_id={api_id}")
        return True

    def copy_api(self, api_id: int, user_id: int) -> ApiDefinition:
        """复制接口"""
        logger.info(f"复制接口: api_id={api_id}, user_id={user_id}")

        api = self.get_api(api_id)
        if not api:
            logger.warning(f"复制接口失败，源接口不存在: api_id={api_id}")
            raise HTTPException(status_code=404, detail="接口不存在")

        new_api = ApiDefinition(
            team_id=api.team_id,
            module_id=api.module_id,
            name=f"{api.name}（副本）",
            method=api.method,
            path=api.path,
            description=api.description,
            status=ApiStatus.DRAFT,
            protocol=api.protocol,
            path_params=api.path_params,
            query_params=api.query_params,
            header_params=api.header_params,
            cookie_params=api.cookie_params,
            body_type=api.body_type,
            body_definition=api.body_definition,
            responses=api.responses,
            pre_request_actions=api.pre_request_actions,
            post_request_actions=api.post_request_actions,
            assertions=api.assertions,
            connect_timeout=api.connect_timeout,
            read_timeout=api.read_timeout,
            write_timeout=api.write_timeout,
            pool_timeout=api.pool_timeout,
            sample_timeout=api.sample_timeout,
            sql_timeout=api.sql_timeout,
            script_timeout=api.script_timeout,
            timeout_enabled=api.timeout_enabled,
            owner_id=user_id,
            created_by=user_id,
            updated_by=user_id,
        )
        self.db.add(new_api)
        self.db.flush()

        tag_relations = self.db.query(ApiTagRelation).filter(ApiTagRelation.api_id == api_id).all()
        logger.debug(f"复制接口标签关联: source_api_id={api_id}, tag_count={len(tag_relations)}")
        for rel in tag_relations:
            new_rel = ApiTagRelation(api_id=new_api.id, tag_id=rel.tag_id)
            self.db.add(new_rel)

        self.db.commit()
        self.db.refresh(new_api)
        logger.info(f"接口复制成功: source_api_id={api_id}, new_api_id={new_api.id}")
        return new_api

    def update_status(self, api_id: int, data: UpdateStatusRequest, user_id: int) -> ApiDefinition:
        """修改接口状态"""
        logger.info(f"修改接口状态: api_id={api_id}, target_status={data.status}, user_id={user_id}")

        api = self.get_api(api_id)
        if not api:
            logger.warning(f"修改接口状态失败，接口不存在: api_id={api_id}")
            raise HTTPException(status_code=404, detail="接口不存在")

        valid, err = self._validate_status_transition(api.status, data.status)
        if not valid:
            logger.warning(f"接口状态流转不合法: api_id={api_id}, current={api.status.value}, target={data.status.value}, error={err}")
            raise HTTPException(status_code=400, detail=err)

        api.status = data.status
        api.updated_by = user_id
        api.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(api)
        logger.info(f"接口状态修改成功: api_id={api_id}, new_status={api.status.value}")
        return api

    def batch_delete(self, api_ids: List[int], user_id: int) -> Dict[str, Any]:
        """批量删除"""
        logger.info(f"批量删除接口: api_ids={api_ids}, user_id={user_id}")

        success_count = 0
        failed_count = 0
        details = []

        for api_id in api_ids:
            api = self.db.query(ApiDefinition).filter(
                ApiDefinition.id == api_id,
                ApiDefinition.is_deleted == False
            ).first()
            if api:
                api.is_deleted = True
                api.deleted_at = datetime.utcnow()
                api.deleted_by = user_id
                success_count += 1
            else:
                failed_count += 1
                details.append({"api_id": api_id, "reason": "接口不存在"})
                logger.warning(f"批量删除时接口不存在: api_id={api_id}")

        self.db.commit()
        logger.info(f"批量删除接口完成: success_count={success_count}, failed_count={failed_count}")
        return {"success_count": success_count, "failed_count": failed_count, "details": details}

    def batch_move(self, api_ids: List[int], target_module_id: Optional[int], user_id: int) -> Dict[str, Any]:
        """批量移动"""
        logger.info(f"批量移动接口: api_ids={api_ids}, target_module_id={target_module_id}, user_id={user_id}")

        success_count = 0
        failed_count = 0
        details = []

        for api_id in api_ids:
            api = self.db.query(ApiDefinition).filter(
                ApiDefinition.id == api_id,
                ApiDefinition.is_deleted == False
            ).first()
            if api:
                api.module_id = target_module_id
                api.updated_by = user_id
                api.updated_at = datetime.utcnow()
                success_count += 1
            else:
                failed_count += 1
                details.append({"api_id": api_id, "reason": "接口不存在"})
                logger.warning(f"批量移动时接口不存在: api_id={api_id}")

        self.db.commit()
        logger.info(f"批量移动接口完成: success_count={success_count}, failed_count={failed_count}")
        return {"success_count": success_count, "failed_count": failed_count, "details": details}

    def batch_status(self, api_ids: List[int], status: ApiStatus, user_id: int) -> Dict[str, Any]:
        """批量修改状态"""
        logger.info(f"批量修改接口状态: api_ids={api_ids}, target_status={status.value}, user_id={user_id}")

        success_count = 0
        failed_count = 0
        details = []

        for api_id in api_ids:
            api = self.db.query(ApiDefinition).filter(
                ApiDefinition.id == api_id,
                ApiDefinition.is_deleted == False
            ).first()
            if api:
                valid, _ = self._validate_status_transition(api.status, status)
                if valid:
                    api.status = status
                    api.updated_by = user_id
                    api.updated_at = datetime.utcnow()
                    success_count += 1
                else:
                    failed_count += 1
                    details.append({"api_id": api_id, "reason": f"不允许从 {api.status.value} 转为 {status.value}"})
                    logger.warning(f"批量修改状态时状态流转不合法: api_id={api_id}, current={api.status.value}, target={status.value}")
            else:
                failed_count += 1
                details.append({"api_id": api_id, "reason": "接口不存在"})
                logger.warning(f"批量修改状态时接口不存在: api_id={api_id}")

        self.db.commit()
        logger.info(f"批量修改接口状态完成: success_count={success_count}, failed_count={failed_count}")
        return {"success_count": success_count, "failed_count": failed_count, "details": details}

    def get_api_tags(self, api_id: int) -> List[Dict[str, Any]]:
        """获取接口的标签列表"""
        logger.debug(f"获取接口标签: api_id={api_id}")

        relations = self.db.query(ApiTagRelation).filter(ApiTagRelation.api_id == api_id).all()
        tags = []
        for rel in relations:
            tag = self.db.query(ApiTag).filter(ApiTag.id == rel.tag_id).first()
            if tag:
                tags.append({"id": tag.id, "name": tag.name, "color": tag.color, "tag_group": tag.tag_group})

        if not tags and relations:
            logger.warning(f"接口标签关联存在但标签数据缺失: api_id={api_id}, relation_count={len(relations)}")

        logger.debug(f"获取接口标签结果: api_id={api_id}, tag_count={len(tags)}")
        return tags

    def get_api_snapshot(self, api: ApiDefinition) -> Dict[str, Any]:
        """获取接口快照(用于版本记录)"""
        logger.debug(f"获取接口快照: api_id={api.id}, name={api.name}")

        snapshot = {
            "name": api.name,
            "method": api.method,
            "path": api.path,
            "description": api.description,
            "status": api.status.value if api.status else None,
            "protocol": api.protocol,
            "path_params": json.loads(api.path_params) if api.path_params else [],
            "query_params": json.loads(api.query_params) if api.query_params else [],
            "header_params": json.loads(api.header_params) if api.header_params else [],
            "cookie_params": json.loads(api.cookie_params) if api.cookie_params else [],
            "body_type": api.body_type.value if api.body_type else None,
            "body_definition": json.loads(api.body_definition) if api.body_definition else None,
            "responses": json.loads(api.responses) if api.responses else [],
            "pre_request_actions": json.loads(api.pre_request_actions) if api.pre_request_actions else [],
            "post_request_actions": json.loads(api.post_request_actions) if api.post_request_actions else [],
            "assertions": json.loads(api.assertions) if api.assertions else [],
            "connect_timeout": api.connect_timeout,
            "read_timeout": api.read_timeout,
            "write_timeout": api.write_timeout,
            "pool_timeout": api.pool_timeout,
            "sample_timeout": api.sample_timeout,
            "sql_timeout": api.sql_timeout,
            "script_timeout": api.script_timeout,
            "timeout_enabled": api.timeout_enabled,
        }
        return snapshot

    def _check_uniqueness(self, team_id: int, method: str, path: str, exclude_id: Optional[int] = None):
        """唯一性校验"""
        logger.debug(f"唯一性校验: team_id={team_id}, method={method}, path={path}, exclude_id={exclude_id}")

        normalized = PathValidator.normalize_path(path)
        query = self.db.query(ApiDefinition).filter(
            ApiDefinition.team_id == team_id,
            ApiDefinition.method == method,
            ApiDefinition.is_deleted == False
        )
        existing = query.all()
        for api in existing:
            if PathValidator.normalize_path(api.path) == normalized:
                if exclude_id and api.id == exclude_id:
                    continue
                logger.warning(f"接口唯一性校验失败: team_id={team_id}, method={method}, path={path}")
                raise HTTPException(status_code=400, detail=f"已存在相同的接口: {method} {path}")

    def _set_tags(self, api_id: int, tag_ids: List[int]):
        """设置接口标签"""
        logger.debug(f"设置接口标签: api_id={api_id}, tag_ids={tag_ids}")

        self.db.query(ApiTagRelation).filter(ApiTagRelation.api_id == api_id).delete()
        for tag_id in tag_ids:
            tag = self.db.query(ApiTag).filter(ApiTag.id == tag_id).first()
            if tag:
                self.db.add(ApiTagRelation(api_id=api_id, tag_id=tag_id))
            else:
                logger.warning(f"设置接口标签时标签不存在: tag_id={tag_id}")

    def _validate_status_transition(self, current: ApiStatus, target: ApiStatus) -> tuple[bool, Optional[str]]:
        """状态流转校验"""
        transitions = {
            ApiStatus.DRAFT: [ApiStatus.ENABLED],
            ApiStatus.ENABLED: [ApiStatus.DISABLED, ApiStatus.DEPRECATED],
            ApiStatus.DISABLED: [ApiStatus.ENABLED, ApiStatus.DEPRECATED],
            ApiStatus.DEPRECATED: [],
        }
        allowed = transitions.get(current, [])
        if target not in allowed:
            return False, f"不允许从 '{current.value}' 转为 '{target.value}'"
        return True, None
