<template>
  <div class="script-assert-config">
    <div class="script-header">
      <el-tag size="small" type="warning">Python</el-tag>
      <span class="script-hint">通过 context 对象访问请求/响应数据，返回 True/False 或 AssertionResult</span>
    </div>
    <el-input
      v-model="config.script"
      type="textarea"
      :rows="8"
      placeholder="body = context.get_response_body_json()
status = context.get_response_status_code()

if status != 200:
    return False

if body.get('code') != 0:
    return AssertionResult(passed=False, message='业务码错误')

return True"
      @input="emitUpdate"
      class="code-textarea"
    />
    <div class="script-footer">
      <el-form label-width="0" size="small" inline>
        <el-form-item label="">
          超时
          <el-input-number v-model="config.timeout" :min="1000" :max="120000" :step="1000" size="small" style="width: 120px; margin: 0 8px" @change="emitUpdate" />
          ms
        </el-form-item>
        <el-form-item label="">
          失败消息
          <el-input v-model="config.message" placeholder="自定义失败消息" size="small" style="width: 200px; margin-left: 8px" @input="emitUpdate" />
        </el-form-item>
      </el-form>
    </div>
  </div>
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
  script: '',
  timeout: 10000,
  message: '',
  ...props.modelValue
})

watch(() => props.modelValue, (val) => {
  Object.assign(config, { script: '', timeout: 10000, message: '', ...val })
}, { deep: true })

function emitUpdate() {
  emit('update:modelValue', { ...config })
}
</script>

<style scoped>
.script-assert-config {
  width: 100%;
}

.script-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.script-hint {
  color: #909399;
  font-size: 12px;
}

.script-footer {
  margin-top: 8px;
}

.script-footer :deep(.el-form-item) {
  margin-bottom: 0;
  margin-right: 16px;
}

.code-textarea :deep(.el-textarea__inner) {
  font-family: ui-monospace, Consolas, monospace;
  font-size: 13px;
  line-height: 1.6;
  background-color: #1e1e1e;
  color: #d4d4d4;
  border-color: #3c3c3c;
}

.code-textarea :deep(.el-textarea__inner)::placeholder {
  color: #6a9955;
}
</style>
