"""
站内通知服务
"""
import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base
from app.models.api import ApiDefinition


class ApiChangeNotification(Base):
    """接口变更通知表"""
    __tablename__ = "api_change_notifications"

    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, ForeignKey("api_definitions.id", ondelete="CASCADE"), nullable=False, index=True)
    version_id = Column(Integer, nullable=True)
    change_type = Column(String(20), nullable=False)
    change_summary = Column(Text, nullable=True)
    notifier_id = Column(Integer, nullable=False)
    notify_type = Column(String(20), default="system")
    created_at = Column(DateTime, default=datetime.utcnow)

    recipients = relationship("ApiChangeNotificationRecipient", back_populates="notification", cascade="all, delete-orphan")


class ApiChangeNotificationRecipient(Base):
    """接口变更通知接收者表"""
    __tablename__ = "api_change_notification_recipients"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey("api_change_notifications.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)

    notification = relationship("ApiChangeNotification", back_populates="recipients")


class NotifyService:
    def __init__(self, db: Session):
        self.db = db

    def notify_change(
        self,
        api_id: int,
        change_type: str,
        change_summary: Optional[str],
        notifier_id: int,
        recipient_ids: List[int],
        version_id: Optional[int] = None
    ) -> Optional[ApiChangeNotification]:
        """发送变更通知"""
        if not recipient_ids:
            return None

        if len(recipient_ids) > 50:
            recipient_ids = recipient_ids[:50]

        notification = ApiChangeNotification(
            api_id=api_id,
            version_id=version_id,
            change_type=change_type,
            change_summary=change_summary,
            notifier_id=notifier_id,
        )
        self.db.add(notification)
        self.db.flush()

        for user_id in recipient_ids:
            recipient = ApiChangeNotificationRecipient(
                notification_id=notification.id,
                user_id=user_id,
            )
            self.db.add(recipient)

        self.db.commit()
        return notification

    def get_user_notifications(
        self,
        user_id: int,
        is_read: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[Dict[str, Any]], int]:
        """获取用户通知列表"""
        query = self.db.query(ApiChangeNotificationRecipient).filter(
            ApiChangeNotificationRecipient.user_id == user_id
        )

        if is_read is not None:
            query = query.filter(ApiChangeNotificationRecipient.is_read == is_read)

        total = query.count()
        recipients = query.order_by(ApiChangeNotificationRecipient.id.desc()) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()

        items = []
        for r in recipients:
            notification = r.notification
            items.append({
                "id": r.id,
                "notification_id": notification.id,
                "api_id": notification.api_id,
                "change_type": notification.change_type,
                "change_summary": notification.change_summary,
                "notifier_id": notification.notifier_id,
                "is_read": r.is_read,
                "read_at": r.read_at,
                "created_at": notification.created_at,
            })

        return items, total

    def mark_as_read(self, recipient_id: int, user_id: int) -> bool:
        """标记通知为已读"""
        recipient = self.db.query(ApiChangeNotificationRecipient).filter(
            ApiChangeNotificationRecipient.id == recipient_id,
            ApiChangeNotificationRecipient.user_id == user_id
        ).first()
        if not recipient:
            return False

        recipient.is_read = True
        recipient.read_at = datetime.utcnow()
        self.db.commit()
        return True

    def mark_all_as_read(self, user_id: int) -> int:
        """标记所有通知为已读"""
        recipients = self.db.query(ApiChangeNotificationRecipient).filter(
            ApiChangeNotificationRecipient.user_id == user_id,
            ApiChangeNotificationRecipient.is_read == False
        ).all()

        now = datetime.utcnow()
        for r in recipients:
            r.is_read = True
            r.read_at = now

        self.db.commit()
        return len(recipients)

    def get_unread_count(self, user_id: int) -> int:
        """获取未读通知数量"""
        return self.db.query(ApiChangeNotificationRecipient).filter(
            ApiChangeNotificationRecipient.user_id == user_id,
            ApiChangeNotificationRecipient.is_read == False
        ).count()
