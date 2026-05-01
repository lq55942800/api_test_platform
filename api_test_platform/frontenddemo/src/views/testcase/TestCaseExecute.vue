<template>
  <el-drawer
    v-model="visible"
    title="执行测试用例"
    size="600px"
  >
    <div class="execute-panel">
      <div v-if="!executing && !result" class="execute-form">
        <el-form label-width="100px">
          <el-form-item label="执行环境">
            <el-select v-model="environmentId" placeholder="选择环境" style="width: 100%">
              <el-option
                v-for="env in environments"
                :key="env.id"
                :label="env.name"
                :value="env.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="失败策略">
            <el-radio-group v-model="failStrategy">
              <el-radio label="stop">失败停止</el-radio>
              <el-radio label="continue">失败继续</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="保存记录">
            <el-switch v-model="saveRecord" />
          </el-form-item>
        </el-form>

        <div class="execute-actions">
          <el-button type="primary" size="large" @click="startExecute" :disabled="!environmentId">
            开始执行
          </el-button>
        </div>
      </div>

      <div v-if="executing" class="executing-state">
        <el-icon class="is-loading" size="32"><Loading /></el-icon>
        <span>执行中...</span>
        <el-progress :percentage="executingProgress" />
      </div>

      <div v-if="result" class="execute-result">
        <div class="result-header" :class="result.status">
          <el-icon v-if="result.status === 'passed'" size="24"><CircleCheck /></el-icon>
          <el-icon v-else-if="result.status === 'failed'" size="24"><CircleClose /></el-icon>
          <span class="result-title">{{ result.status === 'passed' ? '执行通过' : '执行失败' }}</span>
        </div>

        <div class="result-summary">
          <div class="summary-item">
            <span class="label">总步骤</span>
            <span class="value">{{ result.total_steps }}</span>
          </div>
          <div class="summary-item success">
            <span class="label">通过</span>
            <span class="value">{{ result.passed_steps }}</span>
          </div>
          <div class="summary-item error">
            <span class="label">失败</span>
            <span class="value">{{ result.failed_steps }}</span>
          </div>
          <div class="summary-item">
            <span class="label">跳过</span>
            <span class="value">{{ result.skipped_steps }}</span>
          </div>
        </div>

        <div class="step-results">
          <h4>步骤详情</h4>
          <div
            v-for="(step, index) in result.step_results"
            :key="index"
            class="step-result-item"
            :class="step.status"
          >
            <span class="step-num">{{ index + 1 }}</span>
            <span class="step-name">{{ step.step_name }}</span>
            <el-icon v-if="step.status === 'passed'" color="var(--color-success)"><CircleCheck /></el-icon>
            <el-icon v-else-if="step.status === 'failed'" color="var(--color-error)"><CircleClose /></el-icon>
            <el-icon v-else><More /></el-icon>
          </div>
        </div>
      </div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Loading, CircleCheck, CircleClose, More } from '@element-plus/icons-vue'
import { useTestCaseStore } from '@/stores/testcase'
import { useEnvironmentStore } from '@/stores/environment'
import type { TestCase } from '@/types'

const props = defineProps<{
  modelValue: boolean
  testcase: TestCase | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const testCaseStore = useTestCaseStore()
const environmentStore = useEnvironmentStore()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const { environments } = environmentStore

const environmentId = ref<number | null>(null)
const failStrategy = ref('stop')
const saveRecord = ref(true)
const executing = ref(false)
const executingProgress = ref(0)
const result = ref<any>(null)

watch(() => props.testcase, (tc) => {
  if (tc) {
    // Reset state
    executing.value = false
    result.value = null
    executingProgress.value = 0
  }
}, { immediate: true })

const startExecute = async () => {
  if (!props.testcase?.id || !environmentId.value) return

  executing.value = true
  executingProgress.value = 0

  try {
    const res = await testCaseStore.executeTestCase(props.testcase.id, {
      environment_id: environmentId.value,
      fail_strategy: failStrategy.value,
      save_record: saveRecord.value,
    })
    result.value = res
    executingProgress.value = 100
  } catch (e) {
    console.error('Execute failed:', e)
  } finally {
    executing.value = false
  }
}

// Load environments on mount
environmentStore.fetchEnvironments()
</script>

<style scoped>
.execute-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.execute-form {
  flex: 1;
}

.execute-actions {
  margin-top: var(--spacing-xl);
  text-align: center;
}

.executing-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
  padding: var(--spacing-2xl);
}

.executing-state span {
  font-size: 1.125rem;
  color: var(--color-text-secondary);
}

.executing-state .el-progress {
  width: 80%;
}

.execute-result {
  flex: 1;
  overflow-y: auto;
}

.result-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  border-radius: var(--radius-lg);
  margin-bottom: var(--spacing-lg);
}

.result-header.passed {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.result-header.failed {
  background: var(--color-error-bg);
  color: var(--color-error);
}

.result-title {
  font-size: 1.125rem;
  font-weight: 600;
}

.result-summary {
  display: flex;
  gap: var(--spacing-lg);
  padding: var(--spacing-md);
  background: var(--color-bg-hover);
  border-radius: var(--radius-lg);
  margin-bottom: var(--spacing-lg);
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
}

.summary-item .label {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}

.summary-item .value {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.summary-item.success .value {
  color: var(--color-success);
}

.summary-item.error .value {
  color: var(--color-error);
}

.step-results {
  margin-top: var(--spacing-lg);
}

.step-results h4 {
  font-size: 0.9375rem;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-md);
}

.step-result-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-xs);
}

.step-result-item.passed {
  background: var(--color-success-bg);
}

.step-result-item.failed {
  background: var(--color-error-bg);
}

.step-num {
  width: 24px;
  height: 24px;
  background: var(--color-bg-card);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
}

.step-name {
  flex: 1;
  font-size: 0.875rem;
}
</style>