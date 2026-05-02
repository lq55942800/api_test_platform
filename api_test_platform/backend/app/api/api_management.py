"""
接口管理API路由
"""
import json
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.session import get_db
from app.schemas.api import (
    ApiDefinitionCreate, ApiDefinitionUpdate, ApiDefinitionResponse,
    ApiDefinitionListResponse, UpdateStatusRequest,
    ApiModuleCreate, ApiModuleUpdate, ApiModuleResponse,
    ApiTagCreate, ApiTagResponse, ApiTagBatchRequest,
    ApiVersionResponse, ApiVersionListResponse, VersionCompareRequest,
    VersionDiffResponse, RollbackRequest,
    DebugRequest, DebugResultResponse, DebugHistoryResponse, DebugHistoryListResponse,
    ImportRequest, ImportResultResponse, ImportPreviewResponse,
    ExportRequest,
    AuditLogResponse, AuditLogListResponse,
    LockResultResponse,
    BatchDeleteRequest, BatchMoveRequest, BatchStatusRequest, BatchResultResponse,
    ReferenceListResponse, ReferenceInfo,
    NotificationResponse, NotificationListResponse,
    ExportFormat, ConflictStrategy,
)
from app.services.api_service import ApiService
from app.services.module_service import ModuleService
from app.services.tag_service import TagService
from app.services.version_service import VersionService
from app.services.debug_engine import DebugEngine
from app.services.import_engine import ImportEngine
from app.services.export_engine import ExportEngine
from app.services.audit_service import AuditService, AuditAction
from app.services.lock_service import LockService
from app.services.notify_service import NotifyService

from app.models.api import ChangeType, ApiDefinition

logger = get_logger(__name__)

router = APIRouter(tags=["API Management"])

# ==================== 接口定义 CRUD ====================

@router.post("/teams/{team_id}/apis", status_code=201)
def create_api(
    team_id: int,
    api_data: ApiDefinitionCreate,
    db: Session = Depends(get_db)
):
    logger.info(f"创建接口: team_id={team_id}, name={api_data.name}, method={api_data.method}, path={api_data.path}")
    try:
        api_data.team_id = team_id
        service = ApiService(db)
        api = service.create_api(api_data, user_id=0)

        audit = AuditService(db)
        audit.log(
            team_id=team_id, user_id=0, action=AuditAction.CREATE,
            api_id=api.id, resource_name=api.name,
            change_summary=f"创建接口: {api.name}"
        )

        version_svc = VersionService(db)
        snapshot = service.get_api_snapshot(api)
        version_svc.create_version(
            api_id=api.id, snapshot=snapshot,
            change_type=ChangeType.CREATE,
            change_summary=f"创建接口: {api.name}",
            user_id=0,
        )

        logger.info(f"接口创建成功: api_id={api.id}, name={api.name}")
        return _enrich_api_response(api, db)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建接口失败: team_id={team_id}, name={api_data.name}, error={str(e)}")
        raise


@router.get("/teams/{team_id}/apis")
def list_apis(
    team_id: int,
    module_id: Optional[int] = Query(None, description="模块ID筛选，0表示未分类"),
    method: Optional[str] = Query(None, description="HTTP方法筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    tag_id: Optional[int] = Query(None, description="标签ID筛选"),
    owner_id: Optional[int] = Query(None, description="责任人筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    logger.info(f"查询接口列表: team_id={team_id}, module_id={module_id}, method={method}, status={status}, keyword={keyword}, page={page}")
    try:
        service = ApiService(db)
        items, total = service.get_api_list(
            team_id, module_id, method, status, keyword, tag_id, owner_id, page, page_size
        )
        enriched = [_enrich_api_response(api, db) for api in items]
        logger.info(f"查询接口列表成功: team_id={team_id}, total={total}")
        return ApiDefinitionListResponse(items=enriched, total=total, page=page, page_size=page_size)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询接口列表失败: team_id={team_id}, error={str(e)}")
        raise


# ==================== 最近访问（必须在 /apis/{api_id} 之前注册） ====================

@router.get("/apis/recent")
def list_recent_visits(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    logger.info(f"查询最近访问接口: limit={limit}")
    try:
        from app.services.recent_visit_service import RecentVisitService
        service = RecentVisitService(db)
        apis = service.get_recent_visits(user_id=0, limit=limit)
        logger.info(f"查询最近访问接口成功: count={len(apis)}")
        return [_enrich_api_response(api, db) for api in apis]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询最近访问接口失败: error={str(e)}")
        raise


# ==================== 批量操作（必须在 /apis/{api_id} 之前注册） ====================

@router.post("/apis/batch-delete", response_model=BatchResultResponse)
def batch_delete(
    data: BatchDeleteRequest,
    db: Session = Depends(get_db)
):
    logger.info(f"批量删除接口: api_ids={data.api_ids}")
    try:
        service = ApiService(db)
        result = service.batch_delete(data.api_ids, user_id=0)
        logger.info(f"批量删除接口成功: result={result}")
        return BatchResultResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量删除接口失败: api_ids={data.api_ids}, error={str(e)}")
        raise


@router.post("/apis/batch-move", response_model=BatchResultResponse)
def batch_move(
    data: BatchMoveRequest,
    db: Session = Depends(get_db)
):
    logger.info(f"批量移动接口: api_ids={data.api_ids}, target_module_id={data.target_module_id}")
    try:
        service = ApiService(db)
        result = service.batch_move(data.api_ids, data.target_module_id, user_id=0)
        logger.info(f"批量移动接口成功: result={result}")
        return BatchResultResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量移动接口失败: api_ids={data.api_ids}, error={str(e)}")
        raise


@router.post("/apis/batch-status", response_model=BatchResultResponse)
def batch_status(
    data: BatchStatusRequest,
    db: Session = Depends(get_db)
):
    logger.info(f"批量变更接口状态: api_ids={data.api_ids}, status={data.status}")
    try:
        service = ApiService(db)
        result = service.batch_status(data.api_ids, data.status, user_id=0)
        logger.info(f"批量变更接口状态成功: result={result}")
        return BatchResultResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量变更接口状态失败: api_ids={data.api_ids}, error={str(e)}")
        raise


# ==================== 接口详情/更新/删除 ====================

@router.get("/apis/{api_id}")
def get_api(
    api_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"查询接口详情: api_id={api_id}")
    try:
        service = ApiService(db)
        api = service.get_api(api_id)
        if not api:
            logger.warning(f"接口不存在: api_id={api_id}")
            raise HTTPException(status_code=404, detail="接口不存在")
        return _enrich_api_response(api, db)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询接口详情失败: api_id={api_id}, error={str(e)}")
        raise


@router.put("/apis/{api_id}")
def update_api(
    api_id: int,
    api_data: ApiDefinitionUpdate,
    db: Session = Depends(get_db)
):
    logger.info(f"更新接口: api_id={api_id}")
    try:
        service = ApiService(db)
        old_api = service.get_api(api_id)
        old_snapshot = service.get_api_snapshot(old_api) if old_api else None

        api = service.update_api(api_id, api_data, user_id=0)
        new_snapshot = service.get_api_snapshot(api)

        version_svc = VersionService(db)
        if version_svc.should_create_version(api, new_snapshot):
            version_svc.create_version(
                api_id=api.id, snapshot=new_snapshot,
                change_type=ChangeType.UPDATE,
                change_summary=f"更新接口: {api.name}",
                user_id=0,
            )

        audit = AuditService(db)
        audit.log(
            team_id=api.team_id, user_id=0, action=AuditAction.UPDATE,
            api_id=api.id, resource_name=api.name,
            old_value=old_snapshot, new_value=new_snapshot,
            change_summary=f"更新接口: {api.name}"
        )

        logger.info(f"接口更新成功: api_id={api_id}, name={api.name}")
        return _enrich_api_response(api, db)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新接口失败: api_id={api_id}, error={str(e)}")
        raise


@router.delete("/apis/{api_id}", status_code=204)
def delete_api(
    api_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"删除接口: api_id={api_id}")
    try:
        service = ApiService(db)
        api = service.get_api(api_id)
        if not api:
            logger.warning(f"接口不存在: api_id={api_id}")
            raise HTTPException(status_code=404, detail="接口不存在")

        audit = AuditService(db)
        audit.log(
            team_id=api.team_id, user_id=0, action=AuditAction.DELETE,
            api_id=api.id, resource_name=api.name,
            change_summary=f"删除接口: {api.name}"
        )

        service.delete_api(api_id, user_id=0)
        logger.info(f"接口删除成功: api_id={api_id}, name={api.name}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除接口失败: api_id={api_id}, error={str(e)}")
        raise


@router.post("/apis/{api_id}/copy", status_code=201)
def copy_api(
    api_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"复制接口: api_id={api_id}")
    try:
        service = ApiService(db)
        api = service.copy_api(api_id, user_id=0)
        logger.info(f"接口复制成功: source_api_id={api_id}, new_api_id={api.id}")
        return _enrich_api_response(api, db)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"复制接口失败: api_id={api_id}, error={str(e)}")
        raise


@router.put("/apis/{api_id}/status")
def update_api_status(
    api_id: int,
    data: UpdateStatusRequest,
    db: Session = Depends(get_db)
):
    logger.info(f"变更接口状态: api_id={api_id}, status={data.status.value}")
    try:
        service = ApiService(db)
        api = service.update_status(api_id, data, user_id=0)

        audit = AuditService(db)
        audit.log(
            team_id=api.team_id, user_id=0, action=AuditAction.STATUS_CHANGE,
            api_id=api.id, resource_name=api.name,
            change_summary=f"状态变更为: {data.status.value}"
        )

        logger.info(f"接口状态变更成功: api_id={api_id}, status={data.status.value}")
        return _enrich_api_response(api, db)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"变更接口状态失败: api_id={api_id}, error={str(e)}")
        raise


# ==================== 接口调试 ====================

@router.post("/apis/{api_id}/debug", response_model=DebugResultResponse)
async def debug_api(
    api_id: int,
    data: DebugRequest,
    db: Session = Depends(get_db)
):
    logger.info(f"调试接口: api_id={api_id}, environment_id={data.environment_id}")
    try:
        engine = DebugEngine(db)
        result = await engine.execute(
            api_id=api_id,
            environment_id=data.environment_id,
            service_id=data.service_id,
            param_overrides=data.param_overrides,
            header_overrides=data.header_overrides,
            body_overrides=data.body_overrides,
            body_type=data.body_type,
            cookie_overrides=data.cookie_overrides,
            pre_request_actions_overrides=data.pre_request_actions_overrides,
            post_request_actions_overrides=data.post_request_actions_overrides,
            assertions_overrides=data.assertions_overrides,
            timeout_config_overrides=data.timeout_config_overrides,
            user_id=0,
        )

        audit = AuditService(db)
        api = db.query(ApiDefinition).filter(ApiDefinition.id == api_id).first()
        if api:
            audit.log(
                team_id=api.team_id, user_id=0, action=AuditAction.DEBUG,
                api_id=api_id, resource_name=api.name,
                change_summary=f"调试接口: {api.name}"
            )

        logger.info(f"接口调试完成: api_id={api_id}")
        return DebugResultResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"接口调试失败: api_id={api_id}, error={str(e)}")
        raise


@router.get("/apis/{api_id}/debug-histories", response_model=DebugHistoryListResponse)
def list_debug_histories(
    api_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    logger.info(f"查询调试历史: api_id={api_id}, page={page}")
    try:
        engine = DebugEngine(db)
        items, total = engine.get_debug_histories(api_id, page, page_size)
        logger.info(f"查询调试历史成功: api_id={api_id}, total={total}")
        return DebugHistoryListResponse(items=items, total=total, page=page, page_size=page_size)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询调试历史失败: api_id={api_id}, error={str(e)}")
        raise


# ==================== 版本管理 ====================

@router.get("/apis/{api_id}/versions", response_model=ApiVersionListResponse)
def list_versions(
    api_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    logger.info(f"查询版本列表: api_id={api_id}, page={page}")
    try:
        service = VersionService(db)
        items, total = service.get_versions(api_id, page, page_size)
        logger.info(f"查询版本列表成功: api_id={api_id}, total={total}")
        return ApiVersionListResponse(items=items, total=total, page=page, page_size=page_size)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询版本列表失败: api_id={api_id}, error={str(e)}")
        raise


@router.get("/apis/{api_id}/versions/compare", response_model=VersionDiffResponse)
def compare_versions(
    api_id: int,
    v1: int = Query(..., description="版本号1"),
    v2: int = Query(..., description="版本号2"),
    db: Session = Depends(get_db)
):
    logger.info(f"比较版本: api_id={api_id}, v1={v1}, v2={v2}")
    try:
        service = VersionService(db)
        result = service.compare_versions(api_id, v1, v2)
        logger.info(f"版本比较成功: api_id={api_id}, v1={v1}, v2={v2}")
        return VersionDiffResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"版本比较失败: api_id={api_id}, v1={v1}, v2={v2}, error={str(e)}")
        raise


@router.post("/apis/{api_id}/versions/rollback")
def rollback_version(
    api_id: int,
    data: RollbackRequest,
    db: Session = Depends(get_db)
):
    logger.info(f"回滚版本: api_id={api_id}, target_version={data.target_version}")
    try:
        service = VersionService(db)
        api = service.rollback(api_id, data.target_version, user_id=0)

        audit = AuditService(db)
        audit.log(
            team_id=api.team_id, user_id=0, action=AuditAction.ROLLBACK,
            api_id=api.id, resource_name=api.name,
            change_summary=f"回滚到版本v{data.target_version}"
        )

        logger.info(f"版本回滚成功: api_id={api_id}, target_version={data.target_version}")
        return _enrich_api_response(api, db)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"版本回滚失败: api_id={api_id}, target_version={data.target_version}, error={str(e)}")
        raise


# ==================== 编辑锁定 ====================

@router.post("/apis/{api_id}/lock", response_model=LockResultResponse)
def acquire_lock(
    api_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"获取编辑锁: api_id={api_id}")
    try:
        service = LockService(db)
        result = service.acquire_lock(api_id, user_id=0)
        logger.info(f"获取编辑锁完成: api_id={api_id}, result={result}")
        return LockResultResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取编辑锁失败: api_id={api_id}, error={str(e)}")
        raise


@router.delete("/apis/{api_id}/lock", status_code=204)
def release_lock(
    api_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"释放编辑锁: api_id={api_id}")
    try:
        service = LockService(db)
        service.release_lock(api_id, user_id=0)
        logger.info(f"释放编辑锁成功: api_id={api_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"释放编辑锁失败: api_id={api_id}, error={str(e)}")
        raise


# ==================== 模块管理 ====================

@router.get("/teams/{team_id}/api-modules", response_model=List[dict])
def list_modules(
    team_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"查询模块树: team_id={team_id}")
    try:
        service = ModuleService(db)
        result = service.get_module_tree(team_id)
        logger.info(f"查询模块树成功: team_id={team_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询模块树失败: team_id={team_id}, error={str(e)}")
        raise


@router.post("/teams/{team_id}/api-modules", response_model=ApiModuleResponse, status_code=201)
def create_module(
    team_id: int,
    data: ApiModuleCreate,
    db: Session = Depends(get_db)
):
    logger.info(f"创建模块: team_id={team_id}, name={data.name}")
    try:
        data.team_id = team_id
        service = ModuleService(db)
        result = service.create_module(data, user_id=0)
        logger.info(f"模块创建成功: team_id={team_id}, name={data.name}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建模块失败: team_id={team_id}, name={data.name}, error={str(e)}")
        raise


@router.put("/api-modules/{module_id}", response_model=ApiModuleResponse)
def update_module(
    module_id: int,
    data: ApiModuleUpdate,
    db: Session = Depends(get_db)
):
    logger.info(f"更新模块: module_id={module_id}")
    try:
        service = ModuleService(db)
        result = service.update_module(module_id, data, user_id=0)
        logger.info(f"模块更新成功: module_id={module_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新模块失败: module_id={module_id}, error={str(e)}")
        raise


@router.delete("/api-modules/{module_id}", status_code=204)
def delete_module(
    module_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"删除模块: module_id={module_id}")
    try:
        service = ModuleService(db)
        service.delete_module(module_id)
        logger.info(f"模块删除成功: module_id={module_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除模块失败: module_id={module_id}, error={str(e)}")
        raise


# ==================== 标签管理 ====================

@router.get("/teams/{team_id}/api-tags", response_model=List[ApiTagResponse])
def list_tags(
    team_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"查询标签列表: team_id={team_id}")
    try:
        service = TagService(db)
        result = service.get_tags_by_team(team_id)
        logger.info(f"查询标签列表成功: team_id={team_id}, count={len(result)}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询标签列表失败: team_id={team_id}, error={str(e)}")
        raise


@router.post("/teams/{team_id}/api-tags", response_model=ApiTagResponse, status_code=201)
def create_tag(
    team_id: int,
    data: ApiTagCreate,
    db: Session = Depends(get_db)
):
    logger.info(f"创建标签: team_id={team_id}, name={data.name}")
    try:
        data.team_id = team_id
        service = TagService(db)
        result = service.create_tag(data, user_id=0)
        logger.info(f"标签创建成功: team_id={team_id}, name={data.name}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建标签失败: team_id={team_id}, name={data.name}, error={str(e)}")
        raise


@router.delete("/api-tags/{tag_id}", status_code=204)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"删除标签: tag_id={tag_id}")
    try:
        service = TagService(db)
        service.delete_tag(tag_id)
        logger.info(f"标签删除成功: tag_id={tag_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除标签失败: tag_id={tag_id}, error={str(e)}")
        raise


@router.post("/apis/{api_id}/tags")
def set_api_tags(
    api_id: int,
    data: ApiTagBatchRequest,
    db: Session = Depends(get_db)
):
    logger.info(f"设置接口标签: api_id={api_id}, tag_ids={data.tag_ids}")
    try:
        service = TagService(db)
        service.set_api_tags(api_id, data.tag_ids)
        logger.info(f"接口标签设置成功: api_id={api_id}")
        return {"message": "标签设置成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"设置接口标签失败: api_id={api_id}, error={str(e)}")
        raise


# ==================== 导入导出 ====================

@router.post("/teams/{team_id}/apis/import/preview", response_model=ImportPreviewResponse)
def preview_import(
    team_id: int,
    data: ImportRequest,
    db: Session = Depends(get_db)
):
    logger.info(f"预览导入: team_id={team_id}, format={data.format}, import_type={data.import_type}")
    try:
        engine = ImportEngine(db)
        if data.import_type == "url" and data.url:
            content = engine.fetch_from_url(data.url)
        else:
            content = data.content
        result = engine.preview(
            content=content,
            team_id=team_id,
            format=data.format,
        )
        logger.info(f"预览导入成功: team_id={team_id}")
        return ImportPreviewResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"预览导入失败: team_id={team_id}, error={str(e)}")
        raise


@router.post("/teams/{team_id}/apis/import", response_model=ImportResultResponse)
def import_apis(
    team_id: int,
    data: ImportRequest,
    db: Session = Depends(get_db)
):
    logger.info(f"导入接口: team_id={team_id}, format={data.format}, import_type={data.import_type}")
    try:
        engine = ImportEngine(db)
        if data.import_type == "url" and data.url:
            content = engine.fetch_from_url(data.url)
        else:
            content = data.content
        result = engine.import_from_content(
            content=content,
            team_id=team_id,
            module_id=data.module_id,
            conflict_strategy=data.conflict_strategy.value,
            user_id=0,
            format=data.format,
        )

        audit = AuditService(db)
        audit.log(
            team_id=team_id, user_id=0, action=AuditAction.IMPORT,
            change_summary=f"导入接口: 成功{result['created']}个，跳过{result['skipped']}个，失败{result['failed']}个"
        )

        logger.info(f"接口导入成功: team_id={team_id}, created={result['created']}, skipped={result['skipped']}, failed={result['failed']}")
        return ImportResultResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导入接口失败: team_id={team_id}, error={str(e)}")
        raise


@router.post("/teams/{team_id}/apis/export")
def export_apis(
    team_id: int,
    data: ExportRequest,
    db: Session = Depends(get_db)
):
    logger.info(f"导出接口: team_id={team_id}, format={data.format.value}")
    try:
        engine = ExportEngine(db)
        result = engine.export(
            team_id=team_id,
            format=data.format,
            module_id=data.module_id,
            api_ids=data.api_ids,
            include_draft=data.include_draft,
            include_deprecated=data.include_deprecated,
            title=data.title,
            description=data.description,
        )

        audit = AuditService(db)
        audit.log(
            team_id=team_id, user_id=0, action=AuditAction.EXPORT,
            change_summary=f"导出接口: 格式{data.format.value}"
        )

        logger.info(f"接口导出成功: team_id={team_id}, format={data.format.value}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出接口失败: team_id={team_id}, error={str(e)}")
        raise


# ==================== 审计日志 ====================

@router.get("/apis/{api_id}/audit-logs", response_model=AuditLogListResponse)
def list_audit_logs(
    api_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    logger.info(f"查询审计日志: api_id={api_id}, page={page}")
    try:
        service = AuditService(db)
        api_svc = ApiService(db)
        api = api_svc.get_api(api_id)
        if not api:
            logger.warning(f"接口不存在: api_id={api_id}")
            raise HTTPException(status_code=404, detail="接口不存在")

        items, total = service.get_audit_logs(api.team_id, api_id=api_id, page=page, page_size=page_size)
        logger.info(f"查询审计日志成功: api_id={api_id}, total={total}")
        return AuditLogListResponse(items=items, total=total, page=page, page_size=page_size)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询审计日志失败: api_id={api_id}, error={str(e)}")
        raise


# ==================== 引用关系 ====================

@router.get("/apis/{api_id}/references", response_model=ReferenceListResponse)
def get_references(
    api_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"查询引用关系: api_id={api_id}")
    try:
        service = ApiService(db)
        api = service.get_api(api_id)
        if not api:
            logger.warning(f"接口不存在: api_id={api_id}")
            raise HTTPException(status_code=404, detail="接口不存在")

        references = []
        logger.info(f"查询引用关系成功: api_id={api_id}")
        return ReferenceListResponse(api_id=api_id, references=references, total=0)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询引用关系失败: api_id={api_id}, error={str(e)}")
        raise


# ==================== 通知 ====================

@router.get("/notifications", response_model=NotificationListResponse)
def list_notifications(
    is_read: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    logger.info(f"查询通知列表: is_read={is_read}, page={page}")
    try:
        service = NotifyService(db)
        items, total = service.get_user_notifications(user_id=0, is_read=is_read, page=page, page_size=page_size)
        logger.info(f"查询通知列表成功: total={total}")
        return NotificationListResponse(items=items, total=total, page=page, page_size=page_size)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询通知列表失败: error={str(e)}")
        raise


@router.put("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"标记通知已读: notification_id={notification_id}")
    try:
        service = NotifyService(db)
        service.mark_as_read(notification_id, user_id=0)
        logger.info(f"通知标记已读成功: notification_id={notification_id}")
        return {"message": "已标记为已读"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"标记通知已读失败: notification_id={notification_id}, error={str(e)}")
        raise


@router.put("/notifications/read-all")
def mark_all_notifications_read(
    db: Session = Depends(get_db)
):
    logger.info("标记所有通知已读")
    try:
        service = NotifyService(db)
        count = service.mark_all_as_read(user_id=0)
        logger.info(f"全部通知标记已读成功: count={count}")
        return {"message": f"已标记{count}条通知为已读"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"标记所有通知已读失败: error={str(e)}")
        raise


# ==================== 辅助函数 ====================

def _enrich_api_response(api, db: Session) -> dict:
    """丰富接口响应数据，添加标签信息和模块名称"""
    status_val = api.status.value if hasattr(api.status, 'value') else api.status
    body_type_val = api.body_type.value if hasattr(api.body_type, 'value') else api.body_type

    response_data = {
        "id": api.id,
        "team_id": api.team_id,
        "module_id": api.module_id,
        "service_id": api.service_id,
        "name": api.name,
        "method": api.method,
        "path": api.path,
        "description": api.description,
        "status": status_val,
        "protocol": api.protocol,
        "path_params": json.loads(api.path_params) if api.path_params else [],
        "query_params": json.loads(api.query_params) if api.query_params else [],
        "header_params": json.loads(api.header_params) if api.header_params else [],
        "cookie_params": json.loads(api.cookie_params) if api.cookie_params else [],
        "body_type": body_type_val,
        "body_definition": json.loads(api.body_definition) if api.body_definition else None,
        "responses": json.loads(api.responses) if api.responses else [],
        "pre_request_actions": json.loads(api.pre_request_actions) if api.pre_request_actions else [],
        "post_request_actions": json.loads(api.post_request_actions) if api.post_request_actions else [],
        "assertions": json.loads(api.assertions) if api.assertions else [],
        "connect_timeout": api.connect_timeout or 5000,
        "read_timeout": api.read_timeout or 30000,
        "write_timeout": api.write_timeout or 10000,
        "pool_timeout": api.pool_timeout or 5000,
        "sample_timeout": api.sample_timeout or 60000,
        "sql_timeout": api.sql_timeout or 30000,
        "script_timeout": api.script_timeout or 10000,
        "timeout_enabled": api.timeout_enabled if api.timeout_enabled is not None else True,
        "owner_id": api.owner_id,
        "lock_user_id": api.lock_user_id,
        "lock_time": api.lock_time,
        "last_debug_at": api.last_debug_at,
        "last_debug_status": api.last_debug_status,
        "reference_count": api.reference_count,
        "is_deleted": api.is_deleted,
        "created_by": api.created_by,
        "updated_by": api.updated_by,
        "created_at": api.created_at,
        "updated_at": api.updated_at,
        "tags": [],
        "module_name": None,
    }

    if not api.is_deleted:
        try:
            tag_svc = TagService(db)
            response_data["tags"] = tag_svc.get_api_tags(api.id)
        except Exception:
            pass

    if api.module_id:
        try:
            module_svc = ModuleService(db)
            module = module_svc.get_module(api.module_id)
            if module:
                response_data["module_name"] = module.name
        except Exception:
            pass

    return response_data
