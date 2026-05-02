<template>
  <el-form label-width="100px" label-position="left" size="small">
    <el-form-item label="引用名称">
      <el-input v-model="config.reference_name" placeholder="引用名称" @input="emitUpdate" />
    </el-form-item>
    <el-form-item label="正则表达式">
      <el-input v-model="config.regex" placeholder="需包含捕获组 ()" @input="emitUpdate" />
    </el-form-item>
    <el-form-item label="参数名组号">
      <el-input-number v-model="config.param_name_group" :min="1" :max="20" @change="emitUpdate" />
    </el-form-item>
    <el-form-item label="参数值组号">
      <el-input-number v-model="config.param_value_group" :min="1" :max="20" @change="emitUpdate" />
    </el-form-item>
    <el-form-item label="应用范围">
      <el-select v-model="config.apply_to" @change="emitUpdate">
        <el-option label="Body" value="body" />
        <el-option label="Query" value="query" />
        <el-option label="Header" value="header" />
        <el-option label="全部" value="all" />
      </el-select>
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
  reference_name: '',
  regex: '',
  param_name_group: 1,
  param_value_group: 2,
  apply_to: 'all',
  ...props.modelValue
})

watch(() => props.modelValue, (val) => {
  Object.assign(config, {
    reference_name: '', regex: '', param_name_group: 1, param_value_group: 2, apply_to: 'all', ...val
  })
}, { deep: true })

function emitUpdate() {
  emit('update:modelValue', { ...config })
}
</script>
