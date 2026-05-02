<template>
  <div class="testcase-list-page">
    <!-- 页面标题区域 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">测试用例管理</h1>
        <p class="page-subtitle">管理测试用例，支持创建、编辑、执行和跨团队复制</p>
      </div>
    </div>

    <!-- 工具栏区域 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" class="primary-btn" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新建用例
        </el-button>
        <el-button class="outline-btn" @click="showImportDialog = true">
          <el-icon><Upload /></el-icon>
          批量导入
        </el-button>
      </div>
      <div class="toolbar-right">
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
      </div>
    </div>

    <!-- 测试用例列表表格 -->
    <div class="table-container">
      <el-table
        :data="testCases"
        v-loading="loading"
        stripe
        style="width: 100%"
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
            <span>{{ formatDate(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
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
      </el-table>

      <!-- 分页 -->
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
        <div class="pagination-container">
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
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Upload, View, Edit, VideoPlay, Document, CopyDocument, Delete } from '@element-plus/icons-vue'
import { testCaseApi, testCaseModuleApi, executionApi } from '@/api/testcase'
import { environmentApi } from '@/api/environment'
import type { TestCase, TestCaseModule, ExecuteRequest, CrossTeamCopyCheck, ExecutionRecord } from '@/types/testcase'
import type { Environment } from '@/types/environment'

const router = useRouter()

// 状态
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

// 执行对话框
const showExecuteDialog = ref(false)
const currentTestCase = ref<TestCase | null>(null)
const executeForm = ref<ExecuteRequest>({
  environment_id: 0,
  fail_strategy: 'stop',
  save_record: true,
  timeout: 300,
  step_interval: 0
})

// 跨团队复制对话框
const showCopyDialog = ref(false)
const copyCheckResult = ref<CrossTeamCopyCheck | null>(null)
const copyTestCaseId = ref<number>(0)
const copyTargetTeamId = ref<number>(0)

// 导入对话框
const showImportDialog = ref(false)

// 执行记录对话框
const showRecordsDialog = ref(false)
const loadingRecords = ref(false)
const executionRecords = ref<ExecutionRecord[]>([])
const currentRecordTestCase = ref<TestCase | null>(null)
const recordPagination = ref({
  page: 1,
  pageSize: 10,
  total: 0
})

// 序号方法
function indexMethod(index: number) {
  return (currentPage.value - 1) * pageSize.value + index + 1
}

// 获取优先级标签类型
function getPriorityType(priority: string) {
  const typeMap: Record<string, any> = {
    P0: 'danger',
    P1: 'warning',
    P2: '',
    P3: 'info'
  }
  return typeMap[priority] || ''
}

// 获取模块名称
function getModuleName(moduleId: number | null) {
  if (!moduleId) return ''
  const module = modules.value.find(m => m.id === moduleId)
  return module?.name || ''
}

// 格式化日期
function formatDate(date: string) {
  return new Date(date).toLocaleString('zh-CN')
}

// 初始化
onMounted(async () => {
  await Promise.all([
    fetchTestCases(),
    fetchModules(),
    fetchEnvironments()
  ])
})

// 监听分页变化
watch([currentPage, pageSize], () => {
  fetchTestCases()
})

// 监听搜索和筛选变化
let searchTimer: ReturnType<typeof setTimeout> | null = null
watch([searchText, filterStatus, filterPriority, filterModuleId], () => {
  currentPage.value = 1
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    fetchTestCases()
  }, 300)
})

// 获取测试用例列表
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

// 获取模块列表
async function fetchModules() {
  try {
    modules.value = await testCaseModuleApi.list()
  } catch (error) {
    console.error('获取模块列表失败:', error)
  }
}

// 获取环境列表
async function fetchEnvironments() {
  try {
    const result = await environmentApi.list({ page_size: 100 })
    environments.value = result.items || []
  } catch (error) {
    console.error('获取环境列表失败:', error)
  }
}

// 选择变化
function handleSelectionChange(selection: TestCase[]) {
  selectedCases.value = selection
}

// 新建用例
function handleCreate() {
  router.push('/testcase/create')
}

// 查看用例
function handleView(row: TestCase) {
  router.push(`/testcase/${row.id}`)
}

// 编辑用例
function handleEdit(row: TestCase) {
  router.push(`/testcase/${row.id}/edit`)
}

// 执行用例
function handleExecute(row: TestCase) {
  currentTestCase.value = row
  if (!executeForm.value.environment_id && environments.value.length > 0) {
    const defaultEnv = environments.value.find((e: Environment) => e.is_default)
    executeForm.value.environment_id = defaultEnv?.id || environments.value[0].id
  }
  showExecuteDialog.value = true
}

// 确认执行
async function confirmExecute() {
  if (!currentTestCase.value) return

  if (!executeForm.value.environment_id) {
    ElMessage.warning('请选择执行环境')
    return
  }

  executing.value = true
  try {
    const result = await testCaseApi.execute(currentTestCase.value.id, executeForm.value)
    showExecuteDialog.value = false
    if (result.status === 'passed') {
      ElMessage.success('执行通过')
    } else if (result.status === 'failed') {
      ElMessage.warning(`执行未通过：通过 ${result.passed_steps}/${result.total_steps} 步`)
    } else {
      ElMessage.info(`执行状态: ${result.status}`)
    }
  } catch (error) {
    console.error('执行失败:', error)
  } finally {
    executing.value = false
  }
}

// 复制用例
async function handleCopy(row: TestCase) {
  try {
    // 先进行跨团队复制检查
    copyTestCaseId.value = row.id
    copyCheckResult.value = await testCaseApi.checkCopy(row.id, copyTargetTeamId.value)
    showCopyDialog.value = true
  } catch (error) {
    console.error('检查复制失败:', error)
  }
}

// 确认复制
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

// 删除用例
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

// 显示执行记录
async function handleShowRecords(row: TestCase) {
  currentRecordTestCase.value = row
  recordPagination.value.page = 1
  recordPagination.value.total = 0
  showRecordsDialog.value = true
  await loadExecutionRecords()
}

// 加载执行记录
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

// 分页变化
function handleRecordPageChange() {
  loadExecutionRecords()
}

// 查看执行记录详情
function viewRecordDetail(record: ExecutionRecord) {
  router.push(`/execution/${record.id}`)
}
</script>

<style scoped>
.testcase-list-page {
  padding: 24px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 4px;
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

/* 页面标题区域 */
.page-header {
  margin-bottom: 24px;
}

.header-content {
  padding: 24px;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #08060d;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #6b6375;
  margin: 0;
}

/* 工具栏区域 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px 24px;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.primary-btn {
  background-color: #6145ff;
  border-color: #6145ff;
}

.primary-btn:hover {
  background-color: #5035e0;
  border-color: #5035e0;
}

.outline-btn {
  border-color: #6145ff;
  color: #6145ff;
}

.outline-btn:hover {
  background-color: #f0ebff;
}

.search-input {
  width: 300px;
}

.filter-select {
  width: 120px;
}

/* 表格容器 */
.table-container {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* 分页容器 */
.pagination-container {
  padding: 16px;
  display: flex;
  justify-content: flex-end;
  background-color: #ffffff;
  border-top: 1px solid #e5e4e7;
}

/* 用例名称样式 */
.case-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.priority-tag {
  flex-shrink: 0;
}

.name-text {
  font-weight: 500;
  color: #08060d;
  cursor: pointer;
}

.name-text:hover {
  color: #6145ff;
}

/* 标签单元格 */
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
  color: #6b6375;
  font-size: 12px;
}

/* 跨团队复制检查结果 */
.copy-check-result {
  max-height: 500px;
  overflow-y: auto;
}

.warnings-section,
.services-section,
.variables-section {
  margin-top: 20px;
}

.warnings-section h4,
.services-section h4,
.variables-section h4 {
  margin-bottom: 12px;
  font-size: 16px;
  font-weight: 600;
  color: #08060d;
}

.warnings-section .el-alert {
  margin-bottom: 8px;
}

.variable-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-left,
  .toolbar-right {
    width: 100%;
  }

  .search-input {
    flex: 1;
  }
}

@media (max-width: 768px) {
  .testcase-list-page {
    padding: 16px;
  }

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
