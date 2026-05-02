<template>
  <div class="param-builder-config">
    <el-table :data="params" size="small" border style="width: 100%">
      <el-table-column label="位置" width="100">
        <template #default="{ row }">
          <el-select v-model="row.location" size="small" @change="emitUpdate">
            <el-option label="Query" value="query" />
            <el-option label="Header" value="header" />
            <el-option label="Body" value="body" />
            <el-option label="Cookie" value="cookie" />
          </el-select>
        </template>
      </el-table-column>
      <el-table-column label="参数名" min-width="140">
        <template #default="{ row }">
          <el-input v-model="row.name" placeholder="参数名" size="small" @input="emitUpdate" />
        </template>
      </el-table-column>
      <el-table-column label="参数值" min-width="180">
        <template #default="{ row }">
          <el-input v-model="row.value" placeholder="支持${var}引用" size="small" @input="emitUpdate" />
        </template>
      </el-table-column>
      <el-table-column label="启用" width="55" align="center">
        <template #default="{ row }">
          <el-checkbox v-model="row.enabled" size="small" @change="emitUpdate" />
        </template>
      </el-table-column>
      <el-table-column label="" width="50" align="center">
        <template #default="{ $index }">
          <el-button type="danger" link size="small" @click="removeRow($index)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-button size="small" plain style="margin-top: 8px; width: 100%" @click="addRow">
      <el-icon><Plus /></el-icon>添加参数
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
import type { ParamBuilderItem } from '@/types/api'

const props = defineProps<{
  modelValue: Record<string, any>
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, any>]
}>()

const params = ref<ParamBuilderItem[]>([...(props.modelValue?.params || [])])

watch(() => props.modelValue, (val) => {
  params.value = [...(val?.params || [])]
}, { deep: true })

function addRow() {
  params.value.push({ location: 'query', name: '', value: '', enabled: true })
  emitUpdate()
}

function removeRow(index: number) {
  params.value.splice(index, 1)
  emitUpdate()
}

function emitUpdate() {
  emit('update:modelValue', { ...props.modelValue, params: params.value })
}
</script>

<style scoped>
.param-builder-config {
  width: 100%;
}
</style>
