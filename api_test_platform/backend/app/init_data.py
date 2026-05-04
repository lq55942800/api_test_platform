"""
基础数据初始化脚本
创建默认Team和User，确保数据库有基础数据用于测试
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.base_models import Team, User, TeamMember
from passlib.context import CryptContext
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def init_base_data(db: Session):
    """初始化基础数据"""
    
    # 检查是否已存在默认Team
    default_team = db.query(Team).filter(Team.id == 1).first()
    if not default_team:
        default_team = Team(
            id=1,
            name="Default Team",
            description="Default team for testing",
            is_active=True
        )
        db.add(default_team)
        logger.info("Created default team (ID=1)")
    else:
        logger.info("Default team already exists (ID=1)")
    
    # 检查是否已存在默认User
    default_user = db.query(User).filter(User.id == 1).first()
    if not default_user:
        # 创建默认用户，密码为 "admin123"
        default_user = User(
            id=1,
            username="admin",
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),
            full_name="Default Admin",
            is_active=True,
            is_superuser=True
        )
        db.add(default_user)
        logger.info("Created default user (ID=1, username=admin, password=admin123)")
    else:
        logger.info("Default user already exists (ID=1)")
    
    # 创建默认团队成员关系
    default_membership = db.query(TeamMember).filter(
        TeamMember.team_id == 1,
        TeamMember.user_id == 1
    ).first()
    if not default_membership:
        default_membership = TeamMember(
            team_id=1,
            user_id=1,
            role="team_leader",
            status="active"
        )
        db.add(default_membership)
        logger.info("Created default team membership (admin as team_leader)")
    
    # 提交更改
    db.commit()
    
    return default_team, default_user


def main():
    """主函数"""
    logger.info("Starting base data initialization...")
    
    db = SessionLocal()
    try:
        team, user = init_base_data(db)
        logger.info("Base data initialization completed successfully!")
        logger.info(f"Team: ID={team.id}, Name={team.name}")
        logger.info(f"User: ID={user.id}, Username={user.username}, Email={user.email}")
        logger.info("Default password: admin123")
    except Exception as e:
        logger.error(f"Failed to initialize base data: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
