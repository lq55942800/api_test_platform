<template>
  <div class="key-value-editor">
    <div class="kv-header">
      <span class="kv-col-key">Key</span>
      <span class="kv-col-value">Value</span>
      <span class="kv-col-desc">描述</span>
      <span class="kv-col-actions"></span>
    </div>
    <div class="kv-body">
      <div v-for="(item, index) in modelValue" :key="index" class="kv-row">
        <el-input v-model="item.key" placeholder="参数名" class="kv-input-key" />
        <el-input v-model="item.value" placeholder="参数值" class="kv-input-value" />
        <el-input v-model="item.description" placeholder="描述" class="kv-input-desc" />
        <el-button
          type="danger"
          :icon="Delete"
          circle
          plain
          @click="removeRow(index)"
        />
      </div>
    </div>
    <el-button type="primary" plain :icon="Plus" @click="addRow">
      添加参数
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { Delete, Plus } from '@element-plus/icons-vue'

interface KeyValueItem {
  key: string
  value: string
  description?: string
}

const props = defineProps<{
  modelValue: KeyValueItem[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: KeyValueItem[]]
}>()

const addRow = () => {
  emit('update:modelValue', [...props.modelValue, { key: '', value: '', description: '' }])
}

const removeRow = (index: number) => {
  const newList = [...props.modelValue]
  newList.splice(index, 1)
  emit('update:modelValue', newList)
}
</script>

<style scoped>
.key-value-editor {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.kv-header {
  display: flex;
  gap: var(--spacing-sm);
  padding: 0 var(--spacing-xs);
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  font-weight: 500;
}

.kv-col-key { width: 140px; }
.kv-col-value { flex: 1; }
.kv-col-desc { width: 160px; }
.kv-col-actions { width: 40px; }

.kv-body {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.kv-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.kv-input-key { width: 140px; }
.kv-input-value { flex: 1; }
.kv-input-desc { width: 160px; }
</style>