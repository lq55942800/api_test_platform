<template>
  <div class="execution-detail" v-loading="loading">
    <div class="breadcrumb-card">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/testcase' }">测试用例</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: `/testcase/${executionRecord?.test_case_id}` }">用例详情</el-breadcrumb-item>
        <el-breadcrumb-item>执行详情</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="detail-header">
      <div class="header-left">
        <el-button link @click="router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <el-tag :type="statusTagType" size="large" effect="dark" round>
          {{ statusText }}
        </el-tag>
        <h2 class="detail-title">执行详情 #{{ executionId }}</h2>
      </div>
      <div class="header-right">
        <span class="header-subtitle">{{ executionRecord?.test_case_name || '测试用例' }} · {{ formatTime(executionRecord?.start_time) }}</span>
        <el-button type="primary" @click="handleRetry" :loading="retrying">
          <el-icon><RefreshRight /></el-icon>
          重新执行
        </el-button>
      </div>
    </div>

    <div v-if="executionRecord" class="detail-content">
      <div class="section-card summary-card">
        <div class="section-title">执行概览</div>
        <div class="summary-grid">
          <div class="summary-stat">
            <div class="stat-label">总步骤</div>
            <div class="stat-value total">{{ executionRecord.total_steps }}</div>
          </div>
          <div class="summary-stat">
            <div class="stat-label">通过</div>
            <div class="stat-value success">{{ executionRecord.passed_steps }}</div>
          </div>
          <div class="summary-stat">
            <div class="stat-label">失败</div>
            <div class="stat-value danger">{{ executionRecord.failed_steps }}</div>
          </div>
          <div class="summary-stat">
            <div class="stat-label">跳过</div>
            <div class="stat-value warning">{{ executionRecord.skipped_steps || 0 }}</div>
          </div>
          <div class="summary-stat">
            <div class="stat-label">总耗时</div>
            <div class="stat-value">{{ executionRecord.duration ? `${(executionRecord.duration / 1000).toFixed(2)}s` : '-' }}</div>
          </div>
        </div>
        <div class="progress-bar-container">
          <el-progress
            :percentage="passRate"
            :color="passRate === 100 ? '#67c23a' : passRate >= 80 ? '#e6a23c' : '#f56c6c'"
            :stroke-width="12"
            :format="() => `${passRate}%`"
          />
        </div>
        <el-descriptions :column="3" border size="small" class="summary-desc">
          <el-descriptions-item label="执行环境">{{ executionRecord.environment_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatTime(executionRecord.start_time) }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{ formatTime(executionRecord.end_time) }}</el-descriptions-item>
        </el-descriptions>
        <el-alert v-if="executionRecord.error_message" type="error" :closable="false" show-icon class="error-alert">
          <template #title>错误信息</template>
          <div>{{ executionRecord.error_message }}</div>
        </el-alert>
      </div>

      <div class="section-card">
        <div class="section-title">
          执行步骤
          <el-badge :value="stepRecords.length" type="primary" style="margin-left: 8px" />
        </div>
        <div v-if="stepRecords.length === 0">
          <el-empty description="暂无执行步骤记录" />
        </div>
        <el-collapse v-else v-model="expandedSteps" class="step-collapse">
          <el-collapse-item
            v-for="(step, index) in stepRecords"
            :key="step.id"
            :name="step.id"
          >
            <template #title>
              <div class="step-header" :class="{ 'step-failed': step.status === 'failed' || step.status === 'error' }">
                <div class="step-left">
                  <el-tag round :type="getStepStatusType(step.status)" size="small" effect="dark">
                    {{ index + 1 }}
                  </el-tag>
                  <el-tag :type="getStepStatusType(step.status)" size="small">
                    {{ getStepStatusText(step.status) }}
                  </el-tag>
                  <span class="step-name">{{ step.step_name || step.api_name || `步骤 ${index + 1}` }}</span>
                  <el-tag v-if="step.status === 'skipped'" type="info" size="small" effect="plain">已跳过</el-tag>
                  <el-tag v-if="step.error_message" type="danger" size="small" effect="plain">
                    <el-icon><WarningFilled /></el-icon>
                    有错误
                  </el-tag>
                </div>
                <div class="step-right" @click.stop>
                  <span class="step-duration">{{ step.duration || step.response_time ? `${step.duration || step.response_time}ms` : '-' }}</span>
                  <el-button
                    v-if="step.status === 'failed' || step.status === 'error'"
                    type="primary"
                    link
                    size="small"
                    @click="handleRetryStep(step)"
                    :loading="retryingStepId === step.id"
                  >
                    <el-icon><RefreshRight /></el-icon>
                    重试
                  </el-button>
                </div>
              </div>
            </template>
            <StepDetailPanel :step="step" />
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, RefreshRight, WarningFilled } from '@element-plus/icons-vue'
import { executionApi, testCaseApi, executeSSE } from '@/api/testcase'
import type { SSEStepEvent } from '@/api/testcase'
import type { ExecutionRecord, StepExecutionRecord } from '@/types/testcase'
import StepDetailPanel from './components/StepDetailPanel.vue'

const router = useRouter()
const route = useRoute()

const executionId = computed(() => Number(route.params.id))
const loading = ref(false)
const retrying = ref(false)
const retryingStepId = ref<number | null>(null)
const executionRecord = ref<ExecutionRecord | null>(null)
const stepRecords = ref<StepExecutionRecord[]>([])
const expandedSteps = ref<number[]>([])
let pollTimer: ReturnType<typeof setInterval> | null = null

const passRate = computed(() => {
  if (!executionRecord.value || !executionRecord.value.total_steps) return 0
  return Math.round((executionRecord.value.passed_steps / executionRecord.value.total_steps) * 100)
})

const statusTagType = computed(() => {
  if (!executionRecord.value) return 'info'
  const map: Record<string, string> = { passed: 'success', failed: 'danger', running: 'warning', pending: 'info' }
  return map[executionRecord.value.status] || 'info'
})

const statusText = computed(() => {
  if (!executionRecord.value) return '-'
  const map: Record<string, string> = { passed: '通过', failed: '失败', running: '执行中', pending: '待执行' }
  return map[executionRecord.value.status] || executionRecord.value.status
})

function formatTime(time: string | null | undefined) {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

function getStepStatusType(status: string) {
  const map: Record<string, string> = { passed: 'success', failed: 'danger', skipped: 'warning', running: '', error: 'danger' }
  return map[status] || 'info'
}

function getStepStatusText(status: string) {
  const map: Record<string, string> = { passed: '通过', failed: '失败', skipped: '跳过', running: '执行中', error: '错误' }
  return map[status] || status
}

async function fetchExecutionDetail() {
  loading.value = true
  try {
    executionRecord.value = await executionApi.get(executionId.value)
    stepRecords.value = await executionApi.listStepExecutions(executionId.value)
  } catch (error) {
    console.error('获取执行详情失败:', error)
    ElMessage.error('获取执行详情失败')
  } finally {
    loading.value = false
  }
}

async function handleRetry() {
  if (!executionRecord.value) return
  retrying.value = true
  try {
    const testCaseId = executionRecord.value.test_case_id
    const environmentId = executionRecord.value.environment_id
    let newExecutionId: number | null = null
    executeSSE(
      testCaseId,
      {
        environment_id: environmentId,
        fail_strategy: 'stop',
        save_record: true,
        timeout: 300,
        step_interval: 0,
      },
      (event: SSEStepEvent) => {
        if (event.type === 'started' && event.execution_id) {
          newExecutionId = event.execution_id
          ElMessage.info('重新执行已启动')
        } else if (event.type === 'completed') {
          ElMessage.success(event.status === 'passed' ? '执行通过' : '执行未通过')
          if (newExecutionId) {
            router.replace(`/execution/${newExecutionId}`)
          } else {
            fetchExecutionDetail()
          }
        } else if (event.type === 'error') {
          ElMessage.error(event.message || '执行失败')
          fetchExecutionDetail()
        }
      },
      (error) => {
        console.error('SSE重新执行错误:', error)
        ElMessage.error('重新执行连接失败')
        retrying.value = false
      },
      () => {
        retrying.value = false
      }
    )
  } catch (error: any) {
    console.error('重新执行失败:', error)
    ElMessage.error('重新执行失败')
    retrying.value = false
  }
}

async function handleRetryStep(step: StepExecutionRecord) {
  if (!executionRecord.value || !step.api_id) {
    ElMessage.warning('无法重试：缺少接口信息')
    return
  }
  
  retryingStepId.value = step.id
  try {
    const res = await executionApi.retryStep(executionId.value, step.id)
    if (res.success) {
      ElMessage.success('步骤重试成功')
      await fetchExecutionDetail()
    } else {
      ElMessage.error(res.message || '步骤重试失败')
    }
  } catch (error: any) {
    console.error('步骤重试失败:', error)
    ElMessage.error(error.message || '步骤重试失败')
  } finally {
    retryingStepId.value = null
  }
}

function startPolling() {
  stopPolling()
  pollTimer = setInterval(async () => {
    if (executionRecord.value?.status === 'running') {
      try {
        executionRecord.value = await executionApi.get(executionId.value)
        stepRecords.value = await executionApi.listStepExecutions(executionId.value)
        if (executionRecord.value.status !== 'running') {
          stopPolling()
        }
      } catch {}
    }
  }, 3000)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

onMounted(() => {
  fetchExecutionDetail().then(() => {
    if (executionRecord.value?.status === 'running') {
      startPolling()
    }
  })
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.execution-detail { padding: 24px; background-color: #f5f5f5; min-height: 100vh; }
.breadcrumb-card { margin-bottom: 16px; padding: 12px 20px; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06); }
.detail-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; background-color: #ffffff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06); margin-bottom: 20px; border: 1px solid #eef2f7; }
.header-left { display: flex; align-items: center; gap: 12px; }
.detail-title { margin: 0; font-size: 20px; font-weight: 600; color: #08060d; }
.header-right { display: flex; align-items: center; gap: 16px; }
.header-subtitle { font-size: 14px; color: #6b6375; }
.detail-content { display: flex; flex-direction: column; gap: 20px; }
.section-card { background-color: #ffffff; border-radius: 12px; box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06); padding: 24px; }
.section-title { font-size: 16px; font-weight: 600; color: #1a1a2e; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 2px solid #eef2f7; display: flex; align-items: center; }
.section-title::before { content: ''; width: 4px; height: 18px; background-color: #6145ff; border-radius: 2px; margin-right: 10px; }

.summary-grid { display: flex; gap: 24px; margin-bottom: 16px; flex-wrap: wrap; }
.summary-stat { text-align: center; min-width: 80px; }
.stat-label { font-size: 12px; color: #909399; margin-bottom: 4px; }
.stat-value { font-size: 24px; font-weight: 700; color: #303133; }
.stat-value.total { color: #409eff; }
.stat-value.success { color: #67c23a; }
.stat-value.danger { color: #f56c6c; }
.stat-value.warning { color: #e6a23c; }

.progress-bar-container { margin-bottom: 16px; }
.summary-desc { margin-bottom: 16px; }
.error-alert { margin-top: 16px; }

.step-collapse { border: none; }
.step-collapse :deep(.el-collapse-item__header) { background-color: #fafafa; padding: 0 16px; border-radius: 0; height: auto; min-height: 48px; line-height: normal; padding-top: 8px; padding-bottom: 8px; }
.step-collapse :deep(.el-collapse-item__wrap) { border: none; border-top: 1px solid #e4e7ed; }
.step-collapse :deep(.el-collapse-item__content) { padding: 16px; }
.step-header { display: flex; justify-content: space-between; align-items: center; width: 100%; }
.step-header.step-failed { background: linear-gradient(90deg, #fef0f0 0%, #fafafa 100%); }
.step-left { display: flex; align-items: center; gap: 10px; }
.step-name { font-weight: 500; color: #303133; }
.step-right { display: flex; align-items: center; gap: 16px; }
.step-duration { color: #909399; font-size: 13px; }
</style>
