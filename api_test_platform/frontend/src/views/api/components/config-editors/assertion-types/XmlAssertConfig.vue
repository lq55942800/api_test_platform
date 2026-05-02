<template>
  <el-form label-width="100px" label-position="left" size="small">
    <el-form-item label="自定义消息">
      <el-input v-model="config.message" placeholder="响应体不是合法的XML" @input="emitUpdate" />
    </el-form-item>
    <div class="info-tip">
      此断言仅验证响应数据是否为格式正确的XML，无需额外配置。
    </div>
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
  message: '',
  ...props.modelValue
})

watch(() => props.modelValue, (val) => {
  Object.assign(config, { message: '', ...val })
}, { deep: true })

function emitUpdate() {
  emit('update:modelValue', { ...config })
}
</script>

<style scoped>
.info-tip {
  color: #909399;
  font-size: 12px;
  padding: 8px 12px;
  background-color: #f9fafb;
  border-radius: 4px;
}
</style>
