<template>
  <div class="testcase-detail" v-loading="loading">
    <div class="breadcrumb-card">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/testcase' }">测试用例</el-breadcrumb-item>
        <el-breadcrumb-item>{{ isNew ? '新建用例' : (formData.name || '用例详情') }}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="detail-header">
      <div class="header-left">
        <el-button link @click="router.push('/testcase')">
          <el-icon><ArrowLeft /></el-icon>
          返回列表
        </el-button>
        <template v-if="!isNew">
          <el-tag :type="formData.status === 'enabled' ? 'success' : 'info'" size="small" effect="light">
            {{ formData.status === 'enabled' ? '启用' : '禁用' }}
          </el-tag>
          <el-tag :type="priorityTagType" size="small" effect="light">{{ formData.priority }}</el-tag>
          <h2 class="detail-title">{{ formData.name || '测试用例' }}</h2>
        </template>
        <template v-else>
          <el-tag type="info" size="small">新建用例</el-tag>
        </template>
      </div>
      <div class="header-right">
        <template v-if="!isNew">
          <el-select v-model="selectedEnvironmentId" placeholder="选择环境" size="default" style="width: 160px" clearable>
            <el-option v-for="env in environments" :key="env.id" :label="env.name" :value="env.id" />
          </el-select>
          <el-button type="success" size="small" @click="handleExecute">
            <el-icon><VideoPlay /></el-icon>
            执行
          </el-button>
        </template>
        <el-button type="primary" size="small" @click="handleSave" :loading="saving">
          {{ isNew ? '创建' : '保存' }}
        </el-button>
      </div>
    </div>

    <div class="detail-content">
      <div class="section-card">
        <div class="section-title">基本信息</div>
        <el-form :model="formData" :rules="formRules" ref="formRef" label-width="80px" label-position="left">
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="用例名称" prop="name">
                <el-input v-model="formData.name" placeholder="请输入用例名称" maxlength="100" show-word-limit />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="优先级" prop="priority">
                <el-select v-model="formData.priority" style="width: 100%">
                  <el-option label="P0" value="P0" />
                  <el-option label="P1" value="P1" />
                  <el-option label="P2" value="P2" />
                  <el-option label="P3" value="P3" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="状态">
                <div class="status-switch">
                  <el-switch
                    v-model="formData.status"
                    active-value="enabled"
                    inactive-value="disabled"
                    active-text="启用"
                    inactive-text="禁用"
                    inline-prompt
                    style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949"
                  />
                </div>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="标签">
                <el-select v-model="formData.tags" multiple filterable allow-create default-first-option placeholder="选择或创建标签" style="width: 100%">
                  <el-option v-for="tag in existTags" :key="tag" :label="tag" :value="tag" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="所属模块">
                <el-select v-model="formData.module_ids" multiple filterable collapse-tags collapse-tags-tooltip placeholder="选择模块" clearable style="width: 100%">
                  <el-option v-for="m in modules" :key="m.id" :label="m.name" :value="m.id" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="描述">
            <el-input v-model="formData.description" type="textarea" placeholder="请输入用例描述信息" :rows="3" maxlength="500" show-word-limit />
          </el-form-item>
        </el-form>
      </div>

      <div class="section-card">
        <div class="section-title">变量配置</div>
        <VariableConfig v-model="formData.variables" />
      </div>

      <div class="section-card">
        <div class="section-title">
          测试步骤
          <el-badge :value="totalStepCount" type="primary" style="margin-left: 8px" />
          <div class="section-title-right">
            <el-dropdown trigger="click" @command="addStep">
              <el-button type="primary" size="small">
                <el-icon><Plus /></el-icon>
                添加步骤
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="api">
                    <el-icon><Connection /></el-icon> API步骤
                  </el-dropdown-item>
                  <el-dropdown-item command="if">
                    <el-icon><Switch /></el-icon> IF 条件判断
                  </el-dropdown-item>
                  <el-dropdown-item command="for">
                    <el-icon><Refresh /></el-icon> FOR 循环
                  </el-dropdown-item>
                  <el-dropdown-item command="while">
                    <el-icon><Loading /></el-icon> WHILE 循环
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>

        <div v-if="stepTree.length > 0" class="step-list">
          <draggable v-model="stepTree" item-key="sort_order" handle=".step-drag-handle" ghost-class="step-ghost" animation="200">
            <template #item="{ element: step, index }">
              <StepRow
                :step="step"
                :step-index="String(index + 1)"
                :depth="0"
                :max-depth="3"
                :api-list="apis"
                @edit="onStepEdit"
                @copy="onStepCopy"
                @delete="onStepDelete"
                @toggle-enabled="onStepToggleEnabled"
                @add-child="onStepAddChild"
              />
            </template>
          </draggable>
        </div>
        <el-empty v-else description="暂无测试步骤，点击上方按钮添加" :image-size="80" />
      </div>
    </div>

    <ApiStepDrawer
      v-model="showApiDrawer"
      :step="editingStep"
      :api-list="apis"
      :environment-id="selectedEnvironmentId"
      @save="onStepSave"
    />

    <ConditionStepDrawer
      v-model="showConditionDrawer"
      :step="editingStep"
      @save="onStepSave"
    />

    <el-dialog v-model="showExecuteDialog" title="执行测试用例" width="520px" :close-on-click-modal="false">
      <el-form :model="executeForm" label-position="top">
        <el-form-item label="选择环境" required>
          <el-select v-model="executeForm.environment_id" placeholder="请选择执行环境" style="width: 100%">
            <el-option v-for="env in environments" :key="env.id" :label="env.name" :value="env.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="失败策略">
              <el-radio-group v-model="executeForm.fail_strategy">
                <el-radio value="stop">遇错停止</el-radio>
                <el-radio value="continue">继续执行</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="保存记录">
              <el-switch v-model="executeForm.save_record" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="超时(秒)">
              <el-input-number v-model="executeForm.timeout" :min="10" :max="600" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="步骤间隔(ms)">
              <el-input-number v-model="executeForm.step_interval" :min="0" :max="10000" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showExecuteDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmExecute" :loading="executing">{{ isDebugMode ? '调试执行' : '执行' }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showDebugResult" title="执行结果" width="1000px" top="5vh" :close-on-click-modal="false">
      <div v-if="debugResult" class="result-panel">
        <div class="result-header-bar">
          <div class="result-header-left">
            <el-tag :type="debugResult.status === 'passed' ? 'success' : 'danger'" size="large" effect="dark" round>
              {{ debugResult.status === 'passed' ? '执行成功' : debugResult.status === 'failed' ? '执行失败' : debugResult.status }}
            </el-tag>
            <h2 class="result-title">执行结果 #{{ testCaseId }}</h2>
          </div>
          <div class="result-header-right">
            <span class="result-subtitle">{{ formData.name || '测试用例' }} · {{ formatTime(debugResult.start_time || new Date().toISOString()) }}</span>
          </div>
        </div>

        <el-row :gutter="16" class="result-summary">
          <el-col :span="6">
            <el-statistic title="总步骤数" :value="debugResult.total_steps" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="通过步骤" :value="debugResult.passed_steps" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="失败步骤" :value="debugResult.failed_steps" />
          </el-col>
          <el-col :span="6">
            <el-statistic
              title="总耗时"
              :value="debugResult.duration ? (debugResult.duration / 1000).toFixed(2) : '-'"
            >
              <template #suffix>
                <span v-if="debugResult.duration">s</span>
              </template>
            </el-statistic>
          </el-col>
        </el-row>

        <div v-if="debugResult.error_message" class="result-error">
          <el-alert type="error" :closable="false" show-icon>
            <template #title>错误信息</template>
            <div>{{ debugResult.error_message }}</div>
          </el-alert>
        </div>

        <div class="result-steps-section">
          <div class="section-title">
            执行步骤
            <el-badge :value="debugResult.step_results?.length || 0" type="primary" style="margin-left: 8px" />
          </div>
          <div v-if="!debugResult.step_results?.length">
            <el-empty description="暂无执行步骤记录" />
          </div>
          <el-collapse v-else v-model="expandedResultSteps" class="step-collapse">
            <el-collapse-item
              v-for="(sr, idx) in debugResult.step_results"
              :key="idx"
              :name="idx"
            >
              <template #title>
                <div class="step-header">
                  <div class="step-left">
                    <el-tag round :type="sr.status === 'passed' ? 'success' : 'danger'" size="small" effect="dark">
                      {{ idx + 1 }}
                    </el-tag>
                    <el-tag :type="sr.status === 'passed' ? 'success' : 'danger'" size="small">
                      {{ sr.status === 'passed' ? '通过' : sr.status === 'failed' ? '失败' : sr.status }}
                    </el-tag>
                    <span class="step-name">{{ sr.step_name }}</span>
                  </div>
                  <div class="step-right" @click.stop>
                    <span v-if="sr.response_status" class="step-http">{{ sr.response_status }}</span>
                    <span v-if="sr.response_time" class="step-duration">{{ sr.response_time }}ms</span>
                  </div>
                </div>
              </template>
              <StepDetailPanel :step="adaptStepResult(sr)" />
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>
      <template #footer>
        <el-button @click="showDebugResult = false">关闭</el-button>
        <el-button type="primary" @click="showDebugResult = false">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, VideoPlay, Monitor, Plus, Connection, Switch, Refresh, Loading } from '@element-plus/icons-vue'
import draggable from 'vuedraggable'
import { testCaseApi, testCaseModuleApi, executeSSE } from '@/api/testcase'
import type { SSEStepEvent } from '@/api/testcase'
import { moduleApi } from '@/api/api'
import { apiApi } from '@/api/api'
import { environmentApi } from '@/api/environment'
import VariableConfig from './components/VariableConfig.vue'
import StepRow from './components/StepRow.vue'
import ApiStepDrawer from './components/ApiStepDrawer.vue'
import ConditionStepDrawer from './components/ConditionStepDrawer.vue'
import StepDetailPanel from './components/StepDetailPanel.vue'
import type { TestCaseStep, TestCaseStepCreate, TestCaseVariable, TestCaseModule, ExecuteRequest, StepExecutionRecord } from '@/types/testcase'
import type { ApiDefinition } from '@/types/api'
import type { Environment } from '@/types/environment'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const route = useRoute()
const isNew = computed(() => route.name === 'TestCaseCreate')
const testCaseId = computed(() => Number(route.params.id))
const loading = ref(false)
const saving = ref(false)
const formRef = ref<FormInstance>()

const formData = ref({
  name: '',
  module_ids: [] as number[],
  description: '',
  status: 'enabled' as 'enabled' | 'disabled',
  priority: 'P2' as 'P0' | 'P1' | 'P2' | 'P3',
  tags: [] as string[],
  variables: [] as TestCaseVariable[]
})

const stepTree = ref<TestCaseStep[]>([])
const modules = ref<TestCaseModule[]>([])
const apis = ref<ApiDefinition[]>([])
const environments = ref<Environment[]>([])
const existTags = ref<string[]>(['冒烟测试', '回归测试', '接口测试', '性能测试'])
const selectedEnvironmentId = ref<number | null>(null)

const showApiDrawer = ref(false)
const showConditionDrawer = ref(false)
const editingStep = ref<TestCaseStep | null>(null)
const editingParentStepId = ref<number | null>(null)

const showExecuteDialog = ref(false)
const executing = ref(false)
const isDebugMode = ref(false)
const executeForm = ref<ExecuteRequest>({ environment_id: 0, fail_strategy: 'stop', save_record: true, timeout: 300, step_interval: 0 })

const showDebugResult = ref(false)
const debugResult = ref<any>(null)
const expandedResultSteps = ref<number[]>([])

function adaptStepResult(sr: any): StepExecutionRecord {
  return {
    id: sr.id || 0,
    execution_id: sr.execution_id || 0,
    step_id: sr.step_id || 0,
    step_name: sr.step_name || '',
    status: sr.status || '',
    start_time: sr.start_time || null,
    end_time: sr.end_time || null,
    duration: sr.response_time || sr.duration || 0,
    request_data: {
      ...sr.request_data,
      assertions: sr.assertions || sr.request_data?.assertions || null,
      extractors: sr.extractors || sr.extracted_variables || sr.request_data?.extractors || null,
      pre_actions: sr.pre_actions || sr.request_data?.pre_actions || null,
      post_actions: sr.post_actions || sr.request_data?.post_actions || null
    },
    response_data: sr.response_data || null,
    error_message: sr.error_message || null
  }
}

const priorityTagType = computed(() => {
  const map: Record<string, string> = { P0: 'danger', P1: 'warning', P2: '', P3: 'info' }
  return map[formData.value.priority] || ''
})

const totalStepCount = computed(() => {
  function countSteps(steps: TestCaseStep[]): number {
    let count = 0
    for (const s of steps) {
      count++
      if (s.children?.length) count += countSteps(s.children)
    }
    return count
  }
  return countSteps(stepTree.value)
})

const formRules: FormRules = {
  name: [{ required: true, message: '请输入用例名称', trigger: 'blur' }],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }]
}

onMounted(async () => {
  await Promise.all([fetchModules(), fetchApis(), fetchEnvironments()])
  if (!isNew.value) await fetchTestCase()
})

async function fetchTestCase() {
  loading.value = true
  try {
    const data = await testCaseApi.get(testCaseId.value)
    formData.value = {
      name: data.name,
      module_ids: data.module_id ? [data.module_id] : [],
      description: data.description || '',
      status: data.status,
      priority: data.priority,
      tags: data.tags || [],
      variables: (data.variables || []) as TestCaseVariable[]
    }
    if (data.steps?.length) {
      const firstStep = data.steps[0]
      if ('children' in firstStep || firstStep.parent_step_id !== undefined) {
        stepTree.value = flatToTree(data.steps as TestCaseStep[])
      } else {
        stepTree.value = data.steps as TestCaseStep[]
      }
    } else {
      stepTree.value = []
    }
  } catch (error) {
    console.error('获取测试用例详情失败:', error)
  } finally {
    loading.value = false
  }
}

async function fetchModules() {
  try {
    modules.value = await moduleApi.list()
  } catch (error) {
    console.error('获取模块列表失败:', error)
  }
}

async function fetchApis() {
  try {
    const r = await apiApi.list({ page_size: 100 })
    apis.value = r.items
  } catch (error) {
    console.error('获取API列表失败:', error)
  }
}

async function fetchEnvironments() {
  try {
    const r = await environmentApi.list({ page_size: 100 })
    environments.value = r.items || []
    if (environments.value.length > 0 && !selectedEnvironmentId.value) {
      const defaultEnv = environments.value.find((e: Environment) => e.is_default)
      selectedEnvironmentId.value = defaultEnv?.id || environments.value[0].id
    }
  } catch (error) {
    console.error('获取环境列表失败:', error)
  }
}

function flatToTree(flatList: TestCaseStep[]): TestCaseStep[] {
  const map = new Map<number, TestCaseStep>()
  const roots: TestCaseStep[] = []

  for (const step of flatList) {
    const cloned = { ...step, children: [] as TestCaseStep[] }
    if (step.id) map.set(step.id, cloned)
  }

  for (const step of flatList) {
    const cloned = map.get(step.id!)
    if (!cloned) continue
    if (step.parent_step_id && map.has(step.parent_step_id)) {
      map.get(step.parent_step_id)!.children!.push(cloned)
    } else {
      roots.push(cloned)
    }
  }

  return roots
}

function treeToFlat(tree: TestCaseStep[], parentId: number | null = null): TestCaseStepCreate[] {
  const result: TestCaseStepCreate[] = []

  function traverse(steps: TestCaseStep[], parentStepId: number | null, startIndex: number) {
    for (let i = 0; i < steps.length; i++) {
      const step = steps[i]
      const flatStep: TestCaseStepCreate = {
        step_type: step.step_type,
        api_id: step.api_id,
        parent_step_id: parentStepId,
        step_name: step.step_name,
        sort_order: startIndex + i,
        enabled: step.enabled,
        override_headers: step.override_headers,
        override_params: step.override_params,
        override_body: step.override_body,
        override_body_type: step.override_body_type,
        override_cookies: step.override_cookies,
        assertions: step.assertions,
        extractors: step.extractors,
        pre_script: step.pre_script,
        post_script: step.post_script,
        timeout_config: step.timeout_config,
        execution_condition: step.execution_condition
      }
      result.push(flatStep)
      if (step.children?.length) {
        traverse(step.children, null, 0)
      }
    }
  }

  traverse(tree, parentId, 0)
  return result
}

function assignSortOrders(steps: TestCaseStep[], parentStepId: number | null = null): TestCaseStepCreate[] {
  const result: TestCaseStepCreate[] = []
  for (let i = 0; i < steps.length; i++) {
    const step = steps[i]
    const flatStep: TestCaseStepCreate = {
      step_type: step.step_type,
      api_id: step.api_id,
      parent_step_id: parentStepId,
      step_name: step.step_name,
      sort_order: i,
      enabled: step.enabled,
      override_headers: step.override_headers,
      override_params: step.override_params,
      override_body: step.override_body,
      override_body_type: step.override_body_type,
      override_cookies: step.override_cookies,
      assertions: step.assertions,
      extractors: step.extractors,
      pre_script: step.pre_script,
      post_script: step.post_script,
      timeout_config: step.timeout_config,
      execution_condition: step.execution_condition
    }
    result.push(flatStep)
    if (step.children?.length) {
      const childSteps = assignSortOrders(step.children, step.id || null)
      result.push(...childSteps)
    }
  }
  return result
}

function addStep(command: string) {
  if (command === 'api') {
    addApiStep()
  } else {
    addConditionStep(command)
  }
}

function addApiStep() {
  const newStep: TestCaseStep = {
    step_type: 'api',
    api_id: null,
    step_name: '',
    sort_order: stepTree.value.length,
    enabled: true
  }
  editingStep.value = newStep
  editingParentStepId.value = null
  showApiDrawer.value = true
}

function addConditionStep(type: string) {
  editingStep.value = null
  editingParentStepId.value = null
  const newStep: TestCaseStep = {
    step_type: type as 'if' | 'for' | 'while',
    step_name: '',
    sort_order: stepTree.value.length,
    enabled: true,
    execution_condition: { type: type as 'if' | 'for' | 'while' },
    children: []
  }
  editingStep.value = newStep
  showConditionDrawer.value = true
}

function onStepEdit(step: TestCaseStep) {
  editingStep.value = { ...step }
  if (step.step_type === 'api') {
    showApiDrawer.value = true
  } else {
    showConditionDrawer.value = true
  }
}

function onStepCopy(step: TestCaseStep) {
  function deepCopyStep(s: TestCaseStep): TestCaseStep {
    const copied: TestCaseStep = {
      ...s,
      id: undefined,
      step_name: `${s.step_name || '步骤'} (副本)`,
      children: s.children ? s.children.map(c => deepCopyStep(c)) : []
    }
    if (s.assertions) copied.assertions = [...s.assertions]
    if (s.extractors) copied.extractors = s.extractors.map((e: any) => ({ ...e, config: { ...e.config } }))
    return copied
  }

  const copied = deepCopyStep(step)

  function insertAfterStep(tree: TestCaseStep[], target: TestCaseStep, newStep: TestCaseStep): boolean {
    for (let i = 0; i < tree.length; i++) {
      if (tree[i] === target) {
        tree.splice(i + 1, 0, newStep)
        return true
      }
      if (tree[i].children?.length) {
        if (insertAfterStep(tree[i].children!, target, newStep)) return true
      }
    }
    return false
  }

  insertAfterStep(stepTree.value, step, copied)
  ElMessage.success('步骤已复制')
}

function onStepDelete(step: TestCaseStep) {
  ElMessageBox.confirm('确定删除该步骤及其子步骤吗？', '警告', { type: 'warning' })
    .then(() => {
      function removeFromTree(tree: TestCaseStep[], target: TestCaseStep): boolean {
        const idx = tree.indexOf(target)
        if (idx >= 0) {
          tree.splice(idx, 1)
          return true
        }
        for (const s of tree) {
          if (s.children?.length && removeFromTree(s.children!, target)) return true
        }
        return false
      }
      removeFromTree(stepTree.value, step)
      ElMessage.success('步骤已删除')
    })
    .catch(() => {})
}

function onStepToggleEnabled(step: TestCaseStep, enabled: boolean) {
  step.enabled = enabled
}

function onStepAddChild(parentStep: TestCaseStep, stepType: string) {
  if (stepType === 'api') {
    editingStep.value = null
    editingParentStepId.value = parentStep.id || null
    const newStep: TestCaseStep = {
      step_type: 'api',
      api_id: null,
      parent_step_id: parentStep.id || null,
      step_name: '',
      sort_order: parentStep.children?.length || 0,
      enabled: true
    }
    editingStep.value = newStep
    showApiDrawer.value = true
  } else {
    editingStep.value = null
    editingParentStepId.value = parentStep.id || null
    const newStep: TestCaseStep = {
      step_type: stepType as 'if' | 'for' | 'while',
      parent_step_id: parentStep.id || null,
      step_name: '',
      sort_order: parentStep.children?.length || 0,
      enabled: true,
      execution_condition: { type: stepType as 'if' | 'for' | 'while' },
      children: []
    }
    editingStep.value = newStep
    showConditionDrawer.value = true
  }
}

function onStepSave(step: TestCaseStep) {
  if (editingParentStepId.value !== null) {
    function findParent(tree: TestCaseStep[], parentId: number | null): TestCaseStep | null {
      for (const s of tree) {
        if (s.id === parentId) return s
        if (s.children?.length) {
          const found = findParent(s.children!, parentId)
          if (found) return found
        }
      }
      return null
    }
    const parent = findParent(stepTree.value, editingParentStepId.value)
    if (parent) {
      if (!parent.children) parent.children = []
      step.parent_step_id = editingParentStepId.value
      parent.children.push(step)
    }
    editingParentStepId.value = null
    return
  }

  if (editingStep.value && editingStep.value.id !== undefined) {
    function updateInTree(tree: TestCaseStep[], targetId: number | undefined, newStep: TestCaseStep): boolean {
      for (let i = 0; i < tree.length; i++) {
        if (tree[i].id === targetId) {
          newStep.children = tree[i].children || []
          tree[i] = newStep
          return true
        }
        if (tree[i].children?.length && updateInTree(tree[i].children!, targetId, newStep)) return true
      }
      return false
    }
    const updated = updateInTree(stepTree.value, editingStep.value.id, step)
    if (!updated) {
      stepTree.value.push(step)
    }
  } else {
    stepTree.value.push(step)
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
    const flatSteps = assignSortOrders(stepTree.value)

    const saveData = {
      name: formData.value.name,
      module_id: formData.value.module_ids.length > 0 ? formData.value.module_ids[0] : null,
      description: formData.value.description,
      status: formData.value.status,
      priority: formData.value.priority,
      tags: formData.value.tags,
      variables: formData.value.variables,
      steps: flatSteps
    }

    if (isNew.value) {
      const result = await testCaseApi.create(saveData)
      ElMessage.success('创建成功')
      router.push(`/testcase/${result.id}`)
    } else {
      await testCaseApi.update(testCaseId.value, saveData)
      ElMessage.success('保存成功')
      await fetchTestCase()
    }
  } catch (error) {
    console.error('保存失败:', error)
  } finally {
    saving.value = false
  }
}

function handleExecute() {
  isDebugMode.value = false
  executeForm.value.environment_id = selectedEnvironmentId.value || 0
  showExecuteDialog.value = true
}

function handleDebug() {
  isDebugMode.value = true
  executeForm.value.save_record = false
  executeForm.value.environment_id = selectedEnvironmentId.value || 0
  showExecuteDialog.value = true
}

async function confirmExecute() {
  if (!executeForm.value.environment_id) {
    ElMessage.warning('请选择执行环境')
    return
  }
  executing.value = true
  showExecuteDialog.value = false
  const sseSteps = ref<any[]>([])
  let executionId: number | null = null
  executeSSE(
    testCaseId.value,
    executeForm.value,
    (event: SSEStepEvent) => {
      if (event.type === 'started' && event.execution_id) {
        executionId = event.execution_id
        ElMessage.info('执行已启动，正在运行...')
      } else if (event.type === 'step') {
        sseSteps.value.push(event)
      } else if (event.type === 'completed') {
        ElMessage.success(event.status === 'passed' ? '执行通过' : '执行未通过')
        if (executionId) {
          router.push(`/execution/${executionId}`)
        }
      } else if (event.type === 'error') {
        ElMessage.error(event.message || event.error || '执行失败')
      }
    },
    (error) => {
      console.error('SSE执行错误:', error)
      ElMessage.error('执行连接失败')
      executing.value = false
    },
    () => {
      executing.value = false
    }
  )
}

function formatTime(time: string) {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

function getMethodType(method: string) {
  const map: Record<string, string> = {
    GET: 'success',
    POST: 'primary',
    PUT: 'warning',
    DELETE: 'danger',
    PATCH: 'info'
  }
  return map[method?.toUpperCase()] || 'info'
}


</script>

<style scoped>
.testcase-detail {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.breadcrumb-card {
  margin-bottom: 16px;
  padding: 12px 20px;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.breadcrumb-card :deep(.el-breadcrumb) {
  font-size: 14px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  margin-bottom: 20px;
  border: 1px solid #eef2f7;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left :deep(.el-button) {
  color: #606266;
}

.header-left :deep(.el-button:hover) {
  color: #409eff;
}

.detail-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a2e;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-right :deep(.el-button) {
  margin: 0;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-card {
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  padding: 24px;
  transition: box-shadow 0.3s ease;
}

.section-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid #eef2f7;
  display: flex;
  align-items: center;
}

.section-title::before {
  content: '';
  width: 4px;
  height: 18px;
  background-color: #409eff;
  border-radius: 2px;
  margin-right: 10px;
}

.section-title-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title-right :deep(.el-button) {
  border-radius: 6px;
}

.step-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.step-ghost {
  opacity: 0.4;
  background: #f5f0ff;
}

.result-panel {
  max-height: 700px;
  overflow-y: auto;
}

.result-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.result-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.result-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #08060d;
}

.result-header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.result-subtitle {
  font-size: 14px;
  color: #6b6375;
}

.result-summary {
  margin-bottom: 20px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.result-error {
  margin-bottom: 16px;
}

.result-steps-section {
  margin-top: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #08060d;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid #eef2f7;
  display: flex;
  align-items: center;
}

.section-title::before {
  content: '';
  width: 4px;
  height: 18px;
  background-color: #6145ff;
  border-radius: 2px;
  margin-right: 10px;
}

.step-collapse {
  border: none;
}

.step-collapse :deep(.el-collapse-item__header) {
  background-color: #fafafa;
  padding: 0 16px;
  border-radius: 0;
  height: auto;
  min-height: 48px;
  line-height: normal;
  padding-top: 8px;
  padding-bottom: 8px;
}

.step-collapse :deep(.el-collapse-item__wrap) {
  border: none;
  border-top: 1px solid #e4e7ed;
}

.step-collapse :deep(.el-collapse-item__content) {
  padding: 16px;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.step-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.step-name {
  font-weight: 500;
  color: #303133;
}

.step-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.step-http {
  color: #909399;
  font-size: 13px;
}

.step-duration {
  color: #909399;
  font-size: 13px;
}

.status-switch {
  display: flex;
  align-items: center;
}

:deep(.el-collapse-item__header) {
  background-color: #ffffff;
  border: 1px solid #e5e4e7;
  border-radius: 8px;
  padding: 12px 16px;
  height: auto;
  line-height: 1.5;
}

:deep(.el-collapse-item__wrap) {
  border: none;
  background-color: transparent;
}

:deep(.el-collapse-item__content) {
  padding-top: 8px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}

:deep(.el-input__wrapper),
:deep(.el-select .el-input__wrapper) {
  border-radius: 6px;
}

:deep(.el-textarea__inner) {
  border-radius: 6px;
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
