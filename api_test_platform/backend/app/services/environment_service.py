"""
Environment Service
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from fastapi import HTTPException

from app.models.environment import (
    Environment, EnvService, EnvServer, EnvDatabase, 
    EnvVariable, ServiceType
)
from app.schemas.environment import (
    EnvironmentCreate, EnvironmentUpdate,
    ServiceCreate, ServiceUpdate,
    ServerCreate, ServerUpdate,
    DatabaseCreate, DatabaseUpdate,
    VariableCreate, VariableUpdate
)
from app.core.encryption import encrypt_password, decrypt_password
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EnvironmentService:
    def __init__(self, db: Session):
        self.db = db

    def create_environment(self, env_data: EnvironmentCreate, user_id: Optional[int] = None) -> Environment:
        logger.info(f"创建环境: name={env_data.name}, team_id={env_data.team_id}, is_default={env_data.is_default}, user_id={user_id}")

        if env_data.is_default:
            self._unset_default_environment(env_data.team_id)
            logger.debug(f"取消团队其他默认环境: team_id={env_data.team_id}")

        env = Environment(
            team_id=env_data.team_id,
            name=env_data.name,
            description=env_data.description,
            is_default=env_data.is_default,
            created_by=user_id
        )
        self.db.add(env)
        self.db.flush()

        if env_data.variables:
            for var_data in env_data.variables:
                var = EnvVariable(
                    environment_id=env.id,
                    key=var_data.key,
                    value=encrypt_password(var_data.value) if var_data.is_encrypted else var_data.value,
                    value_type=var_data.value_type,
                    is_encrypted=var_data.is_encrypted,
                    description=var_data.description
                )
                self.db.add(var)
            logger.debug(f"创建环境变量: env_id={env.id}, variable_count={len(env_data.variables)}")

        if env_data.services:
            for idx, svc_data in enumerate(env_data.services):
                self._create_service(env.id, svc_data, idx)
            logger.debug(f"创建环境服务: env_id={env.id}, service_count={len(env_data.services)}")

        self.db.commit()
        self.db.refresh(env)
        logger.info(f"环境创建成功: env_id={env.id}, name={env.name}")
        return env

    def get_environment(self, env_id: int) -> Optional[Environment]:
        logger.debug(f"获取环境: env_id={env_id}")
        env = self.db.query(Environment).filter(Environment.id == env_id).first()
        if not env:
            logger.warning(f"环境不存在: env_id={env_id}")
        return env

    def get_environments(
        self,
        team_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[Environment], int]:
        logger.info(f"获取环境列表: team_id={team_id}, is_active={is_active}, search={search}, page={page}, page_size={page_size}")

        query = self.db.query(Environment).options(joinedload(Environment.services))

        if team_id is not None:
            query = query.filter(Environment.team_id == team_id)
        if is_active is not None:
            query = query.filter(Environment.is_active == is_active)
        if search:
            query = query.filter(
                (Environment.name.ilike(f"%{search}%")) |
                (Environment.description.ilike(f"%{search}%"))
            )

        total = query.count()
        items = query.order_by(Environment.is_default.desc(), Environment.updated_at.desc()) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()

        logger.debug(f"环境列表查询结果: total={total}, returned={len(items)}")
        return items, total

    def update_environment(self, env_id: int, env_data: EnvironmentUpdate) -> Environment:
        logger.info(f"更新环境: env_id={env_id}")

        env = self.get_environment(env_id)
        if not env:
            logger.warning(f"更新环境失败，环境不存在: env_id={env_id}")
            raise HTTPException(status_code=404, detail="Environment not found")

        update_data = env_data.model_dump(exclude_unset=True)

        if update_data.get("is_default"):
            self._unset_default_environment(env.team_id)
            logger.debug(f"取消团队其他默认环境: team_id={env.team_id}")

        for key, value in update_data.items():
            setattr(env, key, value)

        self.db.commit()
        self.db.refresh(env)
        logger.info(f"环境更新成功: env_id={env_id}")
        return env

    def delete_environment(self, env_id: int) -> bool:
        logger.info(f"删除环境: env_id={env_id}")

        env = self.get_environment(env_id)
        if not env:
            logger.warning(f"删除环境失败，环境不存在: env_id={env_id}")
            raise HTTPException(status_code=404, detail="Environment not found")

        self.db.delete(env)
        self.db.commit()
        logger.info(f"环境删除成功: env_id={env_id}")
        return True

    def set_default_environment(self, env_id: int) -> Environment:
        logger.info(f"设置默认环境: env_id={env_id}")

        env = self.get_environment(env_id)
        if not env:
            logger.warning(f"设置默认环境失败，环境不存在: env_id={env_id}")
            raise HTTPException(status_code=404, detail="Environment not found")

        self._unset_default_environment(env.team_id)
        env.is_default = True
        self.db.commit()
        self.db.refresh(env)
        logger.info(f"默认环境设置成功: env_id={env_id}, team_id={env.team_id}")
        return env

    def copy_environment(self, env_id: int) -> Environment:
        logger.info(f"复制环境: env_id={env_id}")

        env = self.get_environment(env_id)
        if not env:
            logger.warning(f"复制环境失败，环境不存在: env_id={env_id}")
            raise HTTPException(status_code=404, detail="Environment not found")

        new_env = Environment(
            team_id=env.team_id,
            name=f"{env.name} (副本)",
            description=env.description,
            is_default=False,
            is_active=True,
            created_by=env.created_by
        )
        self.db.add(new_env)
        self.db.flush()

        for service in env.services:
            new_service = EnvService(
                environment_id=new_env.id,
                name=service.name,
                service_type=service.service_type,
                description=service.description,
                sort_order=service.sort_order
            )
            self.db.add(new_service)
            self.db.flush()

            for server in service.servers:
                new_server = EnvServer(
                    service_id=new_service.id,
                    name=server.name,
                    host=server.host,
                    port=server.port,
                    protocol=server.protocol,
                    base_path=server.base_path,
                    ssl_config=server.ssl_config,
                    headers=server.headers,
                    timeout=server.timeout,
                    is_default=server.is_default
                )
                self.db.add(new_server)

            for db in service.databases:
                new_db = EnvDatabase(
                    service_id=new_service.id,
                    name=db.name,
                    db_type=db.db_type,
                    host=db.host,
                    port=db.port,
                    database=db.database,
                    username=db.username,
                    password=db.password,
                    charset=db.charset,
                    extra_config=db.extra_config,
                    is_default=db.is_default
                )
                self.db.add(new_db)

        logger.debug(f"复制环境服务: source_env_id={env_id}, service_count={len(env.services)}")

        for var in env.variables:
            new_var = EnvVariable(
                environment_id=new_env.id,
                key=var.key,
                value=var.value,
                value_type=var.value_type,
                is_encrypted=var.is_encrypted,
                description=var.description
            )
            self.db.add(new_var)

        self.db.commit()
        self.db.refresh(new_env)
        self.db.expire_all()
        logger.info(f"环境复制成功: source_env_id={env_id}, new_env_id={new_env.id}")
        return self.get_environment(new_env.id)

    def _unset_default_environment(self, team_id: Optional[int]):
        logger.debug(f"取消默认环境: team_id={team_id}")

        query = self.db.query(Environment).filter(Environment.is_default == True)
        if team_id:
            query = query.filter(Environment.team_id == team_id)
        else:
            query = query.filter(Environment.team_id == None)
        updated_count = query.update({"is_default": False})
        if updated_count > 0:
            logger.debug(f"取消了{updated_count}个默认环境: team_id={team_id}")

    def _create_service(self, env_id: int, svc_data: ServiceCreate, sort_order: int = 0) -> EnvService:
        logger.debug(f"创建服务: env_id={env_id}, service_name={svc_data.name}, sort_order={sort_order}")

        service = EnvService(
            environment_id=env_id,
            name=svc_data.name,
            service_type=svc_data.service_type,
            description=svc_data.description,
            sort_order=sort_order
        )
        self.db.add(service)
        self.db.flush()
        return service

    def create_service(self, env_id: int, svc_data: ServiceCreate) -> EnvService:
        logger.info(f"创建服务: env_id={env_id}, service_name={svc_data.name}")

        env = self.get_environment(env_id)
        if not env:
            logger.warning(f"创建服务失败，环境不存在: env_id={env_id}")
            raise HTTPException(status_code=404, detail="Environment not found")

        existing_count = self.db.query(EnvService).filter(EnvService.environment_id == env_id).count()
        if existing_count >= settings.MAX_SERVICES_PER_ENVIRONMENT:
            logger.warning(f"服务数量已达上限: env_id={env_id}, count={existing_count}, max={settings.MAX_SERVICES_PER_ENVIRONMENT}")
            raise HTTPException(
                status_code=400,
                detail=f"Maximum services per environment ({settings.MAX_SERVICES_PER_ENVIRONMENT}) reached"
            )

        max_order = self.db.query(EnvService).filter(
            EnvService.environment_id == env_id
        ).count()

        service = self._create_service(env_id, svc_data, max_order)
        self.db.commit()
        self.db.refresh(service)
        logger.info(f"服务创建成功: service_id={service.id}, name={service.name}")
        return service

    def get_service(self, service_id: int) -> Optional[EnvService]:
        logger.debug(f"获取服务: service_id={service_id}")
        service = self.db.query(EnvService).filter(EnvService.id == service_id).first()
        if not service:
            logger.warning(f"服务不存在: service_id={service_id}")
        return service

    def get_services(
        self,
        env_id: int,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> tuple[List[EnvService], int]:
        logger.info(f"获取服务列表: env_id={env_id}, search={search}, page={page}, page_size={page_size}")

        query = self.db.query(EnvService).filter(EnvService.environment_id == env_id)

        if search:
            query = query.filter(EnvService.name.ilike(f"%{search}%"))

        total = query.count()
        items = query.order_by(EnvService.sort_order, EnvService.id) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()

        logger.debug(f"服务列表查询结果: env_id={env_id}, total={total}, returned={len(items)}")
        return items, total

    def get_all_services(
        self,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 100
    ) -> tuple[List[EnvService], int]:
        logger.info(f"获取所有服务: search={search}, page={page}, page_size={page_size}")

        query = self.db.query(EnvService).join(Environment).filter(Environment.is_active == True)

        if search:
            query = query.filter(EnvService.name.ilike(f"%{search}%"))

        total = query.count()
        items = query.order_by(EnvService.sort_order, EnvService.id) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()

        logger.debug(f"所有服务查询结果: total={total}, returned={len(items)}")
        return items, total

    def update_service(self, service_id: int, svc_data: ServiceUpdate) -> EnvService:
        logger.info(f"更新服务: service_id={service_id}")

        service = self.get_service(service_id)
        if not service:
            logger.warning(f"更新服务失败，服务不存在: service_id={service_id}")
            raise HTTPException(status_code=404, detail="Service not found")

        update_data = svc_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(service, key, value)

        self.db.commit()
        self.db.refresh(service)
        logger.info(f"服务更新成功: service_id={service_id}")
        return service

    def delete_service(self, service_id: int) -> bool:
        logger.info(f"删除服务: service_id={service_id}")

        service = self.get_service(service_id)
        if not service:
            logger.warning(f"删除服务失败，服务不存在: service_id={service_id}")
            raise HTTPException(status_code=404, detail="Service not found")

        self.db.delete(service)
        self.db.commit()
        logger.info(f"服务删除成功: service_id={service_id}")
        return True

    def copy_service(self, service_id: int) -> EnvService:
        logger.info(f"复制服务: service_id={service_id}")

        service = self.get_service(service_id)
        if not service:
            logger.warning(f"复制服务失败，服务不存在: service_id={service_id}")
            raise HTTPException(status_code=404, detail="Service not found")

        existing_count = self.db.query(EnvService).filter(
            EnvService.environment_id == service.environment_id
        ).count()
        if existing_count >= settings.MAX_SERVICES_PER_ENVIRONMENT:
            logger.warning(f"服务数量已达上限: env_id={service.environment_id}, count={existing_count}, max={settings.MAX_SERVICES_PER_ENVIRONMENT}")
            raise HTTPException(
                status_code=400,
                detail=f"Maximum services per environment ({settings.MAX_SERVICES_PER_ENVIRONMENT}) reached"
            )

        new_service = EnvService(
            environment_id=service.environment_id,
            name=f"{service.name} (副本)",
            service_type=service.service_type,
            description=service.description,
            sort_order=service.sort_order
        )
        self.db.add(new_service)
        self.db.flush()

        for server in service.servers:
            new_server = EnvServer(
                service_id=new_service.id,
                name=server.name,
                host=server.host,
                port=server.port,
                protocol=server.protocol,
                base_path=server.base_path,
                ssl_config=server.ssl_config,
                headers=server.headers,
                timeout=server.timeout,
                is_default=server.is_default
            )
            self.db.add(new_server)

        for db in service.databases:
            new_db = EnvDatabase(
                service_id=new_service.id,
                name=db.name,
                db_type=db.db_type,
                host=db.host,
                port=db.port,
                database=db.database,
                username=db.username,
                password=db.password,
                charset=db.charset,
                extra_config=db.extra_config,
                is_default=db.is_default
            )
            self.db.add(new_db)

        self.db.commit()
        self.db.refresh(new_service)
        logger.info(f"服务复制成功: source_service_id={service_id}, new_service_id={new_service.id}")
        return new_service

    def create_server(self, service_id: int, server_data: ServerCreate) -> EnvServer:
        logger.info(f"创建服务器: service_id={service_id}, server_name={server_data.name}")

        service = self.get_service(service_id)
        if not service:
            logger.warning(f"创建服务器失败，服务不存在: service_id={service_id}")
            raise HTTPException(status_code=404, detail="Service not found")

        existing_count = self.db.query(EnvServer).filter(EnvServer.service_id == service_id).count()
        if existing_count >= settings.MAX_SERVERS_PER_SERVICE:
            logger.warning(f"服务器数量已达上限: service_id={service_id}, count={existing_count}, max={settings.MAX_SERVERS_PER_SERVICE}")
            raise HTTPException(
                status_code=400,
                detail=f"Maximum servers per service ({settings.MAX_SERVERS_PER_SERVICE}) reached"
            )

        server = EnvServer(service_id=service_id, **server_data.model_dump())
        self.db.add(server)
        self.db.commit()
        self.db.refresh(server)
        logger.info(f"服务器创建成功: server_id={server.id}, name={server.name}")
        return server

    def update_server(self, server_id: int, server_data: ServerUpdate) -> EnvServer:
        logger.info(f"更新服务器: server_id={server_id}")

        server = self.db.query(EnvServer).filter(EnvServer.id == server_id).first()
        if not server:
            logger.warning(f"更新服务器失败，服务器不存在: server_id={server_id}")
            raise HTTPException(status_code=404, detail="Server not found")

        update_data = server_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(server, key, value)

        self.db.commit()
        self.db.refresh(server)
        logger.info(f"服务器更新成功: server_id={server_id}")
        return server

    def delete_server(self, server_id: int) -> bool:
        logger.info(f"删除服务器: server_id={server_id}")

        server = self.db.query(EnvServer).filter(EnvServer.id == server_id).first()
        if not server:
            logger.warning(f"删除服务器失败，服务器不存在: server_id={server_id}")
            raise HTTPException(status_code=404, detail="Server not found")

        self.db.delete(server)
        self.db.commit()
        logger.info(f"服务器删除成功: server_id={server_id}")
        return True

    def create_database(self, service_id: int, db_data: DatabaseCreate) -> EnvDatabase:
        logger.info(f"创建数据库: service_id={service_id}, db_name={db_data.name}")

        service = self.get_service(service_id)
        if not service:
            logger.warning(f"创建数据库失败，服务不存在: service_id={service_id}")
            raise HTTPException(status_code=404, detail="Service not found")

        existing_count = self.db.query(EnvDatabase).filter(EnvDatabase.service_id == service_id).count()
        if existing_count >= settings.MAX_DATABASES_PER_SERVICE:
            logger.warning(f"数据库数量已达上限: service_id={service_id}, count={existing_count}, max={settings.MAX_DATABASES_PER_SERVICE}")
            raise HTTPException(
                status_code=400,
                detail=f"Maximum databases per service ({settings.MAX_DATABASES_PER_SERVICE}) reached"
            )

        encrypted_password = encrypt_password(db_data.password)
        db = EnvDatabase(
            service_id=service_id,
            name=db_data.name,
            db_type=db_data.db_type,
            host=db_data.host,
            port=db_data.port,
            database=db_data.database,
            username=db_data.username,
            password=encrypted_password,
            charset=db_data.charset,
            extra_config=db_data.extra_config,
            is_default=db_data.is_default
        )
        self.db.add(db)
        self.db.commit()
        self.db.refresh(db)
        logger.info(f"数据库创建成功: db_id={db.id}, name={db.name}")
        return db

    def update_database(self, db_id: int, db_data: DatabaseUpdate) -> EnvDatabase:
        logger.info(f"更新数据库: db_id={db_id}")

        db = self.db.query(EnvDatabase).filter(EnvDatabase.id == db_id).first()
        if not db:
            logger.warning(f"更新数据库失败，数据库不存在: db_id={db_id}")
            raise HTTPException(status_code=404, detail="Database not found")

        update_data = db_data.model_dump(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            update_data["password"] = encrypt_password(update_data["password"])
            logger.debug(f"数据库密码已加密: db_id={db_id}")

        for key, value in update_data.items():
            setattr(db, key, value)

        self.db.commit()
        self.db.refresh(db)
        logger.info(f"数据库更新成功: db_id={db_id}")
        return db

    def delete_database(self, db_id: int) -> bool:
        logger.info(f"删除数据库: db_id={db_id}")

        db = self.db.query(EnvDatabase).filter(EnvDatabase.id == db_id).first()
        if not db:
            logger.warning(f"删除数据库失败，数据库不存在: db_id={db_id}")
            raise HTTPException(status_code=404, detail="Database not found")

        self.db.delete(db)
        self.db.commit()
        logger.info(f"数据库删除成功: db_id={db_id}")
        return True

    def create_variable(self, env_id: int, var_data: VariableCreate) -> EnvVariable:
        logger.info(f"创建环境变量: env_id={env_id}, key={var_data.key}")

        env = self.get_environment(env_id)
        if not env:
            logger.warning(f"创建环境变量失败，环境不存在: env_id={env_id}")
            raise HTTPException(status_code=404, detail="Environment not found")

        existing_count = self.db.query(EnvVariable).filter(
            EnvVariable.environment_id == env_id
        ).count()
        if existing_count >= settings.MAX_VARIABLES_PER_ENVIRONMENT:
            logger.warning(f"环境变量数量已达上限: env_id={env_id}, count={existing_count}, max={settings.MAX_VARIABLES_PER_ENVIRONMENT}")
            raise HTTPException(
                status_code=400,
                detail=f"Maximum variables per environment ({settings.MAX_VARIABLES_PER_ENVIRONMENT}) reached"
            )

        existing = self.db.query(EnvVariable).filter(
            and_(EnvVariable.environment_id == env_id, EnvVariable.key == var_data.key)
        ).first()
        if existing:
            logger.warning(f"环境变量已存在: env_id={env_id}, key={var_data.key}")
            raise HTTPException(status_code=400, detail=f"Variable '{var_data.key}' already exists")

        var = EnvVariable(
            environment_id=env_id,
            key=var_data.key,
            value=encrypt_password(var_data.value) if var_data.is_encrypted else var_data.value,
            value_type=var_data.value_type,
            is_encrypted=var_data.is_encrypted,
            description=var_data.description
        )
        self.db.add(var)
        self.db.commit()
        self.db.refresh(var)
        logger.info(f"环境变量创建成功: var_id={var.id}, key={var.key}")
        return var

    def update_variable(self, var_id: int, var_data: VariableUpdate) -> EnvVariable:
        logger.info(f"更新环境变量: var_id={var_id}")

        var = self.db.query(EnvVariable).filter(EnvVariable.id == var_id).first()
        if not var:
            logger.warning(f"更新环境变量失败，变量不存在: var_id={var_id}")
            raise HTTPException(status_code=404, detail="Variable not found")

        update_data = var_data.model_dump(exclude_unset=True)

        if "key" in update_data and update_data["key"] != var.key:
            existing = self.db.query(EnvVariable).filter(
                and_(
                    EnvVariable.environment_id == var.environment_id,
                    EnvVariable.key == update_data["key"]
                )
            ).first()
            if existing:
                logger.warning(f"环境变量key已存在: env_id={var.environment_id}, key={update_data['key']}")
                raise HTTPException(status_code=400, detail=f"Variable '{update_data['key']}' already exists")

        if "value" in update_data:
            is_encrypted = update_data.get("is_encrypted", var.is_encrypted)
            if is_encrypted:
                update_data["value"] = encrypt_password(update_data["value"])
                logger.debug(f"环境变量值已加密: var_id={var_id}")

        for key, value in update_data.items():
            setattr(var, key, value)

        self.db.commit()
        self.db.refresh(var)
        logger.info(f"环境变量更新成功: var_id={var_id}")
        return var

    def delete_variable(self, var_id: int) -> bool:
        logger.info(f"删除环境变量: var_id={var_id}")

        var = self.db.query(EnvVariable).filter(EnvVariable.id == var_id).first()
        if not var:
            logger.warning(f"删除环境变量失败，变量不存在: var_id={var_id}")
            raise HTTPException(status_code=404, detail="Variable not found")

        self.db.delete(var)
        self.db.commit()
        logger.info(f"环境变量删除成功: var_id={var_id}")
        return True

    def get_decrypted_database(self, db_id: int) -> Optional[Dict]:
        logger.debug(f"获取解密数据库信息: db_id={db_id}")

        db = self.db.query(EnvDatabase).filter(EnvDatabase.id == db_id).first()
        if not db:
            logger.warning(f"数据库不存在: db_id={db_id}")
            return None

        return {
            "id": db.id,
            "service_id": db.service_id,
            "name": db.name,
            "db_type": db.db_type,
            "host": db.host,
            "port": db.port,
            "database": db.database,
            "username": db.username,
            "password": decrypt_password(db.password),
            "charset": db.charset,
            "extra_config": db.extra_config,
            "is_default": db.is_default
        }
