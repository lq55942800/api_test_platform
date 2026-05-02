<template>
  <el-form label-width="120px" label-position="left" size="small">
    <el-form-item label="输出请求级变量">
      <el-switch v-model="config.output_variables" @change="emitUpdate" />
    </el-form-item>
    <el-form-item label="输出环境变量">
      <el-switch v-model="config.output_environment_vars" @change="emitUpdate" />
    </el-form-item>
    <el-form-item label="输出全局变量">
      <el-switch v-model="config.output_global_vars" @change="emitUpdate" />
    </el-form-item>
    <el-form-item label="输出响应信息">
      <el-switch v-model="config.output_response_info" @change="emitUpdate" />
    </el-form-item>
    <el-form-item label="过滤正则">
      <el-input v-model="config.filter_pattern" placeholder="变量名过滤正则（为空则输出全部）" @input="emitUpdate" />
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
  output_variables: true,
  output_environment_vars: false,
  output_global_vars: false,
  output_response_info: true,
  filter_pattern: '',
  ...props.modelValue
})

watch(() => props.modelValue, (val) => {
  Object.assign(config, {
    output_variables: true, output_environment_vars: false, output_global_vars: false, output_response_info: true, filter_pattern: '', ...val
  })
}, { deep: true })

function emitUpdate() {
  emit('update:modelValue', { ...config })
}
</script>
