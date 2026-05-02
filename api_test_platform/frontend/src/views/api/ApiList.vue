<template>
  <div class="api-list-page">
    <div class="left-panel">
      <ModuleTree @select="handleModuleSelect" />
      <div class="left-section" v-if="recentVisits.length > 0">
        <div class="section-header">
          <span class="section-icon">🕐</span>
          <span class="section-title">最近</span>
        </div>
        <div class="section-content">
          <div
            v-for="item in recentVisits"
            :key="item.id"
            class="fav-item"
            @click="handleGoDetail(item)"
          >
            <MethodTag :method="item.method" />
            <span class="item-name">{{ item.name }}</span>
            <span class="item-time">{{ formatTimeAgo(item.visited_at) }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="right-panel">
      <div class="page-header">
        <div class="header-content">
          <h1 class="page-title">接口管理</h1>
          <p class="page-subtitle">管理API接口资产，支持录入、导入、调试和版本管理</p>
        </div>
      </div>

      <div class="toolbar">
        <div class="toolbar-left">
          <el-button type="primary" class="primary-btn" @click="router.push('/apis/new')">
            <el-icon><Plus /></el-icon>
            新建接口
          </el-button>
          <el-button class="outline-btn" @click="showImportDialog = true">
            <el-icon><Upload /></el-icon>
            导入
          </el-button>
          <el-button class="outline-btn" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
        </div>
        <div class="toolbar-right">
          <el-input
            v-model="searchText"
            placeholder="搜索接口名称/路径"
            clearable
            class="search-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select v-model="filterMethod" placeholder="方法" clearable class="filter-select">
            <el-option v-for="m in HTTP_METHODS" :key="m.value" :label="m.label" :value="m.value" />
          </el-select>
          <el-select v-model="filterStatus" placeholder="状态" clearable class="filter-select">
            <el-option v-for="s in API_STATUSES" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
          <el-select v-model="filterTagId" placeholder="标签" clearable class="filter-select">
            <el-option v-for="t in tags" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </div>
      </div>

      <div class="batch-bar" v-if="selectedApis.length > 0">
        <span class="batch-info">已选择 {{ selectedApis.length }} 项</span>
        <el-button size="small" type="danger" plain @click="handleBatchDelete">批量删除</el-button>
        <el-button size="small" plain @click="showBatchMoveDialog = true">批量移动</el-button>
        <el-dropdown trigger="click" @command="handleBatchStatusCommand">
          <el-button size="small" plain>
            批量改状态<el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="enabled">启用</el-dropdown-item>
              <el-dropdown-item command="disabled">禁用</el-dropdown-item>
              <el-dropdown-item command="deprecated">废弃</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button size="small" plain @click="handleClearSelection">取消选择</el-button>
      </div>

      <div class="table-container">
        <el-table
          ref="tableRef"
          :data="apis"
          v-loading="loading"
          style="width: 100%"
          @selection-change="handleSelectionChange"
          :header-cell-style="{ backgroundColor: '#fafafa', fontWeight: 600 }"
        >
          <el-table-column type="selection" width="40" align="center" />
          <el-table-column label="方法" width="80" align="center">
            <template #default="{ row }">
              <MethodTag :method="row.method" />
            </template>
          </el-table-column>
          <el-table-column prop="name" label="接口名称" min-width="180">
            <template #default="{ row }">
              <span class="api-name" @click="handleGoDetail(row)">{{ row.name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="path" label="路径" min-width="280">
            <template #default="{ row }">
              <span class="api-path">{{ row.path }}</span>
            </template>
          </el-table-column>
          <el-table-column label="模块" width="120" align="center">
            <template #default="{ row }">
              <span class="module-name">{{ row.module_name || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="80" align="center">
            <template #default="{ row }">
              <StatusTag :status="row.status" />
            </template>
          </el-table-column>
          <el-table-column label="标签" width="150">
            <template #default="{ row }">
              <div class="tag-list">
                <el-tag
                  v-for="tag in parseTags(row.tags)"
                  :key="tag"
                  size="small"
                  class="api-tag"
                >{{ tag }}</el-tag>
                <span v-if="!parseTags(row.tags).length" class="no-tag">-</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="updated_at" label="更新时间" width="160" align="center">
            <template #default="{ row }">
              <span class="update-time">{{ formatDate(row.updated_at) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160" fixed="right" align="center">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="handleDebug(row)">
                <el-icon><VideoPlay /></el-icon>调试
              </el-button>
              <el-button type="primary" link size="small" @click="handleGoDetail(row)">
                <el-icon><Edit /></el-icon>编辑
              </el-button>
              <el-dropdown trigger="click" @command="(cmd: string) => handleMoreCommand(cmd, row)">
                <el-button type="primary" link size="small">
                  <el-icon><More /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="copy">
                      <el-icon><CopyDocument /></el-icon>复制
                    </el-dropdown-item>
                    <el-dropdown-item command="history">
                      <el-icon><Clock /></el-icon>版本历史
                    </el-dropdown-item>
                    <el-dropdown-item command="delete" divided>
                      <el-icon color="#F56C6C"><Delete /></el-icon><span style="color:#F56C6C">删除</span>
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            background
          />
        </div>
      </div>
    </div>

    <DebugPanel :api-data="debugApi" />

    <ImportDialog v-model="showImportDialog" @success="fetchApis" />

    <el-dialog
      v-model="showCreateDialog"
      title="新建接口"
      width="600px"
      :close-on-click-modal="false"
      class="create-dialog"
    >
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="80px">
        <el-form-item label="接口名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入接口名称" maxlength="100" show-word-limit />
        </el-form-item>
        <div class="method-path-row">
          <el-form-item label="请求方法" prop="method">
            <el-select v-model="createForm.method" placeholder="方法" style="width: 120px">
              <el-option v-for="m in HTTP_METHODS" :key="m.value" :label="m.label" :value="m.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="路径" prop="path" class="path-form-item">
            <el-input v-model="createForm.path" placeholder="/api/v1/resource" maxlength="255" />
          </el-form-item>
        </div>
        <el-form-item label="所属模块">
          <el-select v-model="createForm.module_id" placeholder="选择模块" clearable style="width: 100%">
            <el-option
              v-for="m in moduleStore.modules"
              :key="m.id"
              :label="m.name"
              :value="m.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="createForm.description" type="textarea" placeholder="请输入描述" :rows="2" maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="showBatchMoveDialog"
      title="批量移动"
      width="400px"
    >
      <el-form label-width="80px">
        <el-form-item label="目标模块">
          <el-select v-model="batchMoveModuleId" placeholder="选择模块" style="width: 100%">
            <el-option
              v-for="m in moduleStore.modules"
              :key="m.id"
              :label="m.name"
              :value="m.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBatchMoveDialog = false">取消</el-button>
        <el-button type="primary" @click="handleBatchMove" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <VersionPanel v-model="showVersionPanel" :api-id="versionApiId" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Upload, Download, VideoPlay, Edit, More, CopyDocument, Clock, Delete, ArrowDown } from '@element-plus/icons-vue'
import { useApiStore, useModuleStore, useDebugStore, useRecentStore, useTagStore } from '@/stores/api'
import { HTTP_METHODS, API_STATUSES, HttpMethod, ApiStatus } from '@/types/api'
import type { ApiDefinition, ApiDefinitionCreate } from '@/types/api'
import type { FormInstance, FormRules } from 'element-plus'
import ModuleTree from './components/ModuleTree.vue'
import MethodTag from './components/MethodTag.vue'
import StatusTag from './components/StatusTag.vue'
import DebugPanel from './components/DebugPanel.vue'
import ImportDialog from './ImportDialog.vue'
import VersionPanel from './VersionPanel.vue'

const router = useRouter()
const apiStore = useApiStore()
const moduleStore = useModuleStore()
const debugStore = useDebugStore()
const recentStore = useRecentStore()
const tagStore = useTagStore()

const loading = ref(false)
const submitting = ref(false)
const searchText = ref('')
const filterMethod = ref('')
const filterStatus = ref('')
const filterModuleId = ref<number | null>(null)
const filterTagId = ref<number | null>(null)
const currentPage = ref(1)
const pageSize = ref(20)
const selectedApis = ref<ApiDefinition[]>([])
const tableRef = ref<any>()
const showCreateDialog = ref(false)
const showImportDialog = ref(false)
const showBatchMoveDialog = ref(false)
const showVersionPanel = ref(false)
const batchMoveModuleId = ref<number | null>(null)
const debugApi = ref<ApiDefinition | null>(null)
const versionApiId = ref<number | null>(null)

const createFormRef = ref<FormInstance>()
const createForm = ref<ApiDefinitionCreate>({
  name: '',
  method: HttpMethod.GET,
  path: '',
  description: '',
  module_id: undefined
})

const createRules: FormRules = {
  name: [
    { required: true, message: '请输入接口名称', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  method: [
    { required: true, message: '请选择请求方法', trigger: 'change' }
  ],
  path: [
    { required: true, message: '请输入接口路径', trigger: 'blur' },
    { pattern: /^\//, message: '路径必须以 / 开头', trigger: 'blur' }
  ]
}

const apis = computed(() => apiStore.apis)
const total = computed(() => apiStore.total)
const recentVisits = computed(() => recentStore.recentVisits)
const tags = computed(() => tagStore.tags)

onMounted(async () => {
  await Promise.all([
    fetchApis(),
    recentStore.fetchRecentVisits(),
    tagStore.fetchTags()
  ])
})

watch([currentPage, pageSize], () => {
  fetchApis()
})

let searchTimer: ReturnType<typeof setTimeout> | null = null
watch(searchText, () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    fetchApis()
  }, 300)
})

watch([filterMethod, filterStatus, filterTagId], () => {
  currentPage.value = 1
  fetchApis()
})

async function fetchApis() {
  loading.value = true
  try {
    await apiStore.fetchApis({
      page: currentPage.value,
      page_size: pageSize.value,
      keyword: searchText.value || undefined,
      method: filterMethod.value || undefined,
      status: filterStatus.value || undefined,
      module_id: filterModuleId.value || undefined,
      tag_id: filterTagId.value || undefined
    })
  } finally {
    loading.value = false
  }
}

function handleModuleSelect(moduleId: number | null) {
  filterModuleId.value = moduleId
  currentPage.value = 1
  fetchApis()
}

function handleOpenCreateDialog() {
  createForm.value = {
    name: '',
    method: HttpMethod.GET,
    path: '',
    description: '',
    module_id: moduleStore.modules.length > 0 ? moduleStore.modules[0].id : undefined
  }
  showCreateDialog.value = true
}

function handleGoDetail(row: ApiDefinition) {
  router.push(`/apis/${row.id}`)
}

function handleDebug(row: ApiDefinition) {
  debugApi.value = row
  debugStore.openDebug(row.id)
}

function handleSelectionChange(selection: ApiDefinition[]) {
  selectedApis.value = selection
}

function handleClearSelection() {
  tableRef.value?.clearSelection()
  selectedApis.value = []
}

async function handleCreate() {
  const valid = await createFormRef.value?.validate()
  if (!valid) return

  submitting.value = true
  try {
    await apiStore.createApi(createForm.value)
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    createForm.value = { name: '', method: HttpMethod.GET, path: '', description: '', module_id: undefined }
    await Promise.all([fetchApis(), moduleStore.fetchModules()])
  } catch (error: any) {
  } finally {
    submitting.value = false
  }
}

async function handleMoreCommand(cmd: string, row: ApiDefinition) {
  if (cmd === 'copy') {
    try {
      await ElMessageBox.confirm(`确定要复制接口"${row.name}"吗？`, '提示', { type: 'info' })
      await apiStore.copyApi(row.id)
      ElMessage.success('复制成功')
      await Promise.all([fetchApis(), moduleStore.fetchModules()])
    } catch (error: any) {
      if (error !== 'cancel') { }
    }
  } else if (cmd === 'history') {
    versionApiId.value = row.id
    showVersionPanel.value = true
  } else if (cmd === 'delete') {
    try {
      await ElMessageBox.confirm(
        `确定删除接口"${row.name}"吗？此操作不可恢复。`,
        '警告',
        { type: 'warning', confirmButtonText: '确定删除', confirmButtonClass: 'el-button--danger' }
      )
      await apiStore.deleteApi(row.id)
      ElMessage.success('删除成功')
      await Promise.all([fetchApis(), moduleStore.fetchModules()])
    } catch (error: any) {
      if (error !== 'cancel') { }
    }
  }
}

async function handleBatchDelete() {
  try {
    await ElMessageBox.confirm(
      `确定删除选中的 ${selectedApis.value.length} 个接口？此操作不可恢复。`,
      '警告',
      { type: 'warning' }
    )
    const ids = selectedApis.value.map(a => a.id)
    const result = await apiStore.batchDeleteApis(ids)
    ElMessage.success(`成功删除 ${result.success} 个`)
    selectedApis.value = []
    await Promise.all([fetchApis(), moduleStore.fetchModules()])
  } catch (error: any) {
    if (error !== 'cancel') { }
  }
}

async function handleBatchMove() {
  if (!batchMoveModuleId.value) {
    ElMessage.warning('请选择目标模块')
    return
  }
  submitting.value = true
  try {
    const ids = selectedApis.value.map(a => a.id)
    const result = await apiStore.batchMoveApis(ids, batchMoveModuleId.value)
    ElMessage.success(`成功移动 ${result.success} 个`)
    showBatchMoveDialog.value = false
    selectedApis.value = []
    await Promise.all([fetchApis(), moduleStore.fetchModules()])
  } catch (error: any) {
  } finally {
    submitting.value = false
  }
}

async function handleBatchStatusCommand(status: string) {
  try {
    const ids = selectedApis.value.map(a => a.id)
    const result = await apiStore.batchUpdateStatus(ids, status)
    const statusLabel = { enabled: '启用', disabled: '禁用', deprecated: '废弃' }[status] || status
    ElMessage.success(`成功${statusLabel} ${result.success} 个`)
    selectedApis.value = []
    await fetchApis()
  } catch (error: any) {
  }
}

function handleExport() {
  ElMessage.info('导出功能开发中')
}

function parseTags(tags?: any): string[] {
  if (!tags) return []
  if (Array.isArray(tags)) {
    return tags.map(tag => {
      if (typeof tag === 'string') return tag
      if (typeof tag === 'object' && tag.name) return tag.name
      return ''
    }).filter(Boolean)
  }
  if (typeof tags === 'string') {
    try {
      const parsed = JSON.parse(tags)
      return parseTags(parsed)
    } catch {
      return tags.split(',').filter(Boolean)
    }
  }
  return []
}

function formatDate(date: string) {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

function formatTimeAgo(date: string) {
  if (!date) return ''
  const now = new Date()
  const d = new Date(date)
  const diff = now.getTime() - d.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  return `${d.getMonth() + 1}-${d.getDate()}`
}
</script>

<style scoped>
.api-list-page {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background-color: #f5f5f7;
}

.left-panel {
  width: 220px;
  min-width: 220px;
  background-color: #ffffff;
  border-right: 1px solid #e5e4e7;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow-y: auto;
}

.left-section {
  border-top: 1px solid #e5e4e7;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
  font-size: 13px;
  font-weight: 600;
  color: #6b6375;
}

.section-icon {
  font-size: 14px;
}

.section-title {
  flex: 1;
}

.section-content {
  padding: 0 8px 8px;
}

.fav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: background-color 0.2s;
}

.fav-item:hover {
  background-color: #f4f3ec;
}

.item-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #08060d;
}

.item-time {
  font-size: 11px;
  color: #C0C4CC;
  flex-shrink: 0;
}

.empty-hint {
  font-size: 12px;
  color: #C0C4CC;
  padding: 12px 8px;
  text-align: center;
}

.right-panel {
  flex: 1;
  min-width: 0;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.page-header {
  margin-bottom: 16px;
  flex-shrink: 0;
}

.header-content {
  padding: 16px 20px;
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #e5e4e7;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #08060d;
  margin: 0 0 8px 0;
  line-height: 32px;
}

.page-subtitle {
  font-size: 14px;
  color: #6b6375;
  margin: 0;
  line-height: 22px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding: 12px 16px;
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #e5e4e7;
  flex-shrink: 0;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-left {
  display: flex;
  gap: 8px;
}

.toolbar-left .el-button {
  padding: 8px 16px;
}

.toolbar-right {
  display: flex;
  gap: 8px;
  align-items: center;
}

.primary-btn {
  background-color: #aa3bff !important;
  border-color: #aa3bff !important;
}

.primary-btn:hover {
  background-color: #9333ea !important;
  border-color: #9333ea !important;
}

.outline-btn {
  border-color: #dcdfe6;
  color: #606266;
}

.outline-btn:hover {
  border-color: #aa3bff;
  color: #aa3bff;
}

.search-input {
  width: 280px;
  max-width: 100%;
}

.filter-select {
  width: 90px;
  min-width: 70px;
}

.batch-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  border-radius: 6px;
  margin-bottom: 12px;
  flex-shrink: 0;
  flex-wrap: wrap;
  box-shadow: 0 2px 6px rgba(102, 126, 234, 0.25);
}

.batch-info {
  font-size: 13px;
  font-weight: 500;
  padding-right: 12px;
  margin-right: 4px;
  border-right: 1px solid rgba(255, 255, 255, 0.25);
}

.batch-bar :deep(.el-button) {
  border-color: transparent;
  color: #ffffff;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  padding: 5px 12px;
  height: 28px;
  margin: 0;
}

.batch-bar :deep(.el-dropdown .el-button) {
  margin: 0;
}

.batch-bar :deep(.el-button:hover) {
  border-color: transparent;
  background-color: rgba(255, 255, 255, 0.35);
  color: #ffffff;
}

.batch-bar :deep(.el-button--danger) {
  background-color: #ef4444;
  border-color: transparent;
  color: #ffffff;
  margin: 0;
}

.batch-bar :deep(.el-button--danger:hover) {
  background-color: #dc2626;
  border-color: transparent;
  color: #ffffff;
}

.table-container {
  flex: 1;
  min-height: 0;
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #e5e4e7;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.table-container :deep(.el-table) {
  flex: 1;
}

.table-container :deep(.el-table__body-wrapper) {
  overflow-y: auto;
}

.table-container :deep(.el-table__cell .cell) {
  display: flex;
  align-items: center;
  gap: 4px;
}

.table-container :deep(.el-button + .el-button) {
  margin-left: 0;
}

.api-name {
  color: #08060d;
  cursor: pointer;
  font-weight: 500;
}

.api-name:hover {
  color: #aa3bff;
}

.api-path {
  font-family: ui-monospace, SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 13px;
  color: #6b6375;
}

.module-name {
  font-size: 13px;
  color: #606266;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.api-tag {
  font-size: 11px;
  background-color: #f4f3ec;
  color: #6b6375;
  border: none;
}

.no-tag {
  color: #C0C4CC;
}

.update-time {
  font-size: 13px;
  color: #909399;
}

.pagination-container {
  padding: 16px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #e5e4e7;
  background-color: #fafafa;
}

.method-path-row {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.method-path-row .el-form-item {
  margin-bottom: 18px;
}

.method-path-row .el-form-item:first-child {
  flex: none;
}

.method-path-row .path-form-item {
  flex: 1;
  min-width: 0;
}

.method-path-row .path-form-item :deep(.el-form-item__label) {
  padding-right: 8px;
}

.method-path-row .path-form-item :deep(.el-input) {
  width: 100%;
}

.create-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid #e5e4e7;
  padding-bottom: 16px;
}

@media (max-width: 1200px) {
  .search-input {
    width: 200px;
  }
  
  .filter-select {
    width: 80px;
  }
}

@media (max-width: 1024px) {
  .left-panel {
    display: none;
  }

  .toolbar {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .toolbar-left, .toolbar-right {
    flex-wrap: wrap;
  }

  .search-input {
    width: 100%;
  }
  
  .filter-select {
    flex: 1;
    min-width: 80px;
  }
}
</style>
