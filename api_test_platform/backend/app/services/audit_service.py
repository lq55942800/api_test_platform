"""
审计日志服务
"""
import json
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.api import ApiAuditLog, AuditAction


class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        team_id: int,
        user_id: int,
        action: AuditAction,
        api_id: Optional[int] = None,
        resource_type: str = "api",
        resource_name: Optional[str] = None,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        change_summary: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> ApiAuditLog:
        """记录审计日志"""
        if isinstance(old_value, (dict, list)):
            old_value = json.dumps(old_value, ensure_ascii=False)
        if isinstance(new_value, (dict, list)):
            new_value = json.dumps(new_value, ensure_ascii=False)

        log_entry = ApiAuditLog(
            team_id=team_id,
            api_id=api_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_name=resource_name,
            old_value=old_value,
            new_value=new_value,
            change_summary=change_summary,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(log_entry)
        self.db.flush()
        return log_entry

    def get_audit_logs(
        self,
        team_id: int,
        api_id: Optional[int] = None,
        action: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[ApiAuditLog], int]:
        """获取审计日志"""
        query = self.db.query(ApiAuditLog).filter(ApiAuditLog.team_id == team_id)

        if api_id:
            query = query.filter(ApiAuditLog.api_id == api_id)
        if action:
            query = query.filter(ApiAuditLog.action == action)

        total = query.count()
        items = query.order_by(ApiAuditLog.created_at.desc()) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()

        return items, total
