<template>
  <el-form label-width="100px" label-position="left" size="small">
    <el-form-item label="触发条件">
      <el-select v-model="config.condition" @change="emitUpdate">
        <el-option label="请求失败时" value="on_failure" />
        <el-option label="请求成功时" value="on_success" />
        <el-option label="总是执行" value="always" />
      </el-select>
    </el-form-item>
    <el-form-item label="执行动作">
      <el-select v-model="config.action" @change="emitUpdate">
        <el-option label="继续" value="continue" />
        <el-option label="跳到下一次迭代" value="next_iteration" />
        <el-option label="跳出循环" value="break_loop" />
        <el-option label="停止测试" value="stop_test" />
        <el-option label="立即停止" value="stop_test_now" />
        <el-option label="重试请求" value="retry" />
      </el-select>
    </el-form-item>
    <el-form-item label="最大重试次数" v-if="config.action === 'retry'">
      <el-input-number v-model="config.max_retries" :min="0" :max="10" @change="emitUpdate" />
    </el-form-item>
    <el-form-item label="重试间隔(ms)" v-if="config.action === 'retry'">
      <el-input-number v-model="config.retry_interval" :min="100" :max="60000" :step="100" @change="emitUpdate" />
    </el-form-item>
    <el-form-item label="自定义消息">
      <el-input v-model="config.custom_message" placeholder="自定义消息（可选）" @input="emitUpdate" />
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
  condition: 'on_failure',
  action: 'continue',
  max_retries: 0,
  retry_interval: 1000,
  custom_message: '',
  ...props.modelValue
})

watch(() => props.modelValue, (val) => {
  Object.assign(config, {
    condition: 'on_failure', action: 'continue', max_retries: 0, retry_interval: 1000, custom_message: '', ...val
  })
}, { deep: true })

function emitUpdate() {
  emit('update:modelValue', { ...config })
}
</script>
