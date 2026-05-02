<template>
  <el-form label-width="100px" label-position="left" size="small">
    <el-form-item label="响应头名称">
      <el-input v-model="config.header_name" placeholder="如 Content-Type" @input="emitUpdate" />
    </el-form-item>
    <el-form-item label="比较方式">
      <el-select v-model="config.operator" @change="emitUpdate">
        <el-option label="包含" value="contains" />
        <el-option label="不包含" value="not_contains" />
        <el-option label="等于" value="eq" />
        <el-option label="不等于" value="neq" />
      </el-select>
    </el-form-item>
    <el-form-item label="期望值">
      <el-input v-model="config.expected" placeholder="期望的响应头值" @input="emitUpdate" />
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
  header_name: '',
  operator: 'contains',
  expected: '',
  message: '',
  severity: 'critical',
  ...props.modelValue
})

watch(() => props.modelValue, (val) => {
  Object.assign(config, { header_name: '', operator: 'contains', expected: '', message: '', severity: 'critical', ...val })
}, { deep: true })

function emitUpdate() {
  emit('update:modelValue', { ...config })
}
</script>
