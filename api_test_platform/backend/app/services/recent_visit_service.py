from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from app.models.api import ApiDefinition, ApiRecentVisit
from app.core.logging import get_logger

logger = get_logger(__name__)


class RecentVisitService:
    def __init__(self, db: Session):
        self.db = db

    def record_visit(self, api_id: int, user_id: int) -> None:
        logger.info(f"记录访问: api_id={api_id}, user_id={user_id}")

        existing = (
            self.db.query(ApiRecentVisit)
            .filter(ApiRecentVisit.api_id == api_id, ApiRecentVisit.user_id == user_id)
            .first()
        )
        if existing:
            existing.visited_at = datetime.utcnow()
            logger.debug(f"更新访问时间: api_id={api_id}, user_id={user_id}")
        else:
            visit = ApiRecentVisit(api_id=api_id, user_id=user_id)
            self.db.add(visit)
            logger.debug(f"创建新访问记录: api_id={api_id}, user_id={user_id}")
        self.db.commit()

    def get_recent_visits(self, user_id: int, limit: int = 10) -> List[ApiDefinition]:
        logger.info(f"获取最近访问: user_id={user_id}, limit={limit}")

        visits = (
            self.db.query(ApiRecentVisit)
            .filter(ApiRecentVisit.user_id == user_id)
            .order_by(ApiRecentVisit.visited_at.desc())
            .limit(limit)
            .all()
        )
        api_ids = [v.api_id for v in visits]
        if not api_ids:
            logger.debug(f"用户无最近访问记录: user_id={user_id}")
            return []
        apis = (
            self.db.query(ApiDefinition)
            .filter(ApiDefinition.id.in_(api_ids), ApiDefinition.is_deleted == False)
            .all()
        )
        api_map = {api.id: api for api in apis}
        result = [api_map[aid] for aid in api_ids if aid in api_map]

        missing_ids = [aid for aid in api_ids if aid not in api_map]
        if missing_ids:
            logger.warning(f"最近访问中部分接口不存在或已删除: user_id={user_id}, missing_api_ids={missing_ids}")

        logger.debug(f"获取最近访问结果: user_id={user_id}, visit_count={len(visits)}, result_count={len(result)}")
        return result
