<template>
  <div class="step-detail-panel" :class="{ 'has-error': step.error_message || step.status === 'failed' || step.status === 'error' }">
    <div class="panel-top-bar" :class="{ 'error-bar': step.status === 'failed' || step.status === 'error' }">
      <div class="top-bar-left">
        <el-tag v-if="step.request_method || step.request_data?.method" :type="getMethodType(step.request_method || step.request_data?.method)" size="small" effect="dark">
          {{ (step.request_method || step.request_data?.method)?.toUpperCase() }}
        </el-tag>
        <span v-if="step.request_url || step.request_data?.url" class="top-bar-url">{{ step.request_url || step.request_data?.url }}</span>
      </div>
      <div class="top-bar-right">
        <el-tag v-if="step.response_status || step.response_data?.status_code" :type="(step.response_status || step.response_data?.status_code) < 400 ? 'success' : 'danger'" size="small" effect="dark">
          {{ step.response_status || step.response_data?.status_code }}
        </el-tag>
        <span v-if="step.duration || step.response_time" class="top-bar-duration">{{ step.duration || step.response_time }}ms</span>
      </div>
    </div>

    <div v-if="step.error_message" class="error-banner">
      <div class="error-banner-header" @click="errorExpanded = !errorExpanded">
        <div class="error-banner-left">
          <el-icon class="error-icon"><WarningFilled /></el-icon>
          <span class="error-title">执行失败</span>
          <el-tag type="danger" size="small" effect="light">{{ getErrorType(step.error_message) }}</el-tag>
        </div>
        <div class="error-banner-right">
          <span class="error-preview">{{ getErrorPreview(step.error_message) }}</span>
          <el-icon class="expand-icon" :class="{ 'is-expanded': errorExpanded }"><ArrowDown /></el-icon>
        </div>
      </div>
      <el-collapse-transition>
        <div v-show="errorExpanded" class="error-banner-body">
          <div class="error-detail-section">
            <div class="error-detail-label">错误类型</div>
            <div class="error-detail-value">{{ getErrorType(step.error_message) }}</div>
          </div>
          <div class="error-detail-section">
            <div class="error-detail-label">错误描述</div>
            <div class="error-detail-value">{{ step.error_message }}</div>
          </div>
          <div v-if="step.skip_reason" class="error-detail-section">
            <div class="error-detail-label">跳过原因</div>
            <div class="error-detail-value">{{ step.skip_reason }}</div>
          </div>
        </div>
      </el-collapse-transition>
    </div>

    <el-tabs v-model="activeTab" class="detail-tabs">
      <el-tab-pane label="请求/响应" name="requestResponse">
        <div class="req-res-container">
          <div class="req-res-split">
            <div class="req-res-half">
              <div class="half-title">请求信息</div>
              <div class="half-body">
                <el-descriptions :column="1" border size="small" v-if="step.request_data">
                  <el-descriptions-item label="请求方法">
                    <el-tag :type="getMethodType(step.request_data.method)" size="small" effect="dark">
                      {{ step.request_data.method?.toUpperCase() || '-' }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="请求URL">
                    <span class="url-text">{{ step.request_data.url || '-' }}</span>
                  </el-descriptions-item>
                </el-descriptions>
                <el-collapse v-model="reqExpanded" class="info-collapse">
                  <el-collapse-item v-if="step.request_data?.headers" name="req-headers">
                    <template #title>
                      <span class="collapse-title">请求头 <el-badge :value="Object.keys(step.request_data.headers).length" type="info" /></span>
                    </template>
                    <pre class="code-block">{{ JSON.stringify(step.request_data.headers, null, 2) }}</pre>
                  </el-collapse-item>
                  <el-collapse-item v-if="step.request_data?.params" name="req-params">
                    <template #title><span class="collapse-title">请求参数</span></template>
                    <pre class="code-block">{{ JSON.stringify(step.request_data.params, null, 2) }}</pre>
                  </el-collapse-item>
                  <el-collapse-item v-if="step.request_data?.body" name="req-body">
                    <template #title><span class="collapse-title">请求体</span></template>
                    <pre class="code-block">{{ formatBody(step.request_data.body) }}</pre>
                  </el-collapse-item>
                </el-collapse>
                <el-empty v-if="!step.request_data" description="无请求信息" :image-size="40" />
              </div>
            </div>
            <div class="req-res-divider" />
            <div class="req-res-half">
              <div class="half-title">响应信息</div>
              <div class="half-body">
                <el-descriptions :column="3" border size="small" v-if="step.response_data" class="response-stats">
                  <el-descriptions-item label="状态码">
                    <el-tag :type="step.response_data.status_code < 400 ? 'success' : 'danger'" size="small" effect="dark">
                      {{ step.response_data.status_code }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="耗时">
                    <span class="stat-value success">{{ step.duration || '-' }}ms</span>
                  </el-descriptions-item>
                  <el-descriptions-item label="大小">
                    {{ step.response_data.body ? `${(JSON.stringify(step.response_data.body).length / 1024).toFixed(2)}KB` : '-' }}
                  </el-descriptions-item>
                </el-descriptions>
                <el-collapse v-model="resExpanded" class="info-collapse">
                  <el-collapse-item v-if="step.response_data?.headers" name="res-headers">
                    <template #title>
                      <span class="collapse-title">响应头 <el-badge :value="Object.keys(step.response_data.headers).length" type="info" /></span>
                    </template>
                    <pre class="code-block">{{ JSON.stringify(step.response_data.headers, null, 2) }}</pre>
                  </el-collapse-item>
                  <el-collapse-item v-if="step.response_data?.body" name="res-body">
                    <template #title><span class="collapse-title">响应体</span></template>
                    <pre class="code-block">{{ formatBody(step.response_data.body) }}</pre>
                  </el-collapse-item>
                </el-collapse>
                <el-empty v-if="!step.response_data" description="无响应信息" :image-size="40" />
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane name="preActions">
        <template #label>
          <span>前置操作 <el-badge v-if="preActions.length" :value="preActions.length" type="primary" class="tab-badge" /></span>
        </template>
        <div v-if="preActions.length" class="actions-list">
          <div v-for="(action, idx) in preActions" :key="idx" class="action-item" :class="{ 'action-failed': action.success === false }">
            <div class="action-header">
              <div class="action-left">
                <span class="action-index">{{ idx + 1 }}</span>
                <el-tag size="small" :type="getActionTagType(action.type)" effect="plain">{{ getActionLabel(action.type) }}</el-tag>
                <el-tag v-if="action.success === false" type="danger" size="small" effect="light">失败</el-tag>
                <el-tag v-else type="success" size="small" effect="light">成功</el-tag>
              </div>
              <span class="action-duration">{{ action.duration ?? '-' }}ms</span>
            </div>
            <div class="action-body">
              <ActionDetailRenderer :action="action" />
            </div>
          </div>
        </div>
        <el-empty v-else description="无前置操作" :image-size="40" />
      </el-tab-pane>

      <el-tab-pane name="postActions">
        <template #label>
          <span>后置操作 <el-badge v-if="postActions.length" :value="postActions.length" type="primary" class="tab-badge" /></span>
        </template>
        <div v-if="postActions.length" class="actions-list">
          <div v-for="(action, idx) in postActions" :key="idx" class="action-item" :class="{ 'action-failed': action.success === false }">
            <div class="action-header">
              <div class="action-left">
                <span class="action-index post-index">{{ idx + 1 }}</span>
                <el-tag size="small" :type="getActionTagType(action.type)" effect="plain">{{ getActionLabel(action.type) }}</el-tag>
                <el-tag v-if="action.success === false" type="danger" size="small" effect="light">失败</el-tag>
                <el-tag v-else type="success" size="small" effect="light">成功</el-tag>
              </div>
              <span class="action-duration">{{ action.duration ?? '-' }}ms</span>
            </div>
            <div class="action-body">
              <ActionDetailRenderer :action="action" />
            </div>
          </div>
        </div>
        <el-empty v-else description="无后置操作" :image-size="40" />
      </el-tab-pane>

      <el-tab-pane name="assertions">
        <template #label>
          <span>断言 <el-badge v-if="assertionList.length" :value="assertionList.length" type="primary" class="tab-badge" /></span>
        </template>
        <div v-if="assertionList.length" class="assertion-list">
          <div v-for="(a, idx) in assertionList" :key="idx" class="assertion-item" :class="{ 'assertion-failed': !a.passed }">
            <div class="assertion-left">
              <el-icon :color="a.passed ? '#67c23a' : '#f56c6c'" :size="16">
                <CircleCheckFilled v-if="a.passed" />
                <CircleCloseFilled v-else />
              </el-icon>
              <span class="assertion-name">{{ a.name || `断言 ${idx + 1}` }}</span>
              <el-tag size="small" effect="plain">{{ a.type || '-' }}</el-tag>
            </div>
            <div class="assertion-right">
              <span class="assertion-expected">预期: <el-tag type="success" size="small" effect="light">{{ a.expected }}</el-tag></span>
              <span class="assertion-actual">实际: <el-tag :type="a.passed ? 'success' : 'danger'" size="small" effect="light">{{ a.actual }}</el-tag></span>
            </div>
          </div>
        </div>
        <el-empty v-else description="无断言信息" :image-size="40" />
      </el-tab-pane>

      <el-tab-pane v-if="step.error_message" label="错误信息" name="error">
        <el-alert type="error" :closable="false" show-icon>
          <pre class="error-text">{{ step.error_message }}</pre>
        </el-alert>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { CircleCheckFilled, CircleCloseFilled, WarningFilled, ArrowDown } from '@element-plus/icons-vue'
import type { StepExecutionRecord } from '@/types/testcase'
import ActionDetailRenderer from './ActionDetailRenderer.vue'

const ACTION_LABEL_MAP: Record<string, string> = {
  set_variable: '设置变量',
  wait: '等待',
  script: '脚本',
  database: '数据库',
  extract: '参数提取',
}

const ACTION_TAG_MAP: Record<string, string> = {
  set_variable: '',
  wait: 'info',
  script: 'warning',
  database: 'danger',
  extract: 'success',
}

const props = defineProps<{
  step: StepExecutionRecord
  defaultTab?: string
}>()

const activeTab = ref(props.defaultTab || 'requestResponse')
const reqExpanded = ref<string[]>([])
const resExpanded = ref<string[]>([])
const errorExpanded = ref(true)

const preActions = computed(() => {
  const raw = props.step.request_data?.pre_actions || props.step.pre_actions
  if (!raw) return []
  if (Array.isArray(raw)) return raw
  try { return JSON.parse(raw) } catch { return [] }
})

const postActions = computed(() => {
  const raw = props.step.request_data?.post_actions || props.step.post_actions
  if (!raw) return []
  if (Array.isArray(raw)) return raw
  try { return JSON.parse(raw) } catch { return [] }
})

const assertionList = computed(() => {
  const raw = props.step.request_data?.assertions || props.step.assertions
  if (!raw) return []
  if (Array.isArray(raw)) return raw
  try { return JSON.parse(raw) } catch { return [] }
})

function getMethodType(method: string) {
  const map: Record<string, string> = { GET: 'success', POST: '', PUT: 'warning', DELETE: 'danger', PATCH: 'info' }
  return map[method?.toUpperCase()] || 'info'
}

function getActionLabel(type: string) {
  return ACTION_LABEL_MAP[type] || type
}

function getActionTagType(type: string) {
  return ACTION_TAG_MAP[type] || ''
}

function formatBody(body: any) {
  if (typeof body === 'string') {
    try { return JSON.stringify(JSON.parse(body), null, 2) } catch { return body }
  }
  return JSON.stringify(body, null, 2)
}

function getErrorType(errorMessage: string): string {
  if (!errorMessage) return '未知错误'
  if (errorMessage.includes('timeout') || errorMessage.includes('Timeout')) return '超时错误'
  if (errorMessage.includes('connection') || errorMessage.includes('Connection')) return '连接错误'
  if (errorMessage.includes('DNS') || errorMessage.includes('dns')) return 'DNS解析错误'
  if (errorMessage.includes('SSL') || errorMessage.includes('certificate')) return 'SSL证书错误'
  if (errorMessage.includes('Assertion') || errorMessage.includes('assertion')) return '断言失败'
  if (errorMessage.includes('not found') || errorMessage.includes('Not found')) return '资源不存在'
  if (errorMessage.includes('401') || errorMessage.includes('Unauthorized')) return '认证失败'
  if (errorMessage.includes('403') || errorMessage.includes('Forbidden')) return '权限不足'
  if (errorMessage.includes('500') || errorMessage.includes('Internal Server Error')) return '服务器错误'
  return '执行错误'
}

function getErrorPreview(errorMessage: string): string {
  if (!errorMessage) return ''
  const maxLen = 60
  if (errorMessage.length <= maxLen) return errorMessage
  return errorMessage.substring(0, maxLen) + '...'
}
</script>

<style scoped>
.step-detail-panel { width: 100%; }
.step-detail-panel.has-error { border-left: 3px solid #f56c6c; }
.panel-top-bar { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #f5f7fa; border-radius: 6px; margin-bottom: 12px; }
.panel-top-bar.error-bar { background: #fef0f0; border: 1px solid #fbc4c4; }
.top-bar-left { display: flex; align-items: center; gap: 8px; }
.top-bar-url { font-family: ui-monospace, Consolas, monospace; font-size: 12px; color: #6145ff; word-break: break-all; }
.top-bar-right { display: flex; align-items: center; gap: 8px; }
.top-bar-duration { color: #909399; font-size: 12px; }

.error-banner { margin-bottom: 12px; border: 1px solid #fbc4c4; border-radius: 6px; overflow: hidden; background: #fef0f0; }
.error-banner-header { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: #fde2e2; cursor: pointer; user-select: none; }
.error-banner-header:hover { background: #fcd4d4; }
.error-banner-left { display: flex; align-items: center; gap: 8px; }
.error-icon { color: #f56c6c; font-size: 18px; }
.error-title { font-weight: 600; color: #f56c6c; font-size: 14px; }
.error-banner-right { display: flex; align-items: center; gap: 8px; }
.error-preview { color: #909399; font-size: 12px; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.expand-icon { color: #909399; transition: transform 0.2s; }
.expand-icon.is-expanded { transform: rotate(180deg); }
.error-banner-body { padding: 14px; background: #fff; border-top: 1px solid #fbc4c4; }
.error-detail-section { margin-bottom: 10px; }
.error-detail-section:last-child { margin-bottom: 0; }
.error-detail-label { font-size: 12px; color: #909399; margin-bottom: 4px; font-weight: 500; }
.error-detail-value { font-size: 13px; color: #303133; line-height: 1.5; word-break: break-all; }

.detail-tabs :deep(.el-tabs__header) { margin-bottom: 12px; }
.tab-badge { margin-left: 4px; }

.req-res-container { width: 100%; }
.req-res-split { display: flex; gap: 0; }
.req-res-half { flex: 1; min-width: 0; }
.req-res-divider { width: 1px; background: #e4e7ed; margin: 0 12px; }
.half-title { font-size: 13px; font-weight: 600; color: #303133; margin-bottom: 8px; padding: 6px 10px; background: #f5f7fa; border-radius: 4px; }
.half-body { padding: 0 4px; }

.url-text { font-family: ui-monospace, Consolas, monospace; font-size: 12px; color: #6145ff; word-break: break-all; }
.stat-value { font-weight: 600; color: #303133; }
.stat-value.success { color: #67c23a; }

.info-collapse { margin-top: 8px; border: none; }
.info-collapse :deep(.el-collapse-item__header) { background: #fafafa; padding: 0 12px; font-weight: 500; font-size: 13px; border-radius: 0; }
.info-collapse :deep(.el-collapse-item__wrap) { border: none; }
.info-collapse :deep(.el-collapse-item__content) { padding: 8px 12px; }
.collapse-title { font-size: 13px; }

.code-block { background: #f5f7fa; padding: 10px; border-radius: 4px; font-family: ui-monospace, Consolas, monospace; font-size: 12px; overflow-x: auto; margin: 0; white-space: pre-wrap; word-break: break-all; border: 1px solid #e4e7ed; line-height: 1.5; }

.actions-list { display: flex; flex-direction: column; gap: 8px; }
.action-item { background: #fafafa; border: 1px solid #e5e4e7; border-radius: 6px; overflow: hidden; }
.action-item:hover { border-color: #aa3bff; }
.action-failed { border-color: #f56c6c; }
.action-header { display: flex; justify-content: space-between; align-items: center; padding: 6px 12px; background: #f5f5f7; border-bottom: 1px solid #e5e4e7; }
.action-left { display: flex; align-items: center; gap: 6px; }
.action-index { width: 18px; height: 18px; border-radius: 50%; background: #409eff; color: #fff; font-size: 11px; font-weight: 600; display: flex; align-items: center; justify-content: center; }
.post-index { background: #67c23a; }
.action-duration { color: #909399; font-size: 12px; }
.action-body { padding: 10px 12px; }

.assertion-list { display: flex; flex-direction: column; gap: 6px; }
.assertion-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #fafafa; border: 1px solid #e5e4e7; border-radius: 6px; }
.assertion-failed { border-color: #f56c6c; background: #fef0f0; }
.assertion-left { display: flex; align-items: center; gap: 8px; }
.assertion-name { font-weight: 500; font-size: 13px; }
.assertion-right { display: flex; align-items: center; gap: 12px; font-size: 12px; }

.error-text { margin: 0; white-space: pre-wrap; word-break: break-all; font-family: ui-monospace, Consolas, monospace; font-size: 13px; }
</style>
