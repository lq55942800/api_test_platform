<template>
  <el-drawer
    v-model="visible"
    :title="isEdit ? '编辑测试用例' : '新建测试用例'"
    size="80%"
    :close-on-click-modal="false"
  >
    <div class="testcase-edit-form">
      <el-form ref="formRef" :model="form" label-width="100px">
        <el-form-item label="用例名称" prop="name">
          <el-input v-model="form.name" placeholder="例如：登录流程测试" />
        </el-form-item>

        <el-form-item label="所属模块">
          <el-select v-model="form.module_id" placeholder="选择模块" clearable>
            <el-option
              v-for="mod in modules"
              :key="mod.id"
              :label="mod.name"
              :value="mod.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="优先级">
          <el-select v-model="form.priority" style="width: 120px">
            <el-option label="P0" value="P0" />
            <el-option label="P1" value="P1" />
            <el-option label="P2" value="P2" />
            <el-option label="P3" value="P3" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio label="enabled">启用</el-radio>
            <el-radio label="disabled">禁用</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" rows="2" />
        </el-form-item>
      </el-form>

      <el-divider>测试步骤</el-divider>

      <div class="steps-section">
        <div class="step-list">
          <div
            v-for="(step, index) in form.steps"
            :key="index"
            class="step-item"
          >
            <div class="step-header">
              <span class="step-index">{{ index + 1 }}</span>
              <el-select
                v-model="step.step_type"
                style="width: 100px"
                @change="onStepTypeChange(step)"
              >
                <el-option label="API" value="api" />
                <el-option label="IF条件" value="if" />
                <el-option label="FOR循环" value="for" />
                <el-option label="WHILE循环" value="while" />
              </el-select>
              <el-input
                v-model="step.step_name"
                placeholder="步骤名称"
                style="flex: 1"
              />
              <el-switch v-model="step.enabled" />
              <el-button
                type="danger"
                icon="Delete"
                plain
                circle
                @click="removeStep(index)"
              />
            </div>

            <div v-if="step.step_type === 'api'" class="step-api-config">
              <el-select
                v-model="step.api_id"
                placeholder="选择API"
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="api in apis"
                  :key="api.id"
                  :label="`${api.method} ${api.name}`"
                  :value="api.id"
                />
              </el-select>

              <div v-if="step.api_id" class="step-overrides">
                <h4>参数覆盖</h4>
                <KeyValueEditor v-model="step.override_params" />
                <h4>请求头覆盖</h4>
                <KeyValueEditor v-model="step.override_headers" />
              </div>
            </div>

            <div v-if="step.step_type === 'if' || step.step_type === 'for' || step.step_type === 'while'" class="step-condition">
              <el-input
                v-model="step.execution_condition"
                type="textarea"
                rows="2"
                placeholder="条件表达式，如: ${status} == 'success'"
              />
            </div>
          </div>
        </div>

        <el-button type="primary" plain :icon="Plus" @click="addStep">
          添加步骤
        </el-button>
      </div>

      <div class="drawer-footer">
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSubmit">保存</el-button>
      </div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useTestCaseStore } from '@/stores/testcase'
import { useApiStore } from '@/stores/api'
import type { TestCase, TestCaseStep, StepType } from '@/types'
import KeyValueEditor from '@/components/forms/KeyValueEditor.vue'

interface KeyValueItem {
  key: string
  value: string
  description?: string
}

const props = defineProps<{
  modelValue: boolean
  testcase?: TestCase | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

const testCaseStore = useTestCaseStore()
const apiStore = useApiStore()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const isEdit = computed(() => !!props.testcase?.id)

const formRef = ref()
const saving = ref(false)

const { modules } = testCaseStore
const { apis } = apiStore

const form = ref({
  name: '',
  module_id: null as number | null,
  description: '',
  status: 'enabled' as const,
  priority: 'P2' as const,
  steps: [] as TestCaseStep[],
})

const defaultStep: TestCaseStep = {
  step_type: 'api',
  step_name: '',
  enabled: true,
  api_id: null,
  override_params: [],
  override_headers: [],
  override_body: null,
  assertions: [],
  extractors: [],
  pre_script: null,
  post_script: null,
  execution_condition: null,
}

watch(() => props.testcase, (tc) => {
  if (tc) {
    form.value = {
      name: tc.name,
      module_id: tc.module_id,
      description: tc.description || '',
      status: tc.status,
      priority: tc.priority,
      steps: tc.steps ? [...tc.steps] : [],
    }
  } else {
    form.value = {
      name: '',
      module_id: null,
      description: '',
      status: 'enabled',
      priority: 'P2',
      steps: [],
    }
  }
}, { immediate: true })

const addStep = () => {
  form.value.steps.push({ ...defaultStep })
}

const removeStep = (index: number) => {
  form.value.steps.splice(index, 1)
}

const onStepTypeChange = (step: TestCaseStep) => {
  if (step.step_type !== 'api') {
    step.api_id = null
  }
}

const handleSubmit = async () => {
  if (!form.value.name) {
    ElMessage.warning('请输入用例名称')
    return
  }

  try {
    saving.value = true

    if (isEdit.value) {
      await testCaseStore.updateTestCase(props.testcase!.id!, form.value, 1)
      ElMessage.success('更新成功')
    } else {
      await testCaseStore.createTestCase(form.value, 1, 1)
      ElMessage.success('创建成功')
    }

    emit('success')
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// Fetch APIs for the dropdown
apiStore.fetchApis()
</script>

<style scoped>
.testcase-edit-form {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.testcase-edit-form .el-form {
  padding-right: var(--spacing-md);
}

.steps-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.step-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.step-item {
  background: var(--color-bg-hover);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
}

.step-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.step-index {
  width: 28px;
  height: 28px;
  background: var(--color-primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8125rem;
  font-weight: 600;
}

.step-api-config {
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border-light);
}

.step-overrides {
  margin-top: var(--spacing-md);
}

.step-overrides h4 {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-sm);
}

.step-condition {
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border-light);
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border);
  margin-top: var(--spacing-lg);
}
</style>