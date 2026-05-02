"""
Environment Management API Routes
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.session import get_db
from app.schemas.environment import (
    EnvironmentCreate, EnvironmentUpdate, EnvironmentResponse, EnvironmentListResponse,
    ServiceCreate, ServiceUpdate, ServiceResponse, ServiceListResponse,
    ServerCreate, ServerUpdate, ServerResponse,
    DatabaseCreate, DatabaseUpdate, DatabaseResponse,
    VariableCreate, VariableUpdate, VariableResponse,
    VariableResolveRequest, VariableResolveResponse
)
from app.services.environment_service import EnvironmentService
from app.services.variable_resolver import VariableResolver

logger = get_logger(__name__)

router = APIRouter(prefix="/environments", tags=["Environments"])


@router.post("", response_model=EnvironmentResponse, status_code=201)
def create_environment(
    env_data: EnvironmentCreate,
    db: Session = Depends(get_db)
):
    logger.info(f"创建环境: name={env_data.name}, team_id={env_data.team_id}")
    try:
        service = EnvironmentService(db)
        result = service.create_environment(env_data)
        logger.info(f"环境创建成功: name={env_data.name}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建环境失败: name={env_data.name}, error={str(e)}")
        raise


@router.get("", response_model=EnvironmentListResponse)
def list_environments(
    team_id: Optional[int] = Query(None, description="Team ID filter"),
    is_active: Optional[bool] = Query(None, description="Active status filter"),
    search: Optional[str] = Query(None, description="Search keyword for name or description"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    logger.info(f"查询环境列表: team_id={team_id}, is_active={is_active}, search={search}, page={page}")
    try:
        service = EnvironmentService(db)
        items, total = service.get_environments(team_id, is_active, search, page, page_size)
        logger.info(f"查询环境列表成功: total={total}")
        return EnvironmentListResponse(
            items=[EnvironmentResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询环境列表失败: team_id={team_id}, error={str(e)}")
        raise


@router.get("/{env_id}", response_model=EnvironmentResponse)
def get_environment(
    env_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"查询环境详情: env_id={env_id}")
    try:
        service = EnvironmentService(db)
        env = service.get_environment(env_id)
        if not env:
            logger.warning(f"环境不存在: env_id={env_id}")
            raise HTTPException(status_code=404, detail="Environment not found")
        return env
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询环境详情失败: env_id={env_id}, error={str(e)}")
        raise


@router.put("/{env_id}", response_model=EnvironmentResponse)
def update_environment(
    env_id: int,
    env_data: EnvironmentUpdate,
    db: Session = Depends(get_db)
):
    logger.info(f"更新环境: env_id={env_id}")
    try:
        service = EnvironmentService(db)
        result = service.update_environment(env_id, env_data)
        logger.info(f"环境更新成功: env_id={env_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新环境失败: env_id={env_id}, error={str(e)}")
        raise


@router.delete("/{env_id}", status_code=204)
def delete_environment(
    env_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"删除环境: env_id={env_id}")
    try:
        service = EnvironmentService(db)
        service.delete_environment(env_id)
        logger.info(f"环境删除成功: env_id={env_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除环境失败: env_id={env_id}, error={str(e)}")
        raise


@router.put("/{env_id}/default", response_model=EnvironmentResponse)
def set_default_environment(
    env_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"设置默认环境: env_id={env_id}")
    try:
        service = EnvironmentService(db)
        result = service.set_default_environment(env_id)
        logger.info(f"默认环境设置成功: env_id={env_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"设置默认环境失败: env_id={env_id}, error={str(e)}")
        raise


@router.post("/{env_id}/copy", response_model=EnvironmentResponse, status_code=201)
def copy_environment(
    env_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"复制环境: env_id={env_id}")
    try:
        service = EnvironmentService(db)
        result = service.copy_environment(env_id)
        logger.info(f"环境复制成功: source_env_id={env_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"复制环境失败: env_id={env_id}, error={str(e)}")
        raise


@router.post("/{env_id}/services", response_model=ServiceResponse, status_code=201)
def create_service(
    env_id: int,
    svc_data: ServiceCreate,
    db: Session = Depends(get_db)
):
    logger.info(f"创建服务: env_id={env_id}, name={svc_data.name}")
    try:
        service = EnvironmentService(db)
        result = service.create_service(env_id, svc_data)
        logger.info(f"服务创建成功: env_id={env_id}, name={svc_data.name}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建服务失败: env_id={env_id}, name={svc_data.name}, error={str(e)}")
        raise


@router.get("/{env_id}/services", response_model=ServiceListResponse)
def list_services(
    env_id: int,
    search: Optional[str] = Query(None, description="Search keyword for service name"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    logger.info(f"查询环境服务列表: env_id={env_id}, search={search}, page={page}")
    try:
        env_service = EnvironmentService(db)
        env = env_service.get_environment(env_id)
        if not env:
            logger.warning(f"环境不存在: env_id={env_id}")
            raise HTTPException(status_code=404, detail="Environment not found")
        items, total = env_service.get_services(env_id, search, page, page_size)
        logger.info(f"查询环境服务列表成功: env_id={env_id}, total={total}")
        return ServiceListResponse(
            items=[ServiceResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询环境服务列表失败: env_id={env_id}, error={str(e)}")
        raise


@router.get("/services/all", response_model=ServiceListResponse)
def list_all_services(
    search: Optional[str] = Query(None, description="Search keyword for service name"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=500, description="Page size"),
    db: Session = Depends(get_db)
):
    logger.info(f"查询所有服务: search={search}, page={page}")
    try:
        env_service = EnvironmentService(db)
        items, total = env_service.get_all_services(search, page, page_size)
        logger.info(f"查询所有服务成功: total={total}")
        return ServiceListResponse(
            items=[ServiceResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询所有服务失败: error={str(e)}")
        raise


@router.get("/services/{service_id}", response_model=ServiceResponse)
def get_service(
    service_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"查询服务详情: service_id={service_id}")
    try:
        service = EnvironmentService(db)
        svc = service.get_service(service_id)
        if not svc:
            logger.warning(f"服务不存在: service_id={service_id}")
            raise HTTPException(status_code=404, detail="Service not found")
        return svc
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询服务详情失败: service_id={service_id}, error={str(e)}")
        raise


@router.put("/services/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    svc_data: ServiceUpdate,
    db: Session = Depends(get_db)
):
    logger.info(f"更新服务: service_id={service_id}")
    try:
        service = EnvironmentService(db)
        result = service.update_service(service_id, svc_data)
        logger.info(f"服务更新成功: service_id={service_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新服务失败: service_id={service_id}, error={str(e)}")
        raise


@router.delete("/services/{service_id}", status_code=204)
def delete_service(
    service_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"删除服务: service_id={service_id}")
    try:
        service = EnvironmentService(db)
        service.delete_service(service_id)
        logger.info(f"服务删除成功: service_id={service_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除服务失败: service_id={service_id}, error={str(e)}")
        raise


@router.post("/services/{service_id}/copy", response_model=ServiceResponse, status_code=201)
def copy_service(
    service_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"复制服务: service_id={service_id}")
    try:
        service = EnvironmentService(db)
        result = service.copy_service(service_id)
        logger.info(f"服务复制成功: source_service_id={service_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"复制服务失败: service_id={service_id}, error={str(e)}")
        raise


@router.post("/services/{service_id}/servers", response_model=ServerResponse, status_code=201)
def create_server(
    service_id: int,
    server_data: ServerCreate,
    db: Session = Depends(get_db)
):
    logger.info(f"创建服务器: service_id={service_id}, name={server_data.name}")
    try:
        service = EnvironmentService(db)
        result = service.create_server(service_id, server_data)
        logger.info(f"服务器创建成功: service_id={service_id}, name={server_data.name}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建服务器失败: service_id={service_id}, name={server_data.name}, error={str(e)}")
        raise


@router.put("/servers/{server_id}", response_model=ServerResponse)
def update_server(
    server_id: int,
    server_data: ServerUpdate,
    db: Session = Depends(get_db)
):
    logger.info(f"更新服务器: server_id={server_id}")
    try:
        service = EnvironmentService(db)
        result = service.update_server(server_id, server_data)
        logger.info(f"服务器更新成功: server_id={server_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新服务器失败: server_id={server_id}, error={str(e)}")
        raise


@router.delete("/servers/{server_id}", status_code=204)
def delete_server(
    server_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"删除服务器: server_id={server_id}")
    try:
        service = EnvironmentService(db)
        service.delete_server(server_id)
        logger.info(f"服务器删除成功: server_id={server_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除服务器失败: server_id={server_id}, error={str(e)}")
        raise


@router.post("/services/{service_id}/databases", response_model=DatabaseResponse, status_code=201)
def create_database(
    service_id: int,
    db_data: DatabaseCreate,
    db: Session = Depends(get_db)
):
    logger.info(f"创建数据库: service_id={service_id}, name={db_data.name}")
    try:
        service = EnvironmentService(db)
        result = service.create_database(service_id, db_data)
        logger.info(f"数据库创建成功: service_id={service_id}, name={db_data.name}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建数据库失败: service_id={service_id}, name={db_data.name}, error={str(e)}")
        raise


@router.put("/databases/{db_id}", response_model=DatabaseResponse)
def update_database(
    db_id: int,
    db_data: DatabaseUpdate,
    db_session: Session = Depends(get_db)
):
    logger.info(f"更新数据库: db_id={db_id}")
    try:
        service = EnvironmentService(db_session)
        result = service.update_database(db_id, db_data)
        logger.info(f"数据库更新成功: db_id={db_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新数据库失败: db_id={db_id}, error={str(e)}")
        raise


@router.delete("/databases/{db_id}", status_code=204)
def delete_database(
    db_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"删除数据库: db_id={db_id}")
    try:
        service = EnvironmentService(db)
        service.delete_database(db_id)
        logger.info(f"数据库删除成功: db_id={db_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除数据库失败: db_id={db_id}, error={str(e)}")
        raise


@router.post("/{env_id}/variables", response_model=VariableResponse, status_code=201)
def create_variable(
    env_id: int,
    var_data: VariableCreate,
    db: Session = Depends(get_db)
):
    logger.info(f"创建变量: env_id={env_id}, name={var_data.name}")
    try:
        service = EnvironmentService(db)
        result = service.create_variable(env_id, var_data)
        logger.info(f"变量创建成功: env_id={env_id}, name={var_data.name}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建变量失败: env_id={env_id}, name={var_data.name}, error={str(e)}")
        raise


@router.get("/{env_id}/variables", response_model=list[VariableResponse])
def list_variables(
    env_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"查询变量列表: env_id={env_id}")
    try:
        env_service = EnvironmentService(db)
        env = env_service.get_environment(env_id)
        if not env:
            logger.warning(f"环境不存在: env_id={env_id}")
            raise HTTPException(status_code=404, detail="Environment not found")
        logger.info(f"查询变量列表成功: env_id={env_id}, count={len(env.variables)}")
        return env.variables
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询变量列表失败: env_id={env_id}, error={str(e)}")
        raise


@router.put("/variables/{var_id}", response_model=VariableResponse)
def update_variable(
    var_id: int,
    var_data: VariableUpdate,
    db: Session = Depends(get_db)
):
    logger.info(f"更新变量: var_id={var_id}")
    try:
        service = EnvironmentService(db)
        result = service.update_variable(var_id, var_data)
        logger.info(f"变量更新成功: var_id={var_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新变量失败: var_id={var_id}, error={str(e)}")
        raise


@router.delete("/variables/{var_id}", status_code=204)
def delete_variable(
    var_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"删除变量: var_id={var_id}")
    try:
        service = EnvironmentService(db)
        service.delete_variable(var_id)
        logger.info(f"变量删除成功: var_id={var_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除变量失败: var_id={var_id}, error={str(e)}")
        raise


@router.post("/resolve", response_model=VariableResolveResponse)
def resolve_variables(
    request: VariableResolveRequest,
    db: Session = Depends(get_db)
):
    logger.info(f"解析变量: environment_id={request.environment_id}, text_length={len(request.text) if request.text else 0}")
    try:
        resolver = VariableResolver(db)
        resolved_text, resolved_vars, unresolved = resolver.resolve(
            request.text,
            request.environment_id,
            request.case_variables,
            request.scenario_variables
        )
        logger.info(f"变量解析成功: environment_id={request.environment_id}, resolved={len(resolved_vars)}, unresolved={len(unresolved)}")
        return VariableResolveResponse(
            original_text=request.text,
            resolved_text=resolved_text,
            resolved_variables=resolved_vars,
            unresolved_variables=unresolved
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"变量解析失败: environment_id={request.environment_id}, error={str(e)}")
        raise
