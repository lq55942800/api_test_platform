<template>
  <el-form label-width="100px" label-position="left" size="small">
    <el-form-item label="条件类型">
      <el-select v-model="config.condition_type" @change="emitUpdate">
        <el-option label="变量比较" value="variable" />
        <el-option label="表达式求值" value="expression" />
        <el-option label="自定义脚本" value="script" />
      </el-select>
    </el-form-item>
    <template v-if="config.condition_type === 'variable'">
      <el-form-item label="变量名">
        <el-input v-model="config.variable_name" placeholder="变量名称" @input="emitUpdate" />
      </el-form-item>
      <el-form-item label="运算符">
        <el-select v-model="config.operator" @change="emitUpdate">
          <el-option v-for="op in COMPARISON_OPERATORS" :key="op.value" :label="op.label" :value="op.value" />
        </el-select>
      </el-form-item>
      <el-form-item label="期望值">
        <el-input v-model="config.expected_value" placeholder="期望值" @input="emitUpdate" />
      </el-form-item>
    </template>
    <template v-if="config.condition_type === 'expression'">
      <el-form-item label="条件表达式">
        <el-input v-model="config.expression" type="textarea" :rows="2" placeholder="条件表达式，返回布尔值" @input="emitUpdate" />
      </el-form-item>
    </template>
    <template v-if="config.condition_type === 'script'">
      <el-form-item label="Python脚本">
        <el-input v-model="config.script" type="textarea" :rows="4" placeholder="返回 True/False 的Python脚本" @input="emitUpdate" />
      </el-form-item>
    </template>
    <el-form-item label="求值方式">
      <el-select v-model="config.evaluate_type" @change="emitUpdate">
        <el-option label="全部求值" value="all" />
        <el-option label="首个匹配" value="first_match" />
      </el-select>
    </el-form-item>
    <el-divider content-position="left">条件为真时执行 (Then)</el-divider>
    <div class="sub-action-list">
      <div v-for="(action, index) in config.then_actions" :key="'then-' + index" class="sub-action-item">
        <el-select v-model="action.type" size="small" style="width: 120px" @change="emitUpdate">
          <el-option label="设置变量" value="set_variable" />
        </el-select>
        <el-input v-model="action.config.variable_name" size="small" placeholder="变量名" style="width: 120px" @input="emitUpdate" />
        <el-input v-model="action.config.variable_value" size="small" placeholder="变量值" style="width: 120px" @input="emitUpdate" />
        <el-button type="danger" link size="small" @click="removeThenAction(index)">
          <el-icon><Delete /></el-icon>
        </el-button>
      </div>
      <el-button type="primary" link size="small" @click="addThenAction">添加Then操作</el-button>
    </div>
    <el-divider content-position="left">条件为假时执行 (Else)</el-divider>
    <div class="sub-action-list">
      <div v-for="(action, index) in config.else_actions" :key="'else-' + index" class="sub-action-item">
        <el-select v-model="action.type" size="small" style="width: 120px" @change="emitUpdate">
          <el-option label="设置变量" value="set_variable" />
        </el-select>
        <el-input v-model="action.config.variable_name" size="small" placeholder="变量名" style="width: 120px" @input="emitUpdate" />
        <el-input v-model="action.config.variable_value" size="small" placeholder="变量值" style="width: 120px" @input="emitUpdate" />
        <el-button type="danger" link size="small" @click="removeElseAction(index)">
          <el-icon><Delete /></el-icon>
        </el-button>
      </div>
      <el-button type="primary" link size="small" @click="addElseAction">添加Else操作</el-button>
    </div>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import { Delete } from '@element-plus/icons-vue'
import { COMPARISON_OPERATORS } from '@/types/api'

const props = defineProps<{
  modelValue: Record<string, any>
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, any>]
}>()

const config = reactive({
  condition_type: 'variable',
  variable_name: '',
  operator: 'equals',
  expected_value: '',
  expression: '',
  script: '',
  then_actions: [] as any[],
  else_actions: [] as any[],
  evaluate_type: 'all',
  ...props.modelValue
})

watch(() => props.modelValue, (val) => {
  Object.assign(config, {
    condition_type: 'variable', variable_name: '', operator: 'equals', expected_value: '', expression: '', script: '', then_actions: [], else_actions: [], evaluate_type: 'all', ...val
  })
}, { deep: true })

function addThenAction() {
  if (!config.then_actions) config.then_actions = []
  config.then_actions.push({ type: 'set_variable', config: { variable_name: '', variable_value: '', scope: 'request' } })
  emitUpdate()
}

function removeThenAction(index: number) {
  config.then_actions.splice(index, 1)
  emitUpdate()
}

function addElseAction() {
  if (!config.else_actions) config.else_actions = []
  config.else_actions.push({ type: 'set_variable', config: { variable_name: '', variable_value: '', scope: 'request' } })
  emitUpdate()
}

function removeElseAction(index: number) {
  config.else_actions.splice(index, 1)
  emitUpdate()
}

function emitUpdate() {
  emit('update:modelValue', { ...config })
}
</script>

<style scoped>
.sub-action-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.sub-action-item {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
