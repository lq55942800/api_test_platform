<template>
  <el-drawer
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="编辑API步骤"
    size="800px"
    :close-on-click-modal="false"
    direction="rtl"
  >
    <div class="api-step-drawer">
      <el-form label-position="top" size="small">
        <el-form-item label="步骤名称">
          <el-input v-model="formData.step_name" placeholder="步骤名称" />
        </el-form-item>

        <el-form-item label="选择接口" required>
          <el-select
            v-model="formData.api_id"
            placeholder="请选择接口"
            filterable
            style="width: 100%"
            @change="onApiSelect"
          >
            <el-option
              v-for="api in apiList"
              :key="api.id"
              :label="`${api.method?.toUpperCase()} ${api.path} - ${api.name}`"
              :value="api.id"
            />
          </el-select>
        </el-form-item>

        <div v-if="selectedApiInfo" class="api-preview-panel">
          <div class="api-preview-title">接口信息预览</div>
          <div class="api-preview-grid">
            <div class="api-preview-item">
              <span class="label">请求方法</span>
              <MethodTag :method="selectedApiInfo.method" />
            </div>
            <div class="api-preview-item">
              <span class="label">请求路径</span>
              <span class="value">{{ selectedApiInfo.path }}</span>
            </div>
            <div v-if="serviceInfo" class="api-preview-item full-width">
              <span class="label">所属服务</span>
              <span class="value service-name">{{ serviceInfo.name }}</span>
            </div>
            <div v-if="serverInfo" class="api-preview-item full-width">
              <span class="label">服务器地址</span>
              <span class="value service-url">{{ serverInfo }}</span>
            </div>
          </div>
        </div>

        <el-tabs v-model="activeTab" class="drawer-tabs">
          <el-tab-pane label="Params" name="params">
            <ParamEditor v-model="formData.path_params" :show-type="false" />
          </el-tab-pane>
          <el-tab-pane label="Query" name="query">
            <ParamEditor v-model="formData.query_params" :show-type="false" />
          </el-tab-pane>
          <el-tab-pane label="Headers" name="headers">
            <HeaderEditor v-model="formData.header_params" />
          </el-tab-pane>
          <el-tab-pane label="Body" name="body">
            <BodyEditor
              v-model:type="formData.override_body_type"
              v-model="formData.override_body"
            />
          </el-tab-pane>
          <el-tab-pane label="Cookie" name="cookie">
            <ParamEditor v-model="formData.cookie_params" :show-type="false" />
          </el-tab-pane>
          <el-tab-pane label="前置操作" name="preAction">
            <PreActionEditor v-model="formData.pre_request_actions" />
          </el-tab-pane>
          <el-tab-pane label="后置操作" name="postAction">
            <PostActionEditor v-model="formData.post_request_actions" />
          </el-tab-pane>
          <el-tab-pane label="断言" name="assertion">
            <AssertionEditor v-model="formData.assertions" />
          </el-tab-pane>
          <el-tab-pane label="超时设置" name="timeout">
            <TimeoutConfigComponent v-model="formData.timeout_config_data" />
          </el-tab-pane>
        </el-tabs>
      </el-form>
    </div>

    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" @click="handleSave">确定</el-button>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, watch, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { apiApi } from '@/api/api'
import { environmentApi } from '@/api/environment'
import MethodTag from '@/views/api/components/MethodTag.vue'
import ParamEditor from '@/views/api/components/ParamEditor.vue'
import HeaderEditor from '@/views/api/components/HeaderEditor.vue'
import BodyEditor from '@/views/api/components/BodyEditor.vue'
import PreActionEditor from '@/views/api/components/PreActionEditor.vue'
import PostActionEditor from '@/views/api/components/PostActionEditor.vue'
import AssertionEditor from '@/views/api/components/AssertionEditor.vue'
import TimeoutConfigComponent from '@/views/api/components/TimeoutConfig.vue'
import type { TestCaseStep } from '@/types/testcase'
import type { ApiDefinition, ApiParam } from '@/types/api'
import type { Service } from '@/types/environment'

const props = defineProps<{
  modelValue: boolean
  step: TestCaseStep | null
  apiList: Array<any>
  environmentId?: number | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  save: [step: TestCaseStep]
}>()

const activeTab = ref('params')
const selectedApiInfo = ref<ApiDefinition | null>(null)
const allServices = ref<Service[]>([])

const serviceInfo = computed(() => {
  if (!selectedApiInfo.value?.service_id || !props.environmentId) return null
  const envServices = allServices.value.filter(s => s.environment_id === props.environmentId)
  return envServices.find(s => s.id === selectedApiInfo.value!.service_id) || null
})

const serverInfo = computed(() => {
  if (!serviceInfo.value?.servers?.length) return ''
  const server = serviceInfo.value.servers[0]
  const parts = []
  if (server.host) {
    const protocol = server.protocol || 'http'
    const port = server.port ? `:${server.port}` : ''
    parts.push(`${protocol}://${server.host}${port}`)
  }
  if (server.base_url) {
    parts.push(server.base_url)
  }
  return parts.join(' → ') || server.base_url || ''
})

const formData = reactive({
  step_name: '',
  api_id: null as number | null,
  enabled: true,
  path_params: [] as ApiParam[],
  query_params: [] as ApiParam[],
  header_params: [] as ApiParam[],
  cookie_params: [] as ApiParam[],
  override_body_type: 'none',
  override_body: '',
  override_headers: null as Record<string, any> | null,
  override_params: null as Record<string, any> | null,
  override_cookies: null as any[] | null,
  assertions: [] as any[],
  pre_request_actions: [] as any[],
  post_request_actions: [] as any[],
  timeout_config_data: {} as any
})

async function loadServices() {
  try {
    const res = await environmentApi.listAllServices({ page_size: 100 })
    allServices.value = res.items
  } catch {}
}

watch(() => props.modelValue, (val) => {
  if (val) {
    loadServices()
    if (props.step) {
      formData.step_name = props.step.step_name || ''
      formData.api_id = props.step.api_id || null
      formData.enabled = props.step.enabled
      formData.path_params = []
      formData.query_params = []
      formData.header_params = []
      formData.cookie_params = []
      formData.override_body_type = props.step.override_body_type || 'none'
      formData.override_body = props.step.override_body || ''
      formData.override_headers = props.step.override_headers || null
      formData.override_params = props.step.override_params || null
      formData.override_cookies = props.step.override_cookies || null
      formData.assertions = props.step.assertions ? [...props.step.assertions] : []
      formData.pre_request_actions = []
      formData.post_request_actions = []
      formData.timeout_config_data = props.step.timeout_config || {}

      if (props.step.override_params) {
        const params = props.step.override_params
        formData.query_params = Object.entries(params).map(([name, value]) => ({
          name,
          type: 'String',
          required: false,
          default_value: String(value),
          description: ''
        }))
      }
      if (props.step.override_headers) {
        const headers = props.step.override_headers
        formData.header_params = Object.entries(headers).map(([name, value]) => ({
          name,
          type: 'String',
          required: false,
          default_value: String(value),
          description: ''
        }))
      }

      if (props.step.override_cookies) {
        const cookies = props.step.override_cookies
        if (Array.isArray(cookies)) {
          formData.cookie_params = cookies.map((c: any) => {
            if (typeof c === 'object' && c.name !== undefined) return { ...c }
            return { name: String(c), type: 'String', required: false, default_value: '', description: '' }
          })
        }
      }

      if (props.step.pre_script) {
        try {
          const parsed = JSON.parse(props.step.pre_script)
          if (Array.isArray(parsed)) {
            formData.pre_request_actions = parsed
          }
        } catch {
          formData.pre_request_actions = []
        }
      }

      if (props.step.post_script) {
        try {
          const parsed = JSON.parse(props.step.post_script)
          if (Array.isArray(parsed)) {
            formData.post_request_actions = parsed
          }
        } catch {
          formData.post_request_actions = []
        }
      }

      if (props.step.extractors && Array.isArray(props.step.extractors)) {
        const extractActions = props.step.extractors.map((ext: any) => ({
          id: ext.id || Date.now().toString(36) + Math.random().toString(36).substr(2),
          enabled: ext.enabled !== false,
          name: ext.name || '参数提取',
          type: 'extract',
          phase: 'post_request',
          order: 0,
          config: ext.config || { extractors: [] },
          description: ''
        }))
        formData.post_request_actions = [...formData.post_request_actions, ...extractActions]
      }

      if (props.step.api_id) {
        const found = props.apiList.find((a: any) => a.id === props.step!.api_id)
        selectedApiInfo.value = found || null
      } else {
        selectedApiInfo.value = null
      }
    } else {
      formData.step_name = ''
      formData.api_id = null
      formData.enabled = true
      formData.path_params = []
      formData.query_params = []
      formData.header_params = []
      formData.cookie_params = []
      formData.override_body_type = 'none'
      formData.override_body = ''
      formData.override_headers = null
      formData.override_params = null
      formData.override_cookies = null
      formData.assertions = []
      formData.pre_request_actions = []
      formData.post_request_actions = []
      formData.timeout_config_data = {}
      selectedApiInfo.value = null
    }

    activeTab.value = 'params'
  }
})

async function onApiSelect(apiId: number) {
  try {
    const api = await apiApi.get(apiId)
    selectedApiInfo.value = api
    if (!formData.step_name) formData.step_name = api.name
    if (api.body_type && api.body_type !== 'none') {
      formData.override_body_type = api.body_type
    }
    if (api.header_params?.length) {
      formData.header_params = api.header_params.map((p: any) => ({ ...p }))
    }
    if (api.query_params?.length) {
      formData.query_params = api.query_params.map((p: any) => ({ ...p }))
    }
    if (api.path_params?.length) {
      formData.path_params = api.path_params.map((p: any) => ({ ...p }))
    }
    if (api.cookie_params?.length) {
      formData.cookie_params = api.cookie_params.map((p: any) => ({ ...p }))
    }
    if (api.body_definition && !formData.override_body) {
      try {
        const bodyDef = typeof api.body_definition === 'string' ? JSON.parse(api.body_definition) : api.body_definition
        if (bodyDef) formData.override_body = JSON.stringify(bodyDef, null, 2)
      } catch {}
    }
    if (api.pre_request_actions?.length) {
      try {
        const parsed = typeof api.pre_request_actions === 'string' ? JSON.parse(api.pre_request_actions) : api.pre_request_actions
        if (Array.isArray(parsed)) formData.pre_request_actions = parsed
      } catch {}
    }
    if (api.post_request_actions?.length) {
      try {
        const parsed = typeof api.post_request_actions === 'string' ? JSON.parse(api.post_request_actions) : api.post_request_actions
        if (Array.isArray(parsed)) formData.post_request_actions = parsed
      } catch {}
    }
    if (api.assertions?.length) {
      try {
        const parsed = typeof api.assertions === 'string' ? JSON.parse(api.assertions) : api.assertions
        if (Array.isArray(parsed)) formData.assertions = parsed
      } catch {}
    }
  } catch {
    const found = props.apiList.find((a: any) => a.id === apiId)
    selectedApiInfo.value = found || null
  }
}

function handleSave() {
  const overrideHeaders: Record<string, any> = {}
  formData.header_params.forEach((p: any) => {
    if (p.name) overrideHeaders[p.name] = p.default_value || ''
  })

  const overrideParams: Record<string, any> = {}
  formData.path_params.forEach((p: any) => {
    if (p.name) overrideParams[p.name] = p.default_value || ''
  })
  formData.query_params.forEach((p: any) => {
    if (p.name) overrideParams[p.name] = p.default_value || ''
  })

  const overrideCookies = formData.cookie_params.length > 0 ? formData.cookie_params : null

  const extractors = formData.post_request_actions
    .filter((a: any) => a.type === 'extract')
    .map((a: any) => ({
      id: a.id,
      name: a.name,
      enabled: a.enabled,
      config: a.config
    }))

  const nonExtractActions = formData.post_request_actions.filter((a: any) => a.type !== 'extract')

  const step: TestCaseStep = {
    step_type: 'api',
    api_id: formData.api_id,
    step_name: formData.step_name || null,
    enabled: formData.enabled,
    sort_order: props.step?.sort_order || 0,
    override_headers: Object.keys(overrideHeaders).length > 0 ? overrideHeaders : null,
    override_params: Object.keys(overrideParams).length > 0 ? overrideParams : null,
    override_body: formData.override_body || null,
    override_body_type: formData.override_body_type || null,
    override_cookies: overrideCookies,
    assertions: formData.assertions.length > 0 ? formData.assertions : null,
    extractors: extractors.length > 0 ? extractors : null,
    pre_script: formData.pre_request_actions.length > 0 ? JSON.stringify(formData.pre_request_actions) : null,
    post_script: nonExtractActions.length > 0 ? JSON.stringify(nonExtractActions) : null,
    timeout_config: formData.timeout_config_data.timeout_enabled ? formData.timeout_config_data : null,
    execution_condition: null,
    parent_step_id: props.step?.parent_step_id || null,
    children: props.step?.children || []
  }

  if (props.step?.id) step.id = props.step.id
  if (props.step?.test_case_id) step.test_case_id = props.step.test_case_id

  emit('save', step)
  emit('update:modelValue', false)
  ElMessage.success('步骤已保存')
}
</script>

<style scoped>
.api-step-drawer {
  padding: 0 4px;
}

.api-preview-panel {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  border: 1px solid #e5e4e7;
}

.api-preview-title {
  font-size: 13px;
  font-weight: 600;
  color: #08060d;
  margin-bottom: 12px;
}

.api-preview-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
}

.api-preview-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.api-preview-item.full-width {
  grid-column: 1 / -1;
}

.api-preview-item .label {
  color: #909399;
  white-space: nowrap;
}

.api-preview-item .value {
  color: #08060d;
  font-weight: 500;
}

.service-name {
  color: #6145ff;
  font-weight: 600;
}

.service-url {
  color: #aa3bff;
  word-break: break-all;
}

.drawer-tabs {
  margin-top: 16px;
}
</style>
