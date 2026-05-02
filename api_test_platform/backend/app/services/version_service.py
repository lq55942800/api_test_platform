"""
版本控制服务
"""
import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.api import ApiVersion, ApiDefinition, ChangeType
from app.utils.schema_diff import SchemaDiffEngine
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class VersionService:
    def __init__(self, db: Session):
        self.db = db
        self.diff_engine = SchemaDiffEngine()

    def create_version(
        self,
        api_id: int,
        snapshot: Dict[str, Any],
        change_type: ChangeType,
        change_summary: Optional[str],
        user_id: int,
        affected_fields: Optional[str] = None
    ) -> ApiVersion:
        """创建版本记录"""
        logger.info(f"创建版本记录: api_id={api_id}, change_type={change_type.value if hasattr(change_type, 'value') else change_type}, user_id={user_id}")

        latest = self._get_latest_version(api_id)
        version_number = (latest.version_number + 1) if latest else 1

        logger.debug(f"版本号计算: api_id={api_id}, version_number={version_number}, has_previous={latest is not None}")

        version = ApiVersion(
            api_id=api_id,
            version_number=version_number,
            snapshot=json.dumps(snapshot, ensure_ascii=False),
            change_type=change_type,
            change_summary=change_summary,
            affected_fields=affected_fields,
            changed_by=user_id,
        )
        self.db.add(version)
        self.db.flush()

        self._archive_old_versions(api_id)

        self.db.commit()
        self.db.refresh(version)
        logger.info(f"版本记录创建成功: api_id={api_id}, version_number={version_number}")
        return version

    def get_versions(
        self,
        api_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[ApiVersion], int]:
        """获取版本历史"""
        logger.info(f"获取版本历史: api_id={api_id}, page={page}, page_size={page_size}")

        query = self.db.query(ApiVersion).filter(ApiVersion.api_id == api_id)
        total = query.count()
        items = query.order_by(ApiVersion.version_number.desc()) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()

        logger.debug(f"版本历史查询结果: api_id={api_id}, total={total}, returned={len(items)}")
        return items, total

    def get_version(self, api_id: int, version_number: int) -> Optional[ApiVersion]:
        """获取指定版本"""
        logger.debug(f"获取指定版本: api_id={api_id}, version_number={version_number}")

        version = self.db.query(ApiVersion).filter(
            ApiVersion.api_id == api_id,
            ApiVersion.version_number == version_number
        ).first()

        if not version:
            logger.warning(f"版本不存在: api_id={api_id}, version_number={version_number}")

        return version

    def compare_versions(self, api_id: int, v1: int, v2: int) -> Dict[str, Any]:
        """版本对比"""
        logger.info(f"版本对比: api_id={api_id}, v1={v1}, v2={v2}")

        version1 = self.get_version(api_id, v1)
        version2 = self.get_version(api_id, v2)

        if not version1:
            logger.warning(f"版本对比失败，版本v{v1}不存在: api_id={api_id}")
            raise HTTPException(status_code=404, detail=f"版本 v{v1} 不存在")
        if not version2:
            logger.warning(f"版本对比失败，版本v{v2}不存在: api_id={api_id}")
            raise HTTPException(status_code=404, detail=f"版本 v{v2} 不存在")

        snapshot1 = json.loads(version1.snapshot)
        snapshot2 = json.loads(version2.snapshot)

        diff_result = self.diff_engine.compute_diff(snapshot1, snapshot2)
        logger.debug(f"版本对比完成: api_id={api_id}, v1={v1}, v2={v2}, change_count={len(diff_result.get('changes', []))}")
        return diff_result

    def rollback(self, api_id: int, target_version: int, user_id: int) -> ApiDefinition:
        """回滚到指定版本"""
        logger.info(f"回滚版本: api_id={api_id}, target_version={target_version}, user_id={user_id}")

        target = self.get_version(api_id, target_version)
        if not target:
            logger.warning(f"回滚失败，目标版本不存在: api_id={api_id}, target_version={target_version}")
            raise HTTPException(status_code=404, detail=f"版本 v{target_version} 不存在")

        api = self.db.query(ApiDefinition).filter(
            ApiDefinition.id == api_id,
            ApiDefinition.is_deleted == False
        ).first()
        if not api:
            logger.warning(f"回滚失败，接口不存在: api_id={api_id}")
            raise HTTPException(status_code=404, detail="接口不存在")

        snapshot = json.loads(target.snapshot)
        logger.debug(f"回滚快照解析完成: api_id={api_id}, target_version={target_version}")

        api.name = snapshot.get("name", api.name)
        api.method = snapshot.get("method", api.method)
        api.path = snapshot.get("path", api.path)
        api.description = snapshot.get("description", api.description)
        api.protocol = snapshot.get("protocol", api.protocol)
        api.path_params = json.dumps(snapshot.get("path_params", []), ensure_ascii=False) if snapshot.get("path_params") else None
        api.query_params = json.dumps(snapshot.get("query_params", []), ensure_ascii=False) if snapshot.get("query_params") else None
        api.header_params = json.dumps(snapshot.get("header_params", []), ensure_ascii=False) if snapshot.get("header_params") else None
        api.cookie_params = json.dumps(snapshot.get("cookie_params", []), ensure_ascii=False) if snapshot.get("cookie_params") else None
        api.body_type = snapshot.get("body_type", api.body_type)
        api.body_definition = json.dumps(snapshot.get("body_definition"), ensure_ascii=False) if snapshot.get("body_definition") else None
        api.responses = json.dumps(snapshot.get("responses", []), ensure_ascii=False) if snapshot.get("responses") else None
        api.updated_by = user_id

        self.db.flush()

        self.create_version(
            api_id=api_id,
            snapshot=snapshot,
            change_type=ChangeType.ROLLBACK,
            change_summary=f"回滚到版本v{target_version}",
            user_id=user_id,
        )

        self.db.refresh(api)
        logger.info(f"版本回滚成功: api_id={api_id}, target_version={target_version}")
        return api

    def should_create_version(self, api: ApiDefinition, new_snapshot: Dict[str, Any]) -> bool:
        """判断是否需要创建新版本"""
        logger.debug(f"判断是否需要创建新版本: api_id={api.id}")

        latest = self._get_latest_version(api.id)
        if not latest:
            logger.debug(f"无历史版本，需要创建新版本: api_id={api.id}")
            return True

        old_snapshot = json.loads(latest.snapshot)
        diff_result = self.diff_engine.compute_diff(old_snapshot, new_snapshot)
        has_changes = len(diff_result.get("changes", [])) > 0
        logger.debug(f"版本差异比较: api_id={api.id}, has_changes={has_changes}, change_count={len(diff_result.get('changes', []))}")
        return has_changes

    def _get_latest_version(self, api_id: int) -> Optional[ApiVersion]:
        """获取最新版本"""
        version = self.db.query(ApiVersion).filter(
            ApiVersion.api_id == api_id
        ).order_by(ApiVersion.version_number.desc()).first()
        if version:
            logger.debug(f"获取最新版本: api_id={api_id}, latest_version={version.version_number}")
        else:
            logger.debug(f"无历史版本: api_id={api_id}")
        return version

    def _archive_old_versions(self, api_id: int):
        """归档超出保留数量的版本"""
        count = self.db.query(ApiVersion).filter(ApiVersion.api_id == api_id).count()
        if count > settings.MAX_VERSIONS_PER_API:
            old_versions = self.db.query(ApiVersion).filter(
                ApiVersion.api_id == api_id
            ).order_by(ApiVersion.version_number.asc()).limit(
                count - settings.MAX_VERSIONS_PER_API
            ).all()
            archived_count = len(old_versions)
            for v in old_versions:
                self.db.delete(v)
            logger.info(f"归档旧版本: api_id={api_id}, archived_count={archived_count}, remaining={count - archived_count}, max={settings.MAX_VERSIONS_PER_API}")
        else:
            logger.debug(f"版本数量未超限，无需归档: api_id={api_id}, count={count}, max={settings.MAX_VERSIONS_PER_API}")
