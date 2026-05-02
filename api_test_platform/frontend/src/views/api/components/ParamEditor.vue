<template>
  <div class="param-editor">
    <el-table :data="modelValue" border size="small" style="width: 100%">
      <el-table-column label="参数名" min-width="150">
        <template #default="{ row, $index }">
          <el-input v-model="row.name" placeholder="参数名" size="small" />
        </template>
      </el-table-column>
      <el-table-column label="类型" width="120" v-if="showType">
        <template #default="{ row }">
          <el-select v-model="row.type" placeholder="类型" size="small">
            <el-option
              v-for="pt in PARAM_TYPES"
              :key="pt.value"
              :label="pt.label"
              :value="pt.value"
            />
          </el-select>
        </template>
      </el-table-column>
      <el-table-column label="必填" width="60" align="center">
        <template #default="{ row }">
          <el-checkbox v-model="row.required" size="small" />
        </template>
      </el-table-column>
      <el-table-column label="默认值" min-width="120">
        <template #default="{ row }">
          <el-input v-model="row.default_value" placeholder="默认值" size="small" />
        </template>
      </el-table-column>
      <el-table-column label="描述" min-width="150">
        <template #default="{ row }">
          <el-input v-model="row.description" placeholder="描述" size="small" />
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
      添加参数
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { Plus, Delete } from '@element-plus/icons-vue'
import { PARAM_TYPES, ParamType } from '@/types/api'
import type { ApiParam } from '@/types/api'

const props = withDefaults(defineProps<{
  modelValue: ApiParam[]
  showType?: boolean
}>(), {
  modelValue: () => [],
  showType: false
})

const emit = defineEmits<{
  'update:modelValue': [value: ApiParam[]]
}>()

function handleAdd() {
  const newParam: ApiParam = {
    name: '',
    type: ParamType.STRING,
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
.param-editor {
  width: 100%;
}

.add-btn {
  margin-top: 8px;
}

:deep(.el-table .el-table__cell) {
  padding: 4px 0;
}
</style>
