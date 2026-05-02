<template>
  <div class="execution-report">
    <div class="report-header">
      <h3 class="report-title">执行记录</h3>
      <el-button type="primary" @click="refreshRecords" :loading="loading">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <div class="records-list">
      <el-table :data="records" v-loading="loading" stripe>
        <el-table-column type="index" label="序号" width="70" align="center" />
        <el-table-column prop="test_case_name" label="用例名称" min-width="200" />
        <el-table-column prop="environment_name" label="执行环境" width="150">
          <template #default="{ row }">
            <span>{{ row.environment_name || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="执行状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="步骤统计" width="150" align="center">
          <template #default="{ row }">
            <span class="step-stats">
              <span class="passed">{{ row.passed_steps }}</span>
              <span class="separator">/</span>
              <span class="total">{{ row.total_steps }}</span>
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="执行时长" width="120" align="center">
          <template #default="{ row }">
            <span>{{ formatDuration(row.duration) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="180">
          <template #default="{ row }">
            <span>{{ formatDate(row.start_time) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="executor_name" label="执行人" width="120">
          <template #default="{ row }">
            <span>{{ row.executor_name || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewDetail(row)">详情</el-button>
            <el-button type="primary" link @click="exportReport(row, 'html')">导出HTML</el-button>
            <el-button type="primary" link @click="exportReport(row, 'excel')">导出Excel</el-button>
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

    <el-dialog
      v-model="showStepDetailDialog"
      title="步骤执行详情"
      width="80%"
      :close-on-click-modal="false"
    >
      <div v-if="currentStep" class="step-detail-content">
        <StepDetailPanel :step="currentStep" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { executionApi } from '@/api/testcase'
import type { ExecutionRecord, StepExecutionRecord } from '@/types/testcase'
import StepDetailPanel from './StepDetailPanel.vue'

const router = useRouter()

interface Props {
  testCaseId?: number
}

const props = defineProps<Props>()

const loading = ref(false)
const records = ref<ExecutionRecord[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const showStepDetailDialog = ref(false)
const currentStep = ref<StepExecutionRecord | null>(null)

onMounted(async () => {
  if (props.testCaseId) {
    await fetchRecords()
  }
})

watch(() => props.testCaseId, async (newVal) => {
  if (newVal) {
    currentPage.value = 1
    await fetchRecords()
  }
})

watch([currentPage, pageSize], () => {
  if (props.testCaseId) {
    fetchRecords()
  }
})

async function fetchRecords() {
  if (!props.testCaseId) return
  loading.value = true
  try {
    const data = await executionApi.list(props.testCaseId, {
      page: currentPage.value,
      page_size: pageSize.value
    })
    records.value = data
    total.value = data.length
  } catch (error) {
    console.error('获取执行记录失败:', error)
  } finally {
    loading.value = false
  }
}

async function refreshRecords() {
  await fetchRecords()
  ElMessage.success('刷新成功')
}

function viewDetail(record: ExecutionRecord) {
  router.push(`/execution/${record.id}`)
}

async function exportReport(record: ExecutionRecord, format: 'html' | 'excel') {
  try {
    const blob = await executionApi.exportReport(record.id, format)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `test-report-${record.id}.${format === 'html' ? 'html' : 'xlsx'}`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出报告失败:', error)
  }
}

function getStatusType(status: string) {
  const typeMap: Record<string, string> = {
    pending: 'info',
    running: 'warning',
    passed: 'success',
    failed: 'danger',
    error: 'danger',
    skipped: 'info'
  }
  return typeMap[status] || 'info'
}

function getStatusText(status: string) {
  const textMap: Record<string, string> = {
    pending: '待执行',
    running: '执行中',
    passed: '通过',
    failed: '失败',
    error: '错误',
    skipped: '跳过'
  }
  return textMap[status] || status
}

function formatDate(date: string | null) {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

function formatDuration(duration: number | null) {
  if (!duration) return '-'
  if (duration < 1000) {
    return `${duration}ms`
  } else if (duration < 60000) {
    return `${(duration / 1000).toFixed(2)}s`
  } else {
    const minutes = Math.floor(duration / 60000)
    const seconds = ((duration % 60000) / 1000).toFixed(0)
    return `${minutes}m ${seconds}s`
  }
}
</script>

<style scoped>
.execution-report {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #e5e4e7;
}

.report-title {
  font-size: 16px;
  font-weight: 600;
  color: #08060d;
  margin: 0;
}

.report-title::before {
  content: '';
  width: 4px;
  height: 18px;
  background-color: #6145ff;
  border-radius: 2px;
  margin-right: 10px;
  display: inline-block;
  vertical-align: middle;
}

.records-list {
  padding: 24px;
}

.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.step-stats {
  display: flex;
  align-items: center;
  gap: 4px;
}

.step-stats .passed {
  color: #67c23a;
  font-weight: 600;
}

.step-stats .separator {
  color: #6b6375;
}

.step-stats .total {
  color: #08060d;
  font-weight: 600;
}

.step-detail-content {
  max-height: 70vh;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .records-list {
    padding: 16px;
  }

  .step-detail-content {
    max-height: 60vh;
  }
}
</style>
