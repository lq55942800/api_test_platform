<template>
  <el-form label-width="100px" label-position="left" size="small">
    <el-form-item label="目标参数名">
      <el-input v-model="config.target_param" placeholder="参数名称" @input="emitUpdate" />
    </el-form-item>
    <el-form-item label="参数位置">
      <el-select v-model="config.target_location" @change="emitUpdate">
        <el-option label="Body" value="body" />
        <el-option label="Query" value="query" />
        <el-option label="Header" value="header" />
        <el-option label="Path" value="path" />
        <el-option label="Cookie" value="cookie" />
      </el-select>
    </el-form-item>
    <el-form-item label="表达式">
      <el-input
        v-model="config.expression"
        type="textarea"
        :rows="3"
        placeholder="支持变量引用 ${变量名} 和内置函数 ${__function()}"
        @input="emitUpdate"
      />
    </el-form-item>
    <el-form-item label="表达式说明">
      <el-input v-model="config.description" placeholder="表达式说明（可选）" @input="emitUpdate" />
    </el-form-item>
    <el-form-item label="变量缺失处理">
      <el-select v-model="config.on_var_missing" @change="emitUpdate">
        <el-option label="使用默认值" value="use_default" />
        <el-option label="终止执行" value="abort" />
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
  target_param: '',
  target_location: 'body',
  expression: '',
  description: '',
  on_var_missing: 'use_default',
  ...props.modelValue
})

watch(() => props.modelValue, (val) => {
  Object.assign(config, { target_param: '', target_location: 'body', expression: '', description: '', on_var_missing: 'use_default', ...val })
}, { deep: true })

function emitUpdate() {
  emit('update:modelValue', { ...config })
}
</script>
