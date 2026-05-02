<template>
  <el-form label-width="100px" label-position="left" size="small">
    <el-form-item label="检查字段">
      <el-select v-model="config.field" @change="emitUpdate">
        <el-option label="响应体" value="response_body" />
        <el-option label="响应头" value="response_headers" />
        <el-option label="响应码" value="response_code" />
        <el-option label="请求数据" value="request_data" />
      </el-select>
    </el-form-item>
    <el-form-item label="运算符">
      <el-select v-model="config.operator" @change="emitUpdate">
        <el-option label="等于" value="equals" />
        <el-option label="不等于" value="not_equals" />
        <el-option label="大于" value="greater_than" />
        <el-option label="小于" value="less_than" />
        <el-option label="大于等于" value="greater_or_equal" />
        <el-option label="小于等于" value="less_or_equal" />
      </el-select>
    </el-form-item>
    <el-form-item label="期望大小">
      <el-input-number v-model="config.expected" :min="0" :step="100" @change="emitUpdate" />
    </el-form-item>
    <el-form-item label="大小单位">
      <el-select v-model="config.unit" @change="emitUpdate">
        <el-option label="字节(byte)" value="byte" />
        <el-option label="KB" value="kb" />
        <el-option label="MB" value="mb" />
      </el-select>
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

const config = reactive({
  field: 'response_body',
  operator: 'less_than',
  expected: 10240,
  unit: 'byte',
  message: '',
  ...props.modelValue
})

watch(() => props.modelValue, (val) => {
  Object.assign(config, { field: 'response_body', operator: 'less_than', expected: 10240, unit: 'byte', message: '', ...val })
}, { deep: true })

function emitUpdate() {
  emit('update:modelValue', { ...config })
}
</script>
