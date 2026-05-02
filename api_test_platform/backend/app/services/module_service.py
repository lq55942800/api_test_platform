"""
模块管理服务
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

from app.models.api import ApiModule, ApiDefinition
from app.schemas.api import ApiModuleCreate, ApiModuleUpdate
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ModuleService:
    def __init__(self, db: Session):
        self.db = db

    def create_module(self, data: ApiModuleCreate, user_id: int) -> ApiModule:
        """创建模块"""
        logger.info(f"创建模块: name={data.name}, team_id={data.team_id}, parent_id={data.parent_id}, user_id={user_id}")

        existing = self.db.query(ApiModule).filter(
            ApiModule.team_id == data.team_id,
            ApiModule.parent_id == data.parent_id if data.parent_id else None,
            ApiModule.name == data.name
        ).first()
        if existing:
            logger.warning(f"创建模块失败，同层级下已存在同名模块: name={data.name}, team_id={data.team_id}")
            raise HTTPException(status_code=400, detail=f"同层级下已存在同名模块: {data.name}")

        if data.parent_id:
            depth = self._get_depth(data.parent_id)
            if depth >= settings.MAX_MODULE_DEPTH:
                logger.warning(f"创建模块失败，层级超限: parent_id={data.parent_id}, depth={depth}, max={settings.MAX_MODULE_DEPTH}")
                raise HTTPException(status_code=400, detail=f"模块层级不能超过{settings.MAX_MODULE_DEPTH}层")

        team_module_count = self.db.query(ApiModule).filter(ApiModule.team_id == data.team_id).count()
        if team_module_count >= settings.MAX_MODULES_PER_TEAM:
            logger.warning(f"创建模块失败，团队模块数超限: team_id={data.team_id}, count={team_module_count}, max={settings.MAX_MODULES_PER_TEAM}")
            raise HTTPException(status_code=400, detail=f"团队模块数不能超过{settings.MAX_MODULES_PER_TEAM}个")

        module = ApiModule(
            team_id=data.team_id,
            parent_id=data.parent_id,
            name=data.name,
            description=data.description,
            sort_order=data.sort_order,
            created_by=user_id,
        )
        self.db.add(module)
        self.db.commit()
        self.db.refresh(module)
        logger.info(f"模块创建成功: module_id={module.id}, name={module.name}, team_id={data.team_id}")
        return module

    def get_module(self, module_id: int) -> Optional[ApiModule]:
        """获取模块"""
        logger.debug(f"获取模块: module_id={module_id}")
        module = self.db.query(ApiModule).filter(ApiModule.id == module_id).first()
        if not module:
            logger.warning(f"模块不存在: module_id={module_id}")
        return module

    def get_module_tree(self, team_id: int) -> List[Dict[str, Any]]:
        """获取模块树"""
        logger.info(f"获取模块树: team_id={team_id}")

        modules = self.db.query(ApiModule).filter(ApiModule.team_id == team_id).order_by(
            ApiModule.sort_order, ApiModule.id
        ).all()

        module_api_counts = {}
        total_api_count = 0
        api_count_rows = self.db.query(
            ApiDefinition.module_id,
        ).filter(
            ApiDefinition.team_id == team_id,
            ApiDefinition.is_deleted == False
        ).all()
        for row in api_count_rows:
            total_api_count += 1
            mid = row.module_id
            if mid is not None:
                module_api_counts[mid] = module_api_counts.get(mid, 0) + 1

        logger.debug(f"模块接口统计: team_id={team_id}, total_api_count={total_api_count}, module_count_with_api={len(module_api_counts)}")

        module_map = {}
        for m in modules:
            module_map[m.id] = {
                "id": m.id,
                "team_id": m.team_id,
                "parent_id": m.parent_id,
                "name": m.name,
                "description": m.description,
                "sort_order": m.sort_order,
                "created_by": m.created_by,
                "created_at": m.created_at,
                "updated_at": m.updated_at,
                "children": [],
                "api_count": module_api_counts.get(m.id, 0),
                "total_api_count": total_api_count,
            }

        roots = []
        for m in modules:
            node = module_map[m.id]
            if m.parent_id and m.parent_id in module_map:
                module_map[m.parent_id]["children"].append(node)
            else:
                roots.append(node)

        logger.debug(f"模块树构建完成: team_id={team_id}, root_count={len(roots)}, total_modules={len(modules)}")
        return roots

    def update_module(self, module_id: int, data: ApiModuleUpdate, user_id: int) -> ApiModule:
        """更新模块"""
        logger.info(f"更新模块: module_id={module_id}, user_id={user_id}")

        module = self.get_module(module_id)
        if not module:
            logger.warning(f"更新模块失败，模块不存在: module_id={module_id}")
            raise HTTPException(status_code=404, detail="模块不存在")

        update_data = data.model_dump(exclude_unset=True)

        if "name" in update_data and update_data["name"] != module.name:
            parent_id = update_data.get("parent_id", module.parent_id)
            existing = self.db.query(ApiModule).filter(
                ApiModule.team_id == module.team_id,
                ApiModule.parent_id == parent_id if parent_id else None,
                ApiModule.name == update_data["name"]
            ).first()
            if existing:
                logger.warning(f"更新模块失败，同层级下已存在同名模块: name={update_data['name']}, module_id={module_id}")
                raise HTTPException(status_code=400, detail=f"同层级下已存在同名模块: {update_data['name']}")

        if "parent_id" in update_data and update_data["parent_id"] != module.parent_id:
            if update_data["parent_id"]:
                depth = self._get_depth(update_data["parent_id"])
                if depth >= settings.MAX_MODULE_DEPTH:
                    logger.warning(f"更新模块失败，层级超限: module_id={module_id}, parent_id={update_data['parent_id']}, depth={depth}")
                    raise HTTPException(status_code=400, detail=f"模块层级不能超过{settings.MAX_MODULE_DEPTH}层")
                if update_data["parent_id"] == module_id:
                    logger.warning(f"更新模块失败，不能将模块设为自身的子模块: module_id={module_id}")
                    raise HTTPException(status_code=400, detail="不能将模块设为自身的子模块")
                if self._is_descendant(module_id, update_data["parent_id"]):
                    logger.warning(f"更新模块失败，不能将模块移动到其子模块下: module_id={module_id}, target_parent_id={update_data['parent_id']}")
                    raise HTTPException(status_code=400, detail="不能将模块移动到其子模块下")

        for key, value in update_data.items():
            setattr(module, key, value)

        module.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(module)
        logger.info(f"模块更新成功: module_id={module_id}")
        return module

    def delete_module(self, module_id: int) -> bool:
        """删除模块"""
        logger.info(f"删除模块: module_id={module_id}")

        module = self.get_module(module_id)
        if not module:
            logger.warning(f"删除模块失败，模块不存在: module_id={module_id}")
            raise HTTPException(status_code=404, detail="模块不存在")

        api_count = self.db.query(ApiDefinition).filter(
            ApiDefinition.module_id == module_id,
            ApiDefinition.is_deleted == False
        ).count()
        if api_count > 0:
            logger.warning(f"删除模块失败，模块下存在接口: module_id={module_id}, api_count={api_count}")
            raise HTTPException(status_code=400, detail=f"模块下存在 {api_count} 个接口，请先移动或删除接口")

        child_count = self.db.query(ApiModule).filter(ApiModule.parent_id == module_id).count()
        if child_count > 0:
            logger.warning(f"删除模块失败，模块下存在子模块: module_id={module_id}, child_count={child_count}")
            raise HTTPException(status_code=400, detail="模块下存在子模块，请先删除子模块")

        self.db.delete(module)
        self.db.commit()
        logger.info(f"模块删除成功: module_id={module_id}")
        return True

    def _get_depth(self, module_id: int) -> int:
        """获取模块深度"""
        depth = 0
        current = self.get_module(module_id)
        while current and current.parent_id:
            depth += 1
            current = self.get_module(current.parent_id)
        logger.debug(f"获取模块深度: module_id={module_id}, depth={depth}")
        return depth

    def _is_descendant(self, ancestor_id: int, target_id: int) -> bool:
        """检查target_id是否是ancestor_id的后代"""
        current = self.get_module(target_id)
        while current:
            if current.parent_id == ancestor_id:
                return True
            current = self.get_module(current.parent_id) if current.parent_id else None
        return False
