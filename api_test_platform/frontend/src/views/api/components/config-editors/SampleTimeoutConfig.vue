<template>
  <el-form label-width="100px" label-position="left" size="small">
    <el-form-item label="超时时间(ms)">
      <el-input-number v-model="config.timeout" :min="1000" :max="600000" :step="1000" @change="emitUpdate" />
    </el-form-item>
    <el-form-item label="超时行为">
      <el-select v-model="config.on_timeout" @change="emitUpdate">
        <el-option label="标记失败" value="mark_failed" />
        <el-option label="强制中断" value="abort" />
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
  timeout: 60000,
  on_timeout: 'mark_failed',
  ...props.modelValue
})

watch(() => props.modelValue, (val) => {
  Object.assign(config, {
    timeout: 60000, on_timeout: 'mark_failed', ...val
  })
}, { deep: true })

function emitUpdate() {
  emit('update:modelValue', { ...config })
}
</script>
