<template>
  <div class="set-variable-config">
    <el-table :data="variables" size="small" border style="width: 100%">
      <el-table-column label="变量名" min-width="140">
        <template #default="{ row }">
          <el-input v-model="row.name" placeholder="变量名" size="small" @input="emitUpdate" />
        </template>
      </el-table-column>
      <el-table-column label="变量值" min-width="180">
        <template #default="{ row }">
          <el-input v-model="row.value" placeholder="支持${var}引用" size="small" @input="emitUpdate" />
        </template>
      </el-table-column>
      <el-table-column label="作用域" width="120">
        <template #default="{ row }">
          <el-select v-model="row.scope" size="small" @change="emitUpdate">
            <el-option v-for="s in VARIABLE_SCOPES" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </template>
      </el-table-column>
      <el-table-column label="覆盖" width="60" align="center">
        <template #default="{ row }">
          <el-checkbox v-model="row.overwrite" size="small" @change="emitUpdate" />
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
      <el-icon><Plus /></el-icon>添加变量
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
import { VARIABLE_SCOPES } from '@/types/api'
import type { VariableItem } from '@/types/api'

const props = defineProps<{
  modelValue: Record<string, any>
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, any>]
}>()

const variables = ref<VariableItem[]>([...(props.modelValue?.variables || [])])

watch(() => props.modelValue, (val) => {
  variables.value = [...(val?.variables || [])]
}, { deep: true })

function addRow() {
  variables.value.push({ name: '', value: '', scope: 'temp', overwrite: true })
  emitUpdate()
}

function removeRow(index: number) {
  variables.value.splice(index, 1)
  emitUpdate()
}

function emitUpdate() {
  emit('update:modelValue', { ...props.modelValue, variables: variables.value })
}
</script>

<style scoped>
.set-variable-config {
  width: 100%;
}
</style>
