<template>
  <el-form label-width="100px" label-position="left" size="small">
    <el-form-item label="断言方式">
      <el-select v-model="config.mode" @change="onModeChange">
        <el-option label="包含" value="contains" />
        <el-option label="JSONPath" value="jsonpath" />
        <el-option label="正则表达式" value="regex" />
      </el-select>
    </el-form-item>

    <template v-if="config.mode === 'contains'">
      <el-form-item label="期望内容">
        <el-input v-model="config.expected" type="textarea" :rows="2" placeholder="响应体中应包含的文本" @input="emitUpdate" />
      </el-form-item>
    </template>

    <template v-else-if="config.mode === 'jsonpath'">
      <el-form-item label="JSONPath">
        <el-input v-model="config.expression" placeholder="如 $.data.id" @input="emitUpdate" />
      </el-form-item>
      <el-form-item label="比较方式">
        <el-select v-model="config.operator" @change="emitUpdate">
          <el-option label="等于" value="eq" />
          <el-option label="不等于" value="neq" />
          <el-option label="包含" value="contains" />
          <el-option label="不包含" value="not_contains" />
          <el-option label="大于" value="gt" />
          <el-option label="小于" value="lt" />
          <el-option label="大于等于" value="gte" />
          <el-option label="小于等于" value="lte" />
        </el-select>
      </el-form-item>
      <el-form-item label="期望值">
        <el-input v-model="config.expected" placeholder="提取值的期望值" @input="emitUpdate" />
      </el-form-item>
    </template>

    <template v-else-if="config.mode === 'regex'">
      <el-form-item label="正则表达式">
        <el-input v-model="config.pattern" placeholder="如 &quot;key&quot;:&quot;(.*?)&quot;" @input="emitUpdate" />
      </el-form-item>
      <el-form-item label="匹配规则">
        <el-select v-model="config.match_rule" @change="emitUpdate">
          <el-option label="包含匹配" value="contains" />
          <el-option label="不包含" value="not_contains" />
        </el-select>
      </el-form-item>
    </template>

    <el-form-item label="自定义消息">
      <el-input v-model="config.message" placeholder="断言失败时的自定义消息" @input="emitUpdate" />
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'

const props = defineProps<{
  modelValue: Record<string, any>
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, any>]
}>()

const config = reactive({
  mode: 'contains',
  expected: '',
  expression: '',
  operator: 'eq',
  pattern: '',
  match_rule: 'contains',
  message: '',
  severity: 'critical',
  ...props.modelValue
})

watch(() => props.modelValue, (val) => {
  Object.assign(config, { mode: 'contains', expected: '', expression: '', operator: 'eq', pattern: '', match_rule: 'contains', message: '', severity: 'critical', ...val })
}, { deep: true })

function onModeChange() {
  if (config.mode === 'jsonpath') {
    config.expression = ''
    config.operator = 'eq'
    config.expected = ''
  } else if (config.mode === 'regex') {
    config.pattern = ''
    config.match_rule = 'contains'
  } else {
    config.expected = ''
  }
  emitUpdate()
}

function emitUpdate() {
  emit('update:modelValue', { ...config })
}
</script>
