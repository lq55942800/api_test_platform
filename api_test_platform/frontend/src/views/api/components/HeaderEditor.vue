<template>
  <div class="header-editor">
    <el-table :data="modelValue" border size="small" style="width: 100%">
      <el-table-column label="参数名" min-width="200">
        <template #default="{ row }">
          <el-input v-model="row.name" placeholder="Header名称" size="small" />
        </template>
      </el-table-column>
      <el-table-column label="参数值" min-width="300">
        <template #default="{ row }">
          <el-input v-model="row.default_value" placeholder="Header值" size="small" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="60" align="center" fixed="right">
        <template #default="{ $index }">
          <el-button type="danger" link size="small" @click="handleRemove($index)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-button type="primary" link size="small" @click="handleAdd" class="add-btn">
      <el-icon><Plus /></el-icon>
      添加Header
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { Plus, Delete } from '@element-plus/icons-vue'
import type { ApiParam } from '@/types/api'

const props = withDefaults(defineProps<{
  modelValue: ApiParam[]
}>(), {
  modelValue: () => []
})

const emit = defineEmits<{
  'update:modelValue': [value: ApiParam[]]
}>()

function handleAdd() {
  const newParam: ApiParam = {
    name: '',
    type: 'String',
    required: false,
    default_value: '',
    description: ''
  }
  emit('update:modelValue', [...props.modelValue, newParam])
}

function handleRemove(index: number) {
  const newValue = [...props.modelValue]
  newValue.splice(index, 1)
  emit('update:modelValue', newValue)
}
</script>

<style scoped>
.header-editor {
  width: 100%;
}

.add-btn {
  margin-top: 8px;
}

:deep(.el-table .el-table__cell) {
  padding: 4px 0;
}
</style>
