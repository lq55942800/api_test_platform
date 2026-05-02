"""
标签管理服务
"""
import json
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.api import ApiTag, ApiTagRelation, ApiDefinition
from app.schemas.api import ApiTagCreate, ApiTagBase
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class TagService:
    def __init__(self, db: Session):
        self.db = db

    def create_tag(self, data: ApiTagCreate, user_id: int) -> ApiTag:
        """创建标签"""
        logger.info(f"创建标签: name={data.name}, team_id={data.team_id}, user_id={user_id}")

        existing = self.db.query(ApiTag).filter(
            ApiTag.team_id == data.team_id,
            ApiTag.name == data.name
        ).first()
        if existing:
            logger.warning(f"创建标签失败，标签已存在: name={data.name}, team_id={data.team_id}")
            raise HTTPException(status_code=400, detail=f"标签 '{data.name}' 已存在")

        tag = ApiTag(
            team_id=data.team_id,
            name=data.name,
            color=data.color,
            tag_group=data.tag_group,
            created_by=user_id,
        )
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        logger.info(f"标签创建成功: tag_id={tag.id}, name={tag.name}, team_id={data.team_id}")
        return tag

    def get_tag(self, tag_id: int) -> Optional[ApiTag]:
        """获取标签"""
        logger.debug(f"获取标签: tag_id={tag_id}")
        tag = self.db.query(ApiTag).filter(ApiTag.id == tag_id).first()
        if not tag:
            logger.warning(f"标签不存在: tag_id={tag_id}")
        return tag

    def get_tags_by_team(self, team_id: int) -> List[ApiTag]:
        """获取团队标签列表"""
        logger.debug(f"获取团队标签列表: team_id={team_id}")
        tags = self.db.query(ApiTag).filter(ApiTag.team_id == team_id).order_by(ApiTag.id).all()
        logger.debug(f"团队标签列表查询结果: team_id={team_id}, tag_count={len(tags)}")
        return tags

    def delete_tag(self, tag_id: int) -> bool:
        """删除标签"""
        logger.info(f"删除标签: tag_id={tag_id}")

        tag = self.get_tag(tag_id)
        if not tag:
            logger.warning(f"删除标签失败，标签不存在: tag_id={tag_id}")
            raise HTTPException(status_code=404, detail="标签不存在")

        relation_count = self.db.query(ApiTagRelation).filter(ApiTagRelation.tag_id == tag_id).delete()
        logger.debug(f"删除标签关联关系: tag_id={tag_id}, relation_count={relation_count}")

        self.db.delete(tag)
        self.db.commit()
        logger.info(f"标签删除成功: tag_id={tag_id}, name={tag.name}")
        return True

    def set_api_tags(self, api_id: int, tag_ids: List[int]) -> List[ApiTagRelation]:
        """设置接口标签"""
        logger.info(f"设置接口标签: api_id={api_id}, tag_ids={tag_ids}")

        self.db.query(ApiTagRelation).filter(ApiTagRelation.api_id == api_id).delete()

        if len(tag_ids) > settings.MAX_TAGS_PER_API:
            logger.warning(f"设置接口标签失败，标签数量超限: api_id={api_id}, tag_count={len(tag_ids)}, max={settings.MAX_TAGS_PER_API}")
            raise HTTPException(status_code=400, detail=f"单个接口最多添加 {settings.MAX_TAGS_PER_API} 个标签")

        relations = []
        for tag_id in tag_ids:
            tag = self.get_tag(tag_id)
            if tag:
                rel = ApiTagRelation(api_id=api_id, tag_id=tag_id)
                self.db.add(rel)
                relations.append(rel)
            else:
                logger.warning(f"设置接口标签时标签不存在: tag_id={tag_id}, api_id={api_id}")

        self.db.commit()
        logger.info(f"接口标签设置成功: api_id={api_id}, relation_count={len(relations)}")
        return relations

    def get_apis_by_tag(self, tag_id: int, team_id: int, page: int = 1, page_size: int = 20) -> tuple[List[ApiDefinition], int]:
        """根据标签获取接口列表"""
        logger.info(f"根据标签获取接口列表: tag_id={tag_id}, team_id={team_id}, page={page}, page_size={page_size}")

        query = self.db.query(ApiDefinition).join(
            ApiTagRelation, ApiDefinition.id == ApiTagRelation.api_id
        ).filter(
            ApiTagRelation.tag_id == tag_id,
            ApiDefinition.team_id == team_id,
            ApiDefinition.is_deleted == False
        )

        total = query.count()
        items = query.order_by(ApiDefinition.updated_at.desc()) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()

        logger.debug(f"标签接口列表查询结果: tag_id={tag_id}, total={total}, returned={len(items)}")
        return items, total

    def get_api_tags(self, api_id: int) -> List[dict]:
        """获取接口的标签列表 - 使用JOIN优化查询"""
        logger.debug(f"获取接口标签: api_id={api_id}")

        results = self.db.query(ApiTag).join(
            ApiTagRelation, ApiTag.id == ApiTagRelation.tag_id
        ).filter(
            ApiTagRelation.api_id == api_id
        ).all()

        if not results:
            logger.debug(f"接口无标签: api_id={api_id}")

        return [
            {
                "id": tag.id,
                "name": tag.name,
                "color": tag.color,
                "tag_group": tag.tag_group
            }
            for tag in results
        ]
