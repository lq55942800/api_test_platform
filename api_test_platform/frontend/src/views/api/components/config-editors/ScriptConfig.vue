<template>
  <div class="script-config">
    <div class="script-header">
      <el-tag size="small" type="warning">Python</el-tag>
      <span class="script-hint">通过 context 对象访问请求/响应数据和变量</span>
    </div>
    <el-input
      v-model="config.script"
      type="textarea"
      :rows="10"
      placeholder="def execute(context):
    # 获取变量
    token = context.get_variable('token')
    
    # 设置变量
    context.set_variable('new_var', 'value')
    
    # 获取请求数据
    url = context.get_request_url()
    headers = context.get_request_headers()
    
    # 获取响应数据（仅后置脚本可用）
    status = context.get_response_status_code()
    body = context.get_response_body_json()
    
    # 输出日志
    context.log('debug info')"
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
          错误处理
          <el-select v-model="config.on_error" size="small" style="width: 110px; margin-left: 8px" @change="emitUpdate">
            <el-option label="终止执行" value="abort" />
            <el-option label="跳过继续" value="skip" />
          </el-select>
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
  on_error: 'abort',
  ...props.modelValue
})

watch(() => props.modelValue, (val) => {
  Object.assign(config, { script: '', timeout: 10000, on_error: 'abort', ...val })
}, { deep: true })

function emitUpdate() {
  emit('update:modelValue', { ...config })
}
</script>

<style scoped>
.script-config {
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
