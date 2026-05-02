"""
编辑锁定服务（基于数据库实现）
"""
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timedelta

from app.models.api import ApiDefinition
from app.core.config import settings


class LockService:
    """编辑锁定服务"""

    LOCK_TTL_MINUTES = 30

    def __init__(self, db: Session):
        self.db = db

    def acquire_lock(self, api_id: int, user_id: int) -> dict:
        """获取编辑锁"""
        api = self.db.query(ApiDefinition).filter(
            ApiDefinition.id == api_id,
            ApiDefinition.is_deleted == False
        ).first()
        if not api:
            raise HTTPException(status_code=404, detail="接口不存在")

        if api.lock_user_id and api.lock_user_id != user_id:
            if not self._is_lock_expired(api):
                return {
                    "acquired": False,
                    "locked_by": api.lock_user_id,
                    "locked_at": api.lock_time,
                }

        api.lock_user_id = user_id
        api.lock_time = datetime.utcnow()
        self.db.commit()

        return {"acquired": True, "locked_by": None, "locked_at": None}

    def release_lock(self, api_id: int, user_id: int) -> bool:
        """释放编辑锁"""
        api = self.db.query(ApiDefinition).filter(ApiDefinition.id == api_id).first()
        if not api:
            raise HTTPException(status_code=404, detail="接口不存在")

        if api.lock_user_id and api.lock_user_id != user_id:
            raise HTTPException(status_code=403, detail="只能释放自己持有的锁")

        api.lock_user_id = None
        api.lock_time = None
        self.db.commit()
        return True

    def force_release_lock(self, api_id: int, operator_id: int) -> bool:
        """强制释放编辑锁（团队负责人使用）"""
        api = self.db.query(ApiDefinition).filter(ApiDefinition.id == api_id).first()
        if not api:
            raise HTTPException(status_code=404, detail="接口不存在")

        api.lock_user_id = None
        api.lock_time = None
        self.db.commit()
        return True

    def get_lock_status(self, api_id: int) -> dict:
        """获取锁定状态"""
        api = self.db.query(ApiDefinition).filter(ApiDefinition.id == api_id).first()
        if not api:
            raise HTTPException(status_code=404, detail="接口不存在")

        if api.lock_user_id and not self._is_lock_expired(api):
            return {
                "locked": True,
                "locked_by": api.lock_user_id,
                "locked_at": api.lock_time,
            }

        if api.lock_user_id and self._is_lock_expired(api):
            api.lock_user_id = None
            api.lock_time = None
            self.db.commit()

        return {"locked": False, "locked_by": None, "locked_at": None}

    def _is_lock_expired(self, api: ApiDefinition) -> bool:
        """检查锁是否过期"""
        if not api.lock_time:
            return True
        expiry = api.lock_time + timedelta(minutes=self.LOCK_TTL_MINUTES)
        return datetime.utcnow() > expiry
