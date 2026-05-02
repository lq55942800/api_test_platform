<template>
  <el-form label-width="100px" label-position="left" size="small">
    <el-form-item label="合并策略">
      <el-select v-model="config.action" @change="emitUpdate">
        <el-option label="合并（保留已有）" value="merge" />
        <el-option label="替换（覆盖已有）" value="replace" />
        <el-option label="追加" value="append" />
      </el-select>
    </el-form-item>
    <el-divider content-position="left">请求头列表</el-divider>
    <div class="header-list">
      <div v-for="(header, index) in config.headers" :key="index" class="header-row">
        <el-input v-model="header.name" size="small" placeholder="请求头名称" style="width: 160px" @input="emitUpdate" />
        <el-input v-model="header.value" size="small" placeholder="值（支持变量引用）" style="width: 220px" @input="emitUpdate" />
        <el-switch v-model="header.enabled" size="small" @change="emitUpdate" />
        <el-button type="danger" link size="small" @click="removeHeader(index)">
          <el-icon><Delete /></el-icon>
        </el-button>
      </div>
      <el-button type="primary" link size="small" @click="addHeader">添加请求头</el-button>
    </div>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import { Delete } from '@element-plus/icons-vue'

const props = defineProps<{
  modelValue: Record<string, any>
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, any>]
}>()

const config = reactive({
  action: 'merge',
  headers: [] as { name: string; value: string; enabled: boolean }[],
  ...props.modelValue
})

watch(() => props.modelValue, (val) => {
  Object.assign(config, {
    action: 'merge', headers: [], ...val
  })
}, { deep: true })

function addHeader() {
  if (!config.headers) config.headers = []
  config.headers.push({ name: '', value: '', enabled: true })
  emitUpdate()
}

function removeHeader(index: number) {
  config.headers.splice(index, 1)
  emitUpdate()
}

function emitUpdate() {
  emit('update:modelValue', { ...config })
}
</script>

<style scoped>
.header-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.header-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
