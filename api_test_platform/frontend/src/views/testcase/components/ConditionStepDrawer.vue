<template>
  <el-drawer
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="编辑条件步骤"
    size="600px"
    :close-on-click-modal="false"
    direction="rtl"
  >
    <div class="condition-step-drawer">
      <el-form label-position="top" size="small">
        <el-form-item label="条件类型">
          <el-radio-group v-model="formData.condition_type">
            <el-radio-button value="if">IF</el-radio-button>
            <el-radio-button value="for">FOR</el-radio-button>
            <el-radio-button value="while">WHILE</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <template v-if="formData.condition_type === 'if'">
          <el-form-item label="步骤名称">
            <el-input v-model="formData.step_name" placeholder="IF条件步骤" />
          </el-form-item>
          <div class="condition-if-config">
            <div class="condition-items">
              <div v-for="(cond, idx) in ifConditions" :key="idx" class="condition-item">
                <el-input v-model="cond.expression" placeholder="条件表达式，如 ${status} == 200" style="flex: 1" />
                <el-button v-if="ifConditions.length > 1" type="danger" text size="small" @click="ifConditions.splice(idx, 1)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
            <div v-if="ifConditions.length > 1" class="condition-logic">
              <el-radio-group v-model="ifLogicOperator" size="small">
                <el-radio-button value="and">AND (全部满足)</el-radio-button>
                <el-radio-button value="or">OR (任一满足)</el-radio-button>
              </el-radio-group>
            </div>
            <el-button type="primary" text size="small" @click="ifConditions.push({ expression: '' })">
              <el-icon><Plus /></el-icon> 添加条件
            </el-button>
            <div class="condition-hint">当{{ ifLogicOperator === 'and' ? '所有' : '任一' }}条件满足时执行子步骤</div>
            <el-input v-model="conditionDescription" placeholder="条件描述（可选）" style="margin-top: 8px" />
          </div>
        </template>

        <template v-if="formData.condition_type === 'for'">
          <el-form-item label="步骤名称">
            <el-input v-model="formData.step_name" placeholder="FOR循环步骤" />
          </el-form-item>
          <div class="condition-for-config">
            <el-radio-group v-model="forMode" size="small" style="margin-bottom: 12px">
              <el-radio-button value="count">循环次数</el-radio-button>
              <el-radio-button value="items">循环项</el-radio-button>
            </el-radio-group>

            <div v-if="forMode === 'count'">
              <el-form label-position="top">
                <el-form-item label="循环变量">
                  <el-input v-model="forVariable" placeholder="如 i" />
                </el-form-item>
                <el-form-item label="循环次数">
                  <el-input-number v-model="forCount" :min="1" :max="10000" />
                </el-form-item>
              </el-form>
            </div>

            <div v-if="forMode === 'items'">
              <el-form label-position="top">
                <el-form-item label="循环变量">
                  <el-input v-model="forVariable" placeholder="如 item" />
                </el-form-item>
                <el-form-item label="循环项来源">
                  <el-radio-group v-model="forItemsSource" size="small">
                    <el-radio value="variable">从变量获取</el-radio>
                    <el-radio value="custom">自定义数组</el-radio>
                  </el-radio-group>
                </el-form-item>
                <el-form-item v-if="forItemsSource === 'variable'" label="变量名">
                  <el-input v-model="forItemsVariable" placeholder="如 ${items}" />
                </el-form-item>
                <el-form-item v-if="forItemsSource === 'custom'" label="JSON数组">
                  <el-input v-model="forItemsCustom" type="textarea" :rows="3" placeholder='如 ["a","b","c"] 或 [1,2,3]' />
                </el-form-item>
              </el-form>
            </div>

            <div class="condition-hint">循环变量可在子步骤中通过 ${变量名} 引用</div>
            <el-input v-model="conditionDescription" placeholder="条件描述（可选）" style="margin-top: 8px" />
          </div>
        </template>

        <template v-if="formData.condition_type === 'while'">
          <el-form-item label="步骤名称">
            <el-input v-model="formData.step_name" placeholder="WHILE循环步骤" />
          </el-form-item>
          <div class="condition-while-config">
            <el-radio-group v-model="whileMode" size="small" style="margin-bottom: 12px">
              <el-radio-button value="expression">条件表达式</el-radio-button>
              <el-radio-button value="count">循环次数</el-radio-button>
            </el-radio-group>

            <div v-if="whileMode === 'expression'">
              <el-form label-position="top">
                <el-form-item label="循环条件">
                  <el-input v-model="whileExpression" placeholder="如 ${retry_count} < 3" />
                </el-form-item>
                <el-form-item label="最大循环次数">
                  <el-input-number v-model="whileMaxCount" :min="1" :max="10000" />
                </el-form-item>
              </el-form>
              <div class="condition-hint">循环执行子步骤直到条件不满足或达到最大次数</div>
            </div>

            <div v-if="whileMode === 'count'">
              <el-form label-position="top">
                <el-form-item label="循环次数">
                  <el-input-number v-model="whileFixedCount" :min="1" :max="10000" />
                </el-form-item>
              </el-form>
              <div class="condition-hint">固定循环指定次数</div>
            </div>

            <el-input v-model="conditionDescription" placeholder="条件描述（可选）" style="margin-top: 8px" />
          </div>
        </template>
      </el-form>
    </div>

    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" @click="handleSave">确定</el-button>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { reactive, watch, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Delete, Plus } from '@element-plus/icons-vue'
import type { TestCaseStep, StepExecutionCondition } from '@/types/testcase'

const props = defineProps<{
  modelValue: boolean
  step: TestCaseStep | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  save: [step: TestCaseStep]
}>()

const formData = reactive({
  condition_type: 'if' as 'if' | 'for' | 'while',
  step_name: '',
  enabled: true
})

const ifConditions = ref([{ expression: '' }])
const ifLogicOperator = ref<'and' | 'or'>('and')
const conditionDescription = ref('')

const forMode = ref<'count' | 'items'>('count')
const forVariable = ref('i')
const forCount = ref(3)
const forItemsSource = ref<'variable' | 'custom'>('custom')
const forItemsVariable = ref('')
const forItemsCustom = ref('')

const whileMode = ref<'expression' | 'count'>('expression')
const whileExpression = ref('')
const whileMaxCount = ref(100)
const whileFixedCount = ref(3)

watch(() => props.modelValue, (val) => {
  if (val && props.step) {
    const cond = props.step.execution_condition
    formData.condition_type = (props.step.step_type as 'if' | 'for' | 'while') || 'if'
    formData.step_name = props.step.step_name || ''
    formData.enabled = props.step.enabled
    conditionDescription.value = cond?.description || ''

    if (formData.condition_type === 'if') {
      if (cond?.conditions && Array.isArray(cond.conditions)) {
        ifConditions.value = cond.conditions.map((c: string) => ({ expression: c }))
      } else if (cond?.expression) {
        ifConditions.value = [{ expression: cond.expression }]
      } else {
        ifConditions.value = [{ expression: '' }]
      }
      ifLogicOperator.value = cond?.logic || 'and'
    } else if (formData.condition_type === 'for') {
      if (cond?.for_mode) {
        forMode.value = cond.for_mode
      } else {
        forMode.value = cond?.loop_items ? 'items' : 'count'
      }
      forVariable.value = cond?.loop_variable || 'i'
      forCount.value = cond?.loop_count || 3
      if (cond?.loop_items_source) {
        forItemsSource.value = cond.loop_items_source
      } else {
        forItemsSource.value = 'custom'
      }
      forItemsVariable.value = cond?.loop_items_variable || ''
      forItemsCustom.value = cond?.loop_items || ''
    } else if (formData.condition_type === 'while') {
      if (cond?.while_mode) {
        whileMode.value = cond.while_mode
      } else {
        whileMode.value = cond?.expression ? 'expression' : 'count'
      }
      whileExpression.value = cond?.expression || ''
      whileMaxCount.value = cond?.loop_count || 100
      whileFixedCount.value = cond?.loop_count || 3
    }
  } else if (val) {
    formData.condition_type = 'if'
    formData.step_name = ''
    formData.enabled = true
    ifConditions.value = [{ expression: '' }]
    ifLogicOperator.value = 'and'
    conditionDescription.value = ''
    forMode.value = 'count'
    forVariable.value = 'i'
    forCount.value = 3
    forItemsSource.value = 'custom'
    forItemsVariable.value = ''
    forItemsCustom.value = ''
    whileMode.value = 'expression'
    whileExpression.value = ''
    whileMaxCount.value = 100
    whileFixedCount.value = 3
  }
})

function handleSave() {
  const condition: StepExecutionCondition = {
    type: formData.condition_type
  }

  if (formData.condition_type === 'if') {
    condition.logic = ifLogicOperator.value
    condition.conditions = ifConditions.value.map(c => c.expression).filter(e => e.trim())
    condition.expression = ifConditions.value.map(c => c.expression).join(ifLogicOperator.value === 'and' ? ' && ' : ' || ')
    condition.description = conditionDescription.value
  } else if (formData.condition_type === 'for') {
    condition.for_mode = forMode.value
    condition.loop_variable = forVariable.value
    condition.description = conditionDescription.value
    if (forMode.value === 'count') {
      condition.loop_count = forCount.value
    } else {
      condition.loop_items_source = forItemsSource.value
      if (forItemsSource.value === 'variable') {
        condition.loop_items_variable = forItemsVariable.value
      } else {
        condition.loop_items = forItemsCustom.value
      }
    }
  } else if (formData.condition_type === 'while') {
    condition.while_mode = whileMode.value
    condition.description = conditionDescription.value
    if (whileMode.value === 'expression') {
      condition.expression = whileExpression.value
      condition.loop_count = whileMaxCount.value
    } else {
      condition.loop_count = whileFixedCount.value
    }
  }

  const step: TestCaseStep = {
    step_type: formData.condition_type,
    step_name: formData.step_name || null,
    enabled: formData.enabled,
    sort_order: props.step?.sort_order || 0,
    execution_condition: condition,
    api_id: null,
    parent_step_id: props.step?.parent_step_id || null,
    children: props.step?.children || []
  }

  if (props.step?.id) step.id = props.step.id
  if (props.step?.test_case_id) step.test_case_id = props.step.test_case_id

  emit('save', step)
  emit('update:modelValue', false)
  ElMessage.success('条件步骤已保存')
}
</script>

<style scoped>
.condition-step-drawer {
  padding: 0 4px;
}

.condition-hint {
  color: #909399;
  font-size: 12px;
  line-height: 1.6;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 16px;
}

.condition-if-config {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.condition-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.condition-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.condition-logic {
  margin: 4px 0;
}

.condition-for-config {
  display: flex;
  flex-direction: column;
}

.condition-while-config {
  display: flex;
  flex-direction: column;
}
</style>
