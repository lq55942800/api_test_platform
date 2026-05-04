<template>
  <div class="page-layout">
    <PageHeader
      title="测试用例管理"
      subtitle="管理测试用例，支持创建、编辑、执行和跨团队复制"
    />

    <ToolBar>
      <template #left>
        <el-button type="primary" class="btn-primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新建用例
        </el-button>
        <el-button class="btn-outline" @click="showImportDialog = true">
          <el-icon><Upload /></el-icon>
          批量导入
        </el-button>
      </template>

      <template #right>
        <el-input
          v-model="searchText"
          placeholder="搜索用例名称/描述"
          clearable
          class="search-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="filterStatus" placeholder="状态" clearable class="filter-select">
          <el-option label="启用" value="enabled" />
          <el-option label="禁用" value="disabled" />
        </el-select>
        <el-select v-model="filterPriority" placeholder="优先级" clearable class="filter-select">
          <el-option label="P0" value="P0" />
          <el-option label="P1" value="P1" />
          <el-option label="P2" value="P2" />
          <el-option label="P3" value="P3" />
        </el-select>
        <el-select v-model="filterModuleId" placeholder="模块" clearable class="filter-select">
          <el-option
            v-for="module in modules"
            :key="module.id"
            :label="module.name"
            :value="module.id"
          />
        </el-select>
      </template>
    </ToolBar>

    <DataTable
      :loading="loading"
      :data="testCases"
      :total="total"
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column type="index" label="序号" width="70" align="center" :index="indexMethod" />
      <el-table-column prop="name" label="用例名称" min-width="200">
        <template #default="{ row }">
          <div class="case-name">
            <el-tag :type="getPriorityType(row.priority)" size="small" class="priority-tag">
              {{ row.priority }}
            </el-tag>
            <span class="name-text" @click="handleView(row)">{{ row.name }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="module_id" label="所属模块" width="150">
        <template #default="{ row }">
          <span>{{ getModuleName(row.module_id) || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status === 'enabled' ? 'success' : 'info'" size="small">
            {{ row.status === 'enabled' ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="tags" label="标签" width="200">
        <template #default="{ row }">
          <div class="tags-cell">
            <el-tag
              v-for="tag in (row.tags || []).slice(0, 3)"
              :key="tag"
              size="small"
              class="tag-item"
            >
              {{ tag }}
            </el-tag>
            <span v-if="(row.tags || []).length > 3" class="more-tags">
              +{{ row.tags.length - 3 }}
            </span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="步骤数" width="100" align="center">
        <template #default="{ row }">
          <span>{{ row.steps?.length || 0 }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" sortable>
        <template #default="{ row }">
          <span class="time-text">{{ formatDate(row.created_at) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-tooltip content="查看" placement="top">
              <el-button type="primary" link size="small" @click="handleView(row)">
                <el-icon><View /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="编辑" placement="top">
              <el-button type="primary" link size="small" @click="handleEdit(row)">
                <el-icon><Edit /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="执行" placement="top">
              <el-button type="success" link size="small" @click="handleExecute(row)">
                <el-icon><VideoPlay /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="执行记录" placement="top">
              <el-button type="info" link size="small" @click="handleShowRecords(row)">
                <el-icon><Document /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="复制" placement="top">
              <el-button type="warning" link size="small" @click="handleCopy(row)">
                <el-icon><CopyDocument /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="删除" placement="top">
              <el-button type="danger" link size="small" @click="handleDelete(row)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-tooltip>
          </div>
        </template>
      </el-table-column>
    </DataTable>

    <!-- 执行对话框 -->
    <el-dialog
      v-model="showExecuteDialog"
      title="执行测试用例"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="executeForm" label-width="120px">
        <el-form-item label="选择环境" required>
          <el-select v-model="executeForm.environment_id" placeholder="请选择执行环境">
            <el-option
              v-for="env in environments"
              :key="env.id"
              :label="env.name"
              :value="env.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="失败策略">
          <el-radio-group v-model="executeForm.fail_strategy">
            <el-radio label="stop">遇到失败停止</el-radio>
            <el-radio label="continue">继续执行</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="保存记录">
          <el-switch v-model="executeForm.save_record" />
        </el-form-item>
        <el-form-item label="超时时间(秒)">
          <el-input-number v-model="executeForm.timeout" :min="10" :max="600" />
        </el-form-item>
        <el-form-item label="步骤间隔(毫秒)">
          <el-input-number v-model="executeForm.step_interval" :min="0" :max="10000" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showExecuteDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmExecute" :loading="executing">执行</el-button>
      </template>
    </el-dialog>

    <!-- 执行记录对话框 -->
    <el-dialog v-model="showRecordsDialog" title="执行记录" width="900px" top="5vh">
      <div v-if="executionRecords.length === 0 && !loadingRecords" class="empty-records">
        <el-empty description="暂无执行记录" />
      </div>
      <div v-else>
        <el-table :data="executionRecords" v-loading="loadingRecords" style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'passed' ? 'success' : row.status === 'failed' ? 'danger' : 'warning'" size="small">
                {{ row.status === 'passed' ? '通过' : row.status === 'failed' ? '失败' : row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="environment_name" label="环境" width="120" />
          <el-table-column label="步骤统计" width="150">
            <template #default="{ row }">
              {{ row.total_steps }} 步 / {{ row.passed_steps }} 通过 / {{ row.failed_steps }} 失败
            </template>
          </el-table-column>
          <el-table-column prop="duration" label="耗时" width="100">
            <template #default="{ row }">
              {{ row.duration ? `${row.duration}ms` : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="执行时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="viewRecordDetail(row)">查看详情</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="recordPagination.page"
            v-model:page-size="recordPagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="recordPagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleRecordPageChange"
            @current-change="handleRecordPageChange"
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="showRecordsDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 跨团队复制对话框 -->
    <el-dialog
      v-model="showCopyDialog"
      title="跨团队复制检查"
      width="700px"
      :close-on-click-modal="false"
    >
      <div v-if="copyCheckResult" class="copy-check-result">
        <el-alert
          v-if="!copyCheckResult.can_copy"
          title="无法复制"
          type="error"
          :closable="false"
          show-icon
        >
          <p>该用例无法复制到目标团队，请查看下方警告信息</p>
        </el-alert>

        <div v-if="copyCheckResult.warnings.length > 0" class="warnings-section">
          <h4>警告信息</h4>
          <el-alert
            v-for="(warning, index) in copyCheckResult.warnings"
            :key="index"
            :title="warning.message"
            :type="warning.type === 'error' ? 'error' : 'warning'"
            :closable="false"
            show-icon
          >
            <p>{{ warning.suggestion }}</p>
          </el-alert>
        </div>

        <div v-if="copyCheckResult.services_to_check.length > 0" class="services-section">
          <h4>服务检查</h4>
          <el-table :data="copyCheckResult.services_to_check" border>
            <el-table-column prop="source_service" label="源服务" />
            <el-table-column label="目标团队是否存在">
              <template #default="{ row }">
                <el-tag :type="row.target_exists ? 'success' : 'danger'">
                  {{ row.target_exists ? '存在' : '不存在' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div v-if="copyCheckResult.variables_to_check.length > 0" class="variables-section">
          <h4>需要检查的变量</h4>
          <el-tag
            v-for="variable in copyCheckResult.variables_to_check"
            :key="variable"
            class="variable-tag"
          >
            {{ variable }}
          </el-tag>
        </div>
      </div>
      <template #footer>
        <el-button @click="showCopyDialog = false">取消</el-button>
        <el-button
          v-if="copyCheckResult?.can_copy"
          type="primary"
          @click="confirmCopy"
          :loading="copying"
        >
          确认复制
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Upload, View, Edit, VideoPlay, Document, CopyDocument, Delete } from '@element-plus/icons-vue'
import { testCaseApi, testCaseModuleApi, executionApi, executeSSE } from '@/api/testcase'
import type { SSEStepEvent } from '@/api/testcase'
import { environmentApi } from '@/api/environment'
import type { TestCase, TestCaseModule, ExecuteRequest, CrossTeamCopyCheck, ExecutionRecord } from '@/types/testcase'
import type { Environment } from '@/types/environment'
import PageHeader from '@/components/common/PageHeader.vue'
import ToolBar from '@/components/common/ToolBar.vue'
import DataTable from '@/components/common/DataTable.vue'

const router = useRouter()

const loading = ref(false)
const executing = ref(false)
const copying = ref(false)
const searchText = ref('')
const filterStatus = ref('')
const filterPriority = ref('')
const filterModuleId = ref<number | null>(null)
const testCases = ref<TestCase[]>([])
const modules = ref<TestCaseModule[]>([])
const environments = ref<Environment[]>([])
const selectedCases = ref<TestCase[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const showExecuteDialog = ref(false)
const currentTestCase = ref<TestCase | null>(null)
const executeForm = ref<ExecuteRequest>({
  environment_id: 0,
  fail_strategy: 'stop',
  save_record: true,
  timeout: 300,
  step_interval: 0
})

const showCopyDialog = ref(false)
const copyCheckResult = ref<CrossTeamCopyCheck | null>(null)
const copyTestCaseId = ref<number>(0)
const copyTargetTeamId = ref<number>(0)

const showImportDialog = ref(false)

const showRecordsDialog = ref(false)
const loadingRecords = ref(false)
const executionRecords = ref<ExecutionRecord[]>([])
const currentRecordTestCase = ref<TestCase | null>(null)
const recordPagination = ref({
  page: 1,
  pageSize: 10,
  total: 0
})

function indexMethod(index: number) {
  return (currentPage.value - 1) * pageSize.value + index + 1
}

function getPriorityType(priority: string) {
  const typeMap: Record<string, any> = {
    P0: 'danger',
    P1: 'warning',
    P2: '',
    P3: 'info'
  }
  return typeMap[priority] || ''
}

function getModuleName(moduleId: number | null) {
  if (!moduleId) return ''
  const module = modules.value.find(m => m.id === moduleId)
  return module?.name || ''
}

function formatDate(date: string) {
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(async () => {
  await Promise.all([
    fetchTestCases(),
    fetchModules(),
    fetchEnvironments()
  ])
})

watch([currentPage, pageSize], () => {
  fetchTestCases()
})

let searchTimer: ReturnType<typeof setTimeout> | null = null
watch([searchText, filterStatus, filterPriority, filterModuleId], () => {
  currentPage.value = 1
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    fetchTestCases()
  }, 300)
})

async function fetchTestCases() {
  loading.value = true
  try {
    const data = await testCaseApi.list({
      status: filterStatus.value || undefined,
      priority: filterPriority.value || undefined,
      module_id: filterModuleId.value || undefined,
      keyword: searchText.value || undefined,
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    })
    testCases.value = data
    if (data.length < pageSize.value) {
      total.value = (currentPage.value - 1) * pageSize.value + data.length
    } else {
      total.value = currentPage.value * pageSize.value + 1
    }
  } catch (error) {
    console.error('获取测试用例列表失败:', error)
  } finally {
    loading.value = false
  }
}

async function fetchModules() {
  try {
    modules.value = await testCaseModuleApi.list()
  } catch (error) {
    console.error('获取模块列表失败:', error)
  }
}

async function fetchEnvironments() {
  try {
    const result = await environmentApi.list({ page_size: 100 })
    environments.value = result.items || []
  } catch (error) {
    console.error('获取环境列表失败:', error)
  }
}

function handleSelectionChange(selection: TestCase[]) {
  selectedCases.value = selection
}

function handleCreate() {
  router.push('/testcase/create')
}

function handleView(row: TestCase) {
  router.push(`/testcase/${row.id}`)
}

function handleEdit(row: TestCase) {
  router.push(`/testcase/${row.id}/edit`)
}

function handleExecute(row: TestCase) {
  currentTestCase.value = row
  if (!executeForm.value.environment_id && environments.value.length > 0) {
    const defaultEnv = environments.value.find((e: Environment) => e.is_default)
    executeForm.value.environment_id = defaultEnv?.id || environments.value[0].id
  }
  showExecuteDialog.value = true
}

async function confirmExecute() {
  if (!currentTestCase.value) return

  if (!executeForm.value.environment_id) {
    ElMessage.warning('请选择执行环境')
    return
  }

  executing.value = true
  showExecuteDialog.value = false
  executeSSE(
    currentTestCase.value.id,
    executeForm.value,
    (event: SSEStepEvent) => {
      if (event.type === 'started') {
        ElMessage.info('执行已启动')
      } else if (event.type === 'completed') {
        if (event.status === 'passed') {
          ElMessage.success('执行通过')
        } else {
          ElMessage.warning(`执行未通过：通过 ${event.passed_steps}/${event.total_steps} 步`)
        }
        fetchTestCases()
      } else if (event.type === 'error') {
        ElMessage.error(event.message || '执行失败')
      }
    },
    () => { executing.value = false },
    () => { executing.value = false }
  )
}

async function handleCopy(row: TestCase) {
  try {
    copyTestCaseId.value = row.id
    copyCheckResult.value = await testCaseApi.checkCopy(row.id, copyTargetTeamId.value)
    showCopyDialog.value = true
  } catch (error) {
    console.error('检查复制失败:', error)
  }
}

async function confirmCopy() {
  copying.value = true
  try {
    await testCaseApi.copyToTeam(copyTestCaseId.value, copyTargetTeamId.value)
    ElMessage.success('复制成功')
    showCopyDialog.value = false
    await fetchTestCases()
  } catch (error) {
    console.error('复制失败:', error)
  } finally {
    copying.value = false
  }
}

async function handleDelete(row: TestCase) {
  try {
    await ElMessageBox.confirm(
      `确定要删除测试用例"${row.name}"吗？删除后将无法恢复。`,
      '警告',
      { type: 'warning' }
    )
    await testCaseApi.delete(row.id)
    ElMessage.success('删除成功')
    await fetchTestCases()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

async function handleShowRecords(row: TestCase) {
  currentRecordTestCase.value = row
  recordPagination.value.page = 1
  recordPagination.value.total = 0
  showRecordsDialog.value = true
  await loadExecutionRecords()
}

async function loadExecutionRecords() {
  if (!currentRecordTestCase.value) return

  loadingRecords.value = true
  try {
    const result = await executionApi.list(currentRecordTestCase.value.id, {
      page: recordPagination.value.page,
      page_size: recordPagination.value.pageSize
    })
    executionRecords.value = result.items || result || []
    recordPagination.value.total = result.total || executionRecords.value.length
  } catch (error) {
    console.error('获取执行记录失败:', error)
    executionRecords.value = []
  } finally {
    loadingRecords.value = false
  }
}

function handleRecordPageChange() {
  loadExecutionRecords()
}

function viewRecordDetail(record: ExecutionRecord) {
  router.push(`/execution/${record.id}`)
}
</script>

<style scoped>
.page-layout {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0;
  min-height: 100%;
  background-color: var(--color-surface-200);
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #fff;
  background-color: var(--color-primary-500);
  border: 1px solid var(--color-primary-500);
  border-radius: 0.375rem;
  transition: all var(--transition-fast);
}

.btn-primary:hover {
  background-color: var(--color-primary-600);
  border-color: var(--color-primary-600);
}

.btn-outline {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-neutral-600);
  background-color: transparent;
  border: 1px solid var(--color-neutral-300);
  border-radius: 0.375rem;
  transition: all var(--transition-fast);
}

.btn-outline:hover {
  border-color: var(--color-primary-500);
  color: var(--color-primary-500);
}

.search-input {
  width: 300px;
}

.filter-select {
  width: 100px;
}

.case-name {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.priority-tag {
  flex-shrink: 0;
}

.name-text {
  font-weight: 500;
  color: var(--color-neutral-900);
  cursor: pointer;
}

.name-text:hover {
  color: var(--color-primary-500);
}

.tags-cell {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}

.tag-item {
  margin: 0;
}

.more-tags {
  color: var(--color-neutral-500);
  font-size: 12px;
}

.time-text {
  font-size: 13px;
  color: var(--color-neutral-500);
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 2px;
  flex-wrap: nowrap;
  white-space: nowrap;
}

.action-buttons :deep(.el-button) {
  padding: 4px;
  margin: 0;
}

.action-buttons :deep(.el-button + .el-button) {
  margin-left: 0;
}

.pagination-wrapper {
  padding: 1rem;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid var(--color-neutral-200);
  background-color: var(--color-surface-100);
}

.copy-check-result {
  max-height: 500px;
  overflow-y: auto;
}

.warnings-section,
.services-section,
.variables-section {
  margin-top: 1.25rem;
}

.warnings-section h4,
.services-section h4,
.variables-section h4 {
  margin-bottom: 0.75rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-neutral-900);
}

.warnings-section :deep(.el-alert) {
  margin-bottom: 0.5rem;
}

.variable-tag {
  margin-right: 0.5rem;
  margin-bottom: 0.5rem;
}

.empty-records {
  padding: 2rem;
  text-align: center;
}

@media (max-width: 1200px) {
  .search-input {
    width: 200px;
  }

  .filter-select {
    width: 80px;
  }
}

@media (max-width: 768px) {
  .page-layout {
    padding: 1rem;
  }

  .toolbar-container {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-left,
  .toolbar-right {
    flex-wrap: wrap;
  }

  .search-input {
    width: 100%;
  }

  .filter-select {
    flex: 1;
    min-width: 100px;
  }
}
</style>