<template>
  <div class="api-detail" v-loading="loading">
    <div class="breadcrumb">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/apis' }">接口管理</el-breadcrumb-item>
        <el-breadcrumb-item>{{ isNewApi ? '新建接口' : (currentApi?.name || '接口详情') }}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="detail-header" v-if="currentApi || isNewApi">
      <div class="header-left">
        <el-button link @click="router.push('/apis')">
          <el-icon><ArrowLeft /></el-icon>
          返回列表
        </el-button>
        <template v-if="currentApi">
          <MethodTag :method="currentApi.method" />
          <h2 class="api-title">{{ currentApi.name }}</h2>
        </template>
        <template v-else>
          <el-tag type="info" size="small">新建接口</el-tag>
        </template>
      </div>
      <div class="header-right">
        <template v-if="!isNewApi">
          <el-select
            v-model="currentStatus"
            size="small"
            style="width: 100px"
            @change="handleStatusChange"
          >
            <el-option v-for="s in API_STATUSES" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
          <el-button type="primary" size="small" @click="handleDebug">
            <el-icon><VideoPlay /></el-icon>
            调试
          </el-button>
        </template>
        <el-button type="primary" size="small" @click="handleSave" :loading="saving">
          {{ isNewApi ? '创建' : '保存' }}
        </el-button>
        <template v-if="!isNewApi">
          <el-dropdown trigger="click" @command="handleMoreCommand">
            <el-button size="small">
              <el-icon><More /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="copy">复制接口</el-dropdown-item>
                <el-dropdown-item command="version">版本历史</el-dropdown-item>
                <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
      </div>
    </div>

    <div class="detail-content" v-if="currentApi || isNewApi">
      <div class="section-card">
        <div class="section-title">基本信息</div>
        <el-form :model="formData" label-width="80px" label-position="left" :rules="formRules" ref="formRef">
          <el-row :gutter="24">
            <el-col :span="8">
              <el-form-item label="所属模块" prop="module_id">
                <el-select v-model="formData.module_id" placeholder="选择模块" style="width: 100%">
                  <el-option
                    v-for="m in moduleStore.modules"
                    :key="m.id"
                    :label="m.name"
                    :value="m.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="环境" prop="environment_id">
                <el-select v-model="formData.environment_id" placeholder="选择环境" style="width: 100%" @change="handleEnvironmentChange">
                  <el-option
                    v-for="e in environments"
                    :key="e.id"
                    :label="e.name"
                    :value="e.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="关联服务" prop="service_id">
                <el-select v-model="formData.service_id" placeholder="选择服务" style="width: 100%">
                  <el-option
                    v-for="s in filteredServices"
                    :key="s.id"
                    :label="s.name"
                    :value="s.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="24">
            <el-col :span="8">
              <el-form-item label="接口名称" prop="name">
                <el-input v-model="formData.name" placeholder="接口名称" maxlength="100" />
              </el-form-item>
            </el-col>
            <el-col :span="4">
              <el-form-item label="请求方法">
                <el-select v-model="formData.method" style="width: 100%">
                  <el-option v-for="m in HTTP_METHODS" :key="m.value" :label="m.label" :value="m.value" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="路径">
                <el-input v-model="formData.path" placeholder="/api/v1/resource" maxlength="255" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="24">
            <el-col :span="24">
              <el-form-item label="描述">
                <el-input v-model="formData.description" placeholder="接口描述" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="标签">
            <TagInput v-model="formDataTags" />
          </el-form-item>
        </el-form>
      </div>

      <div class="section-card">
        <div class="section-title">请求定义</div>
        <el-tabs v-model="requestTab">
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
              v-model:type="formData.body_type"
              v-model="formData.body_definition"
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
            <TimeoutConfigComponent v-model="timeoutConfigData" />
          </el-tab-pane>
        </el-tabs>
      </div>

      <div class="section-card" v-if="currentApi">
        <div class="section-title">关联信息</div>
        <div class="info-row">
          <span class="info-label">引用该接口的用例：</span>
          <span class="info-value">{{ currentApi.reference_count || 0 }} 个</span>
        </div>
        <div class="info-row" v-if="currentApi.last_debug_at">
          <span class="info-label">最近调试：</span>
          <span class="info-value">{{ formatDate(currentApi.last_debug_at) }} {{ currentApi.last_debug_status }}</span>
        </div>
      </div>
    </div>

    <DebugPanel v-if="currentApi" :api-data="currentApi" />

    <VersionPanel
      v-if="currentApi && showVersionPanel"
      v-model="showVersionPanel"
      :api-id="currentApi ? currentApi.id : undefined"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, VideoPlay, More } from '@element-plus/icons-vue'
import { useApiStore, useModuleStore, useDebugStore, useVersionStore, useTagStore } from '@/stores/api'
import { HTTP_METHODS, API_STATUSES, HttpMethod, BodyType } from '@/types/api'
import type { ApiDefinitionUpdate, ApiParam, ApiResponse, PreRequestAction, PostRequestAction, Assertion, TimeoutConfig } from '@/types/api'
import type { Service } from '@/types/environment'
import { environmentApi } from '@/api/environment'
import MethodTag from './components/MethodTag.vue'
import StatusTag from './components/StatusTag.vue'
import TagInput from './components/TagInput.vue'
import ParamEditor from './components/ParamEditor.vue'
import HeaderEditor from './components/HeaderEditor.vue'
import BodyEditor from './components/BodyEditor.vue'
import DebugPanel from './components/DebugPanel.vue'
import VersionPanel from './VersionPanel.vue'
import PreActionEditor from './components/PreActionEditor.vue'
import PostActionEditor from './components/PostActionEditor.vue'
import AssertionEditor from './components/AssertionEditor.vue'
import TimeoutConfigComponent from './components/TimeoutConfig.vue'

const route = useRoute()
const router = useRouter()
const apiStore = useApiStore()
const moduleStore = useModuleStore()
const debugStore = useDebugStore()
const versionStore = useVersionStore()
const tagStore = useTagStore()

const loading = ref(false)
const saving = ref(false)
const requestTab = ref('params')
const showVersionPanel = ref(false)
const currentStatus = ref('')
const allServices = ref<Service[]>([])
const environments = ref<any[]>([])
const isNewApi = ref(false)
const formRef = ref()

const currentApi = computed(() => apiStore.currentApi)

const filteredServices = computed(() => {
  if (!formData.value.environment_id) {
    return []
  }
  return allServices.value.filter(s => s.environment_id === formData.value.environment_id)
})

const formRules = {
  module_id: [{ required: true, message: '请选择所属模块', trigger: 'change' }],
  environment_id: [{ required: true, message: '请选择环境', trigger: 'change' }],
  service_id: [{ required: true, message: '请选择关联服务', trigger: 'change' }],
  name: [{ required: true, message: '请输入接口名称', trigger: 'blur' }]
}

const formData = ref<ApiDefinitionUpdate & {
  path_params: ApiParam[]
  query_params: ApiParam[]
  header_params: ApiParam[]
  cookie_params: ApiParam[]
  responses: ApiResponse[]
  pre_request_actions: PreRequestAction[]
  post_request_actions: PostRequestAction[]
  assertions: Assertion[]
  connect_timeout: number
  read_timeout: number
  write_timeout: number
  pool_timeout: number
  sample_timeout: number
  sql_timeout: number
  script_timeout: number
  timeout_enabled: boolean
  service_id: number | null
  environment_id: number | null
}>({
  name: '',
  method: HttpMethod.GET,
  path: '',
  description: '',
  module_id: undefined,
  service_id: null,
  environment_id: null,
  body_type: BodyType.NONE,
  body_definition: '',
  path_params: [],
  query_params: [],
  header_params: [],
  cookie_params: [],
  responses: [{ status_code: 200, description: '成功', body_definition: '', body_example: '' }],
  pre_request_actions: [],
  post_request_actions: [],
  assertions: [],
  connect_timeout: 5000,
  read_timeout: 30000,
  write_timeout: 10000,
  pool_timeout: 5000,
  sample_timeout: 60000,
  sql_timeout: 30000,
  script_timeout: 10000,
  timeout_enabled: true
})

const timeoutConfigData = computed({
  get: () => ({
    connect_timeout: formData.value.connect_timeout,
    read_timeout: formData.value.read_timeout,
    write_timeout: formData.value.write_timeout,
    pool_timeout: formData.value.pool_timeout,
    sample_timeout: formData.value.sample_timeout,
    sql_timeout: formData.value.sql_timeout,
    script_timeout: formData.value.script_timeout,
    timeout_enabled: formData.value.timeout_enabled
  }),
  set: (val: any) => {
    formData.value.connect_timeout = val.connect_timeout
    formData.value.read_timeout = val.read_timeout
    formData.value.write_timeout = val.write_timeout
    formData.value.pool_timeout = val.pool_timeout
    formData.value.sample_timeout = val.sample_timeout
    formData.value.sql_timeout = val.sql_timeout
    formData.value.script_timeout = val.script_timeout
    formData.value.timeout_enabled = val.timeout_enabled
  }
})

const formDataTags = ref<string[]>([])

onMounted(async () => {
  await Promise.all([
    moduleStore.fetchModules(),
    tagStore.fetchTags()
  ])
  const envRes = await environmentApi.list({ page_size: 100 })
  environments.value = envRes.items
  const res = await environmentApi.listAllServices({ page_size: 100 })
  allServices.value = res.items
  const apiId = route.params.id
  
  if (apiId === 'new') {
    isNewApi.value = true
    currentStatus.value = 'draft'
    if (moduleStore.modules.length > 0) {
      formData.value.module_id = moduleStore.modules[0].id
    }
    if (environments.value.length > 0) {
      formData.value.environment_id = environments.value[0].id
      const envServices = allServices.value.filter(s => s.environment_id === formData.value.environment_id)
      if (envServices.length > 0) {
        formData.value.service_id = envServices[0].id
      }
    }
  } else if (apiId) {
    loading.value = true
    try {
      const api = await apiStore.fetchApi(Number(apiId))
      if (api) {
        initFormData(api)
      }
    } finally {
      loading.value = false
    }
  }
})

function initFormData(api: any) {
  currentStatus.value = api.status
  const service = allServices.value.find(s => s.id === api.service_id)
  formData.value = {
    name: api.name,
    method: api.method,
    path: api.path,
    description: api.description || '',
    module_id: api.module_id,
    service_id: api.service_id || null,
    environment_id: service ? service.environment_id : null,
    body_type: api.body_type || BodyType.NONE,
    body_definition: api.body_definition || '',
    path_params: api.path_params || [],
    query_params: api.query_params || [],
    header_params: api.header_params || [],
    cookie_params: api.cookie_params || [],
    responses: api.responses && api.responses.length > 0
      ? api.responses
      : [{ status_code: 200, description: '成功', body_definition: '', body_example: '' }],
    pre_request_actions: (api.pre_request_actions || []).map((a: any) => ({ ...a, phase: a.phase || 'pre_request', order: a.order ?? 0 })),
    post_request_actions: (api.post_request_actions || []).map((a: any) => ({ ...a, phase: a.phase || 'post_request', order: a.order ?? 0 })),
    assertions: (api.assertions || []).map((a: any) => ({ ...a, phase: a.phase || 'assertion', order: a.order ?? 0 })),
    connect_timeout: api.connect_timeout || 5000,
    read_timeout: api.read_timeout || 30000,
    write_timeout: api.write_timeout || 10000,
    pool_timeout: api.pool_timeout || 5000,
    sample_timeout: api.sample_timeout || 60000,
    sql_timeout: api.sql_timeout || 30000,
    script_timeout: api.script_timeout || 10000,
    timeout_enabled: api.timeout_enabled !== undefined ? api.timeout_enabled : true
  }
  formDataTags.value = api.tags ? api.tags.map((t: any) => t.name) : []
}

function handleEnvironmentChange() {
  formData.value.service_id = null
  const envServices = filteredServices.value
  if (envServices.length > 0) {
    formData.value.service_id = envServices[0].id
  }
}

async function handleSave() {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  
  saving.value = true
  try {
    const tagIds: number[] = []
    for (const tagName of formDataTags.value) {
      let tag = tagStore.tags.find(t => t.name === tagName)
      if (!tag) {
        tag = await tagStore.createTag({ name: tagName })
      }
      tagIds.push(tag.id)
    }
    
    const saveData = {
      ...formData.value,
      tag_ids: tagIds
    }
    
    if (isNewApi.value) {
      const newApi = await apiStore.createApi({
        ...saveData,
        team_id: 1
      })
      ElMessage.success('创建成功')
      isNewApi.value = false
      router.push(`/apis/${newApi.id}`)
    } else if (currentApi.value) {
      await apiStore.updateApi(currentApi.value.id, saveData)
      ElMessage.success('保存成功')
    }
  } catch (error: any) {
    // handled
  } finally {
    saving.value = false
  }
}

async function handleStatusChange(status: string) {
  if (!currentApi.value) return
  if (status === 'deprecated' || status === 'disabled') {
    try {
      await ElMessageBox.confirm(
        `确定要将接口状态修改为"${API_STATUSES.find(s => s.value === status)?.label}"吗？`,
        '提示',
        { type: 'warning' }
      )
    } catch {
      currentStatus.value = currentApi.value.status
      return
    }
  }
  try {
    await apiStore.updateApiStatus(currentApi.value.id, status)
    ElMessage.success('状态修改成功')
  } catch (error: any) {
    currentStatus.value = currentApi.value.status
  }
}

function handleDebug() {
  if (!currentApi.value) return
  debugStore.openDebug(currentApi.value.id)
}

async function handleMoreCommand(cmd: string) {
  if (!currentApi.value) return
  if (cmd === 'copy') {
    try {
      await ElMessageBox.confirm(`确定要复制接口"${currentApi.value.name}"吗？`, '提示', { type: 'warning' })
      const newApi = await apiStore.copyApi(currentApi.value.id)
      ElMessage.success('复制成功')
      router.push(`/apis/${newApi.id}`)
    } catch (error: any) {
      if (error !== 'cancel') { /* handled */ }
    }
  } else if (cmd === 'version') {
    showVersionPanel.value = true
  } else if (cmd === 'delete') {
    try {
      await ElMessageBox.confirm(
        `确定删除接口"${currentApi.value.name}"吗？此操作不可恢复。`,
        '警告',
        { type: 'warning' }
      )
      await apiStore.deleteApi(currentApi.value.id)
      ElMessage.success('删除成功')
      router.push('/apis')
    } catch (error: any) {
      if (error !== 'cancel') { /* handled */ }
    }
  }
}

function formatDate(date: string) {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}
</script>

<style scoped>
.api-detail {
  padding: 24px;
  background-color: #f9fafb;
  min-height: 100vh;
}

.breadcrumb {
  margin-bottom: 24px;
  padding: 16px 24px;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.api-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #08060d;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-right :deep(.el-button) {
  margin: 0;
}

.header-right :deep(.el-dropdown .el-button) {
  margin: 0;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section-card {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #08060d;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e5e4e7;
}

.sub-label {
  font-size: 13px;
  font-weight: 500;
  color: #6b6375;
  margin-bottom: 8px;
}

.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.info-label {
  font-size: 14px;
  color: #6b6375;
  margin-right: 8px;
}

.info-value {
  font-size: 14px;
  color: #08060d;
}

.code-textarea :deep(.el-textarea__inner) {
  font-family: ui-monospace, Consolas, monospace;
  font-size: 13px;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .header-right {
    width: 100%;
    flex-wrap: wrap;
  }
}
</style>
