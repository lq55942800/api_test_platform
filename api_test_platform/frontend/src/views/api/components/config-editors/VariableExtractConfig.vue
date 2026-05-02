<template>
  <el-form label-width="100px" label-position="left" size="small">
    <el-form-item label="变量来源">
      <el-select v-model="config.source" @change="emitUpdate">
        <el-option label="环境变量" value="environment" />
        <el-option label="全局变量" value="global" />
        <el-option label="上一步响应" value="previous_response" />
        <el-option label="CSV文件" value="csv_file" />
        <el-option label="JSON文件" value="json_file" />
      </el-select>
    </el-form-item>
    <el-form-item label="来源步骤ID" v-if="config.source === 'previous_response'">
      <el-input v-model="config.source_step_id" placeholder="上一步操作/接口的ID" @input="emitUpdate" />
    </el-form-item>
    <el-form-item label="提取方式">
      <el-select v-model="config.extract_type" @change="emitUpdate">
        <el-option v-for="et in EXTRACT_TYPES" :key="et.value" :label="et.label" :value="et.value" />
      </el-select>
    </el-form-item>
    <el-form-item label="表达式">
      <el-input v-model="config.expression" placeholder="提取表达式" @input="emitUpdate" />
    </el-form-item>
    <el-form-item label="目标变量名">
      <el-input v-model="config.target_variable" placeholder="提取结果存入的变量名" @input="emitUpdate" />
    </el-form-item>
    <el-form-item label="变量作用域">
      <el-select v-model="config.target_scope" @change="emitUpdate">
        <el-option v-for="vs in VARIABLE_SCOPES" :key="vs.value" :label="vs.label" :value="vs.value" />
      </el-select>
    </el-form-item>
    <el-form-item label="默认值">
      <el-input v-model="config.default_value" placeholder="提取为空时使用的默认值" @input="emitUpdate" />
    </el-form-item>
    <el-form-item label="错误处理策略">
      <el-select v-model="config.on_error" @change="emitUpdate">
        <el-option label="使用默认值" value="use_default" />
        <el-option label="终止执行" value="abort" />
        <el-option label="跳过此操作" value="skip" />
      </el-select>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import { EXTRACT_TYPES, VARIABLE_SCOPES } from '@/types/api'

const props = defineProps<{
  modelValue: Record<string, any>
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, any>]
}>()

const config = reactive({
  source: 'environment',
  source_step_id: '',
  extract_type: 'jsonpath',
  expression: '',
  target_variable: '',
  target_scope: 'request',
  default_value: '',
  on_error: 'use_default',
  ...props.modelValue
})

watch(() => props.modelValue, (val) => {
  Object.assign(config, {
    source: 'environment', source_step_id: '', extract_type: 'jsonpath', expression: '', target_variable: '', target_scope: 'request', default_value: '', on_error: 'use_default', ...val
  })
}, { deep: true })

function emitUpdate() {
  emit('update:modelValue', { ...config })
}
</script>
