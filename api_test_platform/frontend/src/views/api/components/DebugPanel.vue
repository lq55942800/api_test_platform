<template>
  <el-drawer
    v-model="visible"
    title="接口调试"
    :size="640"
    direction="rtl"
    :before-close="handleClose"
  >
    <template #header>
      <div class="debug-header">
        <span>接口调试</span>
        <MethodTag v-if="apiData" :method="apiData.method" />
        <span v-if="apiData" class="debug-api-name">{{ apiData.name }}</span>
      </div>
    </template>

    <div class="debug-panel" v-if="apiData">
      <div class="env-selector">
        <span class="label">环境：</span>
        <el-select v-model="environmentId" placeholder="选择环境" style="width: 150px">
          <el-option
            v-for="env in environments"
            :key="env.id"
            :label="env.name"
            :value="env.id"
          />
        </el-select>
        
        <span class="label" style="margin-left: 12px">服务：</span>
        <el-select v-model="serviceId" placeholder="选择服务" style="width: 180px" clearable>
          <el-option
            v-for="svc in filteredServices"
            :key="svc.id"
            :label="svc.name"
            :value="svc.id"
          />
        </el-select>
        
        <el-button
          type="primary"
          @click="handleSend"
          :loading="debugLoading"
          :disabled="!environmentId"
          class="send-btn"
        >
          发送请求
        </el-button>
      </div>

      <div class="request-section">
        <div class="section-title">请求</div>
        <div class="request-url">
          <MethodTag :method="apiData.method" />
          <span class="url-text">{{ apiData.path }}</span>
        </div>

        <el-tabs v-model="requestTab">
          <el-tab-pane label="Params" name="params">
            <ParamEditor v-model="debugPathParams" :show-type="false" />
          </el-tab-pane>
          <el-tab-pane label="Query" name="query">
            <ParamEditor v-model="debugQueryParams" :show-type="false" />
          </el-tab-pane>
          <el-tab-pane label="Headers" name="headers">
            <HeaderEditor v-model="debugHeaders" />
          </el-tab-pane>
          <el-tab-pane label="Body" name="body">
            <BodyEditor
              v-model:type="debugBodyType"
              v-model="debugBody"
            />
          </el-tab-pane>
          <el-tab-pane label="Cookie" name="cookie">
            <ParamEditor v-model="debugCookieParams" :show-type="false" />
          </el-tab-pane>
          <el-tab-pane label="前置操作" name="preAction">
            <PreActionEditor v-model="debugPreActions" />
          </el-tab-pane>
          <el-tab-pane label="后置操作" name="postAction">
            <PostActionEditor v-model="debugPostActions" />
          </el-tab-pane>
          <el-tab-pane label="断言" name="assertion">
            <AssertionEditor v-model="debugAssertions" />
          </el-tab-pane>
          <el-tab-pane label="超时设置" name="timeout">
            <TimeoutConfig v-model="debugTimeoutConfig" />
          </el-tab-pane>
        </el-tabs>
      </div>

      <div class="response-section">
        <div class="section-title">响应</div>
        <ResponseViewer :result="debugResult" />
      </div>

      <div class="action-result-section" v-if="debugResult?.pre_request_results && debugResult.pre_request_results.length > 0">
        <div class="section-title">前置操作结果</div>
        <ActionResultPanel :results="debugResult.pre_request_results" phase="pre_request" />
      </div>

      <div class="assertion-result-section" v-if="debugResult?.assertion_results && debugResult.assertion_results.length > 0">
        <div class="section-title">断言结果</div>
        <AssertionResultPanel :assertionResults="debugResult.assertion_results" :summary="debugResult.assertion_summary" />
      </div>

      <div class="action-result-section" v-if="debugResult?.post_request_results && debugResult.post_request_results.length > 0">
        <div class="section-title">后置操作结果</div>
        <ActionResultPanel :results="debugResult.post_request_results" phase="post_request" />
      </div>

      <div class="variables-section" v-if="debugResult?.variables_snapshot && Object.keys(debugResult.variables_snapshot).length > 0">
        <div class="section-title">变量快照</div>
        <el-table :data="variablesList" size="small" border>
          <el-table-column prop="name" label="变量名" width="180" />
          <el-table-column prop="value" label="值" />
          <el-table-column prop="scope" label="作用域" width="100" />
        </el-table>
      </div>

      <div class="history-section" v-if="recentHistories.length > 0">
        <div class="section-title">调试历史（最近5次）</div>
        <div class="history-list">
          <el-collapse v-model="expandedHistoryIds">
            <el-collapse-item 
              v-for="item in recentHistories" 
              :key="item.id" 
              :name="item.id"
            >
              <template #title>
                <div class="history-title">
                  <span class="history-time">{{ formatTime(item.created_at) }}</span>
                  <span class="history-status" :class="getStatusClass(item.response_status)">
                    {{ item.response_status || '-' }}
                  </span>
                  <span class="history-elapsed">{{ item.elapsed_ms ? item.elapsed_ms + 'ms' : '-' }}</span>
                  <span class="history-method">{{ item.request_method }}</span>
                </div>
              </template>
              
              <div class="history-detail">
                <div class="detail-row">
                  <span class="detail-label">请求URL：</span>
                  <span class="detail-value">{{ item.request_url }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">请求头：</span>
                  <pre class="detail-code">{{ formatHeaders(item.request_headers) }}</pre>
                </div>
                <div class="detail-row" v-if="item.request_body">
                  <span class="detail-label">请求体：</span>
                  <pre class="detail-code">{{ formatHistoryBody(item.request_body) }}</pre>
                </div>
                <div class="detail-row">
                  <span class="detail-label">响应头：</span>
                  <pre class="detail-code">{{ formatHeaders(item.response_headers) }}</pre>
                </div>
                <div class="detail-row" v-if="item.response_body">
                  <span class="detail-label">响应体：</span>
                  <pre class="detail-code">{{ formatHistoryBody(item.response_body) }}</pre>
                </div>
                <div class="detail-row" v-if="item.error_message">
                  <span class="detail-label">错误信息：</span>
                  <span class="detail-error">{{ item.error_message }}</span>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useDebugStore } from '@/stores/api'
import { useEnvironmentStore } from '@/stores/environment'
import { apiApi } from '@/api/api'
import { environmentApi } from '@/api/environment'
import MethodTag from './MethodTag.vue'
import ParamEditor from './ParamEditor.vue'
import HeaderEditor from './HeaderEditor.vue'
import BodyEditor from './BodyEditor.vue'
import ResponseViewer from './ResponseViewer.vue'
import AssertionResultPanel from './AssertionResultPanel.vue'
import ActionResultPanel from './ActionResultPanel.vue'
import PreActionEditor from './PreActionEditor.vue'
import PostActionEditor from './PostActionEditor.vue'
import AssertionEditor from './AssertionEditor.vue'
import TimeoutConfig from './TimeoutConfig.vue'
import type { ApiDefinition, ApiParam, DebugHistory } from '@/types/api'

const props = defineProps<{
  apiData: ApiDefinition | null
}>()

const debugStore = useDebugStore()
const envStore = useEnvironmentStore()

const visible = computed({
  get: () => debugStore.debugVisible,
  set: (val) => { if (!val) debugStore.closeDebug() }
})

const environments = computed(() => envStore.environments)
const debugResult = computed(() => debugStore.debugResult)
const debugLoading = computed(() => debugStore.debugLoading)
const debugHistories = computed(() => debugStore.debugHistories)

const variablesList = computed(() => {
  const snapshot = debugResult.value?.variables_snapshot
  if (!snapshot) return []
  return Object.entries(snapshot).map(([key, val]) => ({
    name: key,
    value: typeof val === 'object' ? JSON.stringify(val) : String(val),
    scope: ''
  }))
})

const environmentId = ref<number | null>(null)
const serviceId = ref<number | null>(null)
const allServices = ref<any[]>([])
const requestTab = ref('params')
const debugPathParams = ref<ApiParam[]>([])
const debugQueryParams = ref<ApiParam[]>([])
const debugHeaders = ref<ApiParam[]>([])
const debugBodyType = ref('none')
const debugBody = ref('')
const debugCookieParams = ref<ApiParam[]>([])
const debugPreActions = ref<any[]>([])
const debugPostActions = ref<any[]>([])
const debugAssertions = ref<any[]>([])
const debugTimeoutConfig = ref<any>({})
const expandedHistoryIds = ref<number[]>([])

const filteredServices = computed(() => {
  if (!environmentId.value) return []
  return allServices.value.filter(s => s.environment_id === environmentId.value)
})

const recentHistories = computed(() => {
  return debugHistories.value.slice(0, 5)
})

watch(() => props.apiData, (api) => {
  if (api) {
    debugPathParams.value = api.path_params ? JSON.parse(JSON.stringify(api.path_params)) : []
    debugQueryParams.value = api.query_params ? JSON.parse(JSON.stringify(api.query_params)) : []
    debugHeaders.value = api.header_params ? JSON.parse(JSON.stringify(api.header_params)) : []
    debugBodyType.value = api.body_type || 'none'
    // 确保body_definition是字符串
    if (api.body_definition) {
      debugBody.value = typeof api.body_definition === 'string' 
        ? api.body_definition 
        : JSON.stringify(api.body_definition, null, 2)
    } else {
      debugBody.value = ''
    }
    
    // 初始化新增参数
    debugCookieParams.value = api.cookie_params ? JSON.parse(JSON.stringify(api.cookie_params)) : []
    debugPreActions.value = api.pre_request_actions ? JSON.parse(JSON.stringify(api.pre_request_actions)) : []
    debugPostActions.value = api.post_request_actions ? JSON.parse(JSON.stringify(api.post_request_actions)) : []
    debugAssertions.value = api.assertions ? JSON.parse(JSON.stringify(api.assertions)) : []
    debugTimeoutConfig.value = {
      connect_timeout: api.connect_timeout,
      read_timeout: api.read_timeout,
      write_timeout: api.write_timeout,
      pool_timeout: api.pool_timeout,
      sample_timeout: api.sample_timeout,
      sql_timeout: api.sql_timeout,
      script_timeout: api.script_timeout,
      timeout_enabled: api.timeout_enabled
    }
    
    serviceId.value = api.service_id || null
    debugStore.fetchDebugHistories(api.id)
    
    // 设置默认环境和服务
    setDefaultEnvironmentAndService(api)
  }
}, { immediate: true })

function setDefaultEnvironmentAndService(api: ApiDefinition) {
  // 如果接口关联了服务，优先选择该服务所在的环境
  if (api.service_id && allServices.value.length > 0) {
    const service = allServices.value.find(s => s.id === api.service_id)
    if (service) {
      environmentId.value = service.environment_id
      serviceId.value = service.id
      return
    }
  }
  
  // 如果没有关联服务或找不到服务，使用默认环境
  if (!environmentId.value && envStore.environments.length > 0) {
    const defaultEnv = envStore.environments.find(e => e.is_default)
    environmentId.value = defaultEnv?.id || envStore.environments[0]?.id
  }
}

// 当服务列表加载完成后，重新设置默认环境和服务
watch(() => allServices.value, (services) => {
  if (services.length > 0 && props.apiData) {
    setDefaultEnvironmentAndService(props.apiData)
  }
}, { immediate: true })

watch(() => environmentId, (newEnvId) => {
  if (newEnvId && serviceId.value) {
    const service = allServices.value.find(s => s.id === serviceId.value)
    if (!service || service.environment_id !== newEnvId) {
      serviceId.value = null
    }
  }
})

watch(() => envStore.environments, (envs) => {
  if (envs.length > 0 && !environmentId.value) {
    const defaultEnv = envs.find(e => e.is_default)
    environmentId.value = defaultEnv?.id || envs[0]?.id
  }
}, { immediate: true })

if (envStore.environments.length === 0) {
  envStore.fetchEnvironments()
}

async function loadServices() {
  try {
    const res = await environmentApi.listAllServices({ page_size: 500 })
    allServices.value = res.items
  } catch (error) {
    console.error('Failed to load services:', error)
  }
}

loadServices()

function handleClose() {
  debugStore.closeDebug()
}

async function handleSend() {
  if (!props.apiData || !environmentId.value) return
  try {
    await debugStore.executeDebug(props.apiData.id, {
      environment_id: environmentId.value,
      service_id: serviceId.value,
      param_overrides: buildParamOverrides(),
      header_overrides: buildHeaderOverrides(),
      body_overrides: debugBody.value || null,
      body_type: debugBodyType.value || null,
      cookie_overrides: debugCookieParams.value.length > 0 ? debugCookieParams.value : null,
      pre_request_actions_overrides: debugPreActions.value.length > 0 ? debugPreActions.value : null,
      post_request_actions_overrides: debugPostActions.value.length > 0 ? debugPostActions.value : null,
      assertions_overrides: debugAssertions.value.length > 0 ? debugAssertions.value : null,
      timeout_config_overrides: debugTimeoutConfig.value && Object.keys(debugTimeoutConfig.value).length > 0 ? debugTimeoutConfig.value : null,
      timeout: 30
    })
    
    if (debugStore.debugResult?.error_message) {
      ElMessage.error(debugStore.debugResult.error_message)
    } else {
      ElMessage.success('请求完成')
    }
  } catch (error: any) {
    ElMessage.error(error.message || '请求失败')
  }
}

function buildParamOverrides() {
  const overrides: Record<string, any> = {}
  // 合并Path参数
  debugPathParams.value.forEach(p => {
    if (p.name && p.default_value) {
      overrides[p.name] = p.default_value
    }
  })
  // 合并Query参数
  debugQueryParams.value.forEach(p => {
    if (p.name && p.default_value) {
      overrides[p.name] = p.default_value
    }
  })
  return overrides
}

function buildHeaderOverrides() {
  const overrides: Record<string, any> = {}
  debugHeaders.value.forEach(p => {
    if (p.name && p.default_value) {
      overrides[p.name] = p.default_value
    }
  })
  return overrides
}

function handleHistoryClick(item: DebugHistory) {
  if (item.request_body) {
    try {
      debugBody.value = item.request_body
    } catch {
      debugBody.value = item.request_body
    }
  }
}

function formatTime(date: string) {
  if (!date) return ''
  const d = new Date(date)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
  if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'
  return d.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}

function getStatusClass(status?: number) {
  if (!status) return ''
  if (status >= 200 && status < 300) return 'status-success'
  if (status >= 400) return 'status-error'
  return ''
}

function formatHeaders(headers: string | null): string {
  if (!headers) return '无'
  try {
    const parsed = JSON.parse(headers)
    return JSON.stringify(parsed, null, 2)
  } catch {
    return headers
  }
}

function formatHistoryBody(body: string | null): string {
  if (!body) return '无'
  try {
    return JSON.stringify(JSON.parse(body), null, 2)
  } catch {
    return body
  }
}
</script>

<style scoped>
.debug-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.debug-api-name {
  color: #08060d;
}

.debug-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.env-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.env-selector .label {
  font-size: 14px;
  color: #6b6375;
}

.env-selector .send-btn {
  margin-left: auto;
}

.sub-label {
  font-size: 13px;
  font-weight: 500;
  color: #606266;
  margin-bottom: 8px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #08060d;
  margin-bottom: 8px;
}

.request-url {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding: 8px 12px;
  background-color: #f9fafb;
  border-radius: 6px;
  border: 1px solid #e5e4e7;
}

.url-text {
  font-family: ui-monospace, Consolas, monospace;
  font-size: 13px;
  color: #08060d;
  word-break: break-all;
}

.send-action {
  display: flex;
  justify-content: flex-end;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.history-title {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.history-method {
  font-family: ui-monospace, Consolas, monospace;
  font-weight: 600;
  color: #606266;
}

.history-time {
  color: #6b6375;
}

.history-status {
  font-weight: 600;
  font-family: ui-monospace, Consolas, monospace;
}

.status-success { color: #67C23A; }
.status-error { color: #F56C6C; }

.history-elapsed {
  color: #6b6375;
  font-family: ui-monospace, Consolas, monospace;
}

.history-detail {
  padding: 12px;
  background-color: #f9fafb;
  border-radius: 4px;
}

.detail-row {
  margin-bottom: 8px;
}

.detail-row:last-child {
  margin-bottom: 0;
}

.detail-label {
  font-weight: 600;
  color: #606266;
  margin-right: 8px;
}

.detail-value {
  font-family: ui-monospace, Consolas, monospace;
  word-break: break-all;
}

.detail-code {
  margin: 4px 0 0 0;
  padding: 8px;
  background-color: #fff;
  border: 1px solid #e5e4e7;
  border-radius: 4px;
  font-family: ui-monospace, Consolas, monospace;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow: auto;
}

.detail-error {
  color: #F56C6C;
}
</style>
