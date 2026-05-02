<template>
  <el-form label-width="100px" label-position="left" size="small">
    <el-form-item label="比较方式">
      <el-select v-model="config.operator" @change="onOperatorChange">
        <el-option label="等于" value="eq" />
        <el-option label="不等于" value="neq" />
        <el-option label="在列表中" value="in" />
      </el-select>
    </el-form-item>
    <el-form-item v-if="config.operator === 'in'" label="状态码列表">
      <el-select v-model="config.expected_list" multiple filterable allow-create default-first-option placeholder="输入状态码" @change="emitUpdate">
        <el-option v-for="item in commonStatusCodes" :key="item.value" :label="item.label" :value="item.value" />
      </el-select>
    </el-form-item>
    <el-form-item v-else label="期望状态码">
      <el-input-number v-model="config.expected" :min="100" :max="599" @change="emitUpdate" />
    </el-form-item>
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

const commonStatusCodes = [
  { value: 200, label: '200 OK' },
  { value: 201, label: '201 Created' },
  { value: 204, label: '204 No Content' },
  { value: 301, label: '301 Moved' },
  { value: 400, label: '400 Bad Request' },
  { value: 401, label: '401 Unauthorized' },
  { value: 403, label: '403 Forbidden' },
  { value: 404, label: '404 Not Found' },
  { value: 500, label: '500 Server Error' },
]

const config = reactive({
  operator: 'eq',
  expected: 200,
  expected_list: [200] as number[],
  message: '',
  severity: 'critical',
  ...props.modelValue
})

watch(() => props.modelValue, (val) => {
  Object.assign(config, { operator: 'eq', expected: 200, expected_list: [200], message: '', severity: 'critical', ...val })
}, { deep: true })

function onOperatorChange() {
  if (config.operator === 'in' && !config.expected_list?.length) {
    config.expected_list = [200]
  }
  emitUpdate()
}

function emitUpdate() {
  emit('update:modelValue', { ...config })
}
</script>
