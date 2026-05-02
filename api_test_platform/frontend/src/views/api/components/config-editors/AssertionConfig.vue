<template>
  <div class="assertion-config">
    <el-table :data="assertions" size="small" border style="width: 100%">
      <el-table-column label="断言类型" width="110">
        <template #default="{ row }">
          <el-select v-model="row.type" size="small" @change="emitUpdate">
            <el-option v-for="t in ASSERTION_TYPES" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </template>
      </el-table-column>
      <el-table-column label="路径/字段" min-width="140">
        <template #default="{ row }">
          <el-input
            v-model="row.path"
            :placeholder="getPathPlaceholder(row.type)"
            :disabled="!needsPath(row.type)"
            size="small"
            @input="emitUpdate"
          />
        </template>
      </el-table-column>
      <el-table-column label="比较方式" width="110">
        <template #default="{ row }">
          <el-select v-model="row.operator" size="small" @change="emitUpdate">
            <el-option v-for="op in ASSERTION_OPERATORS" :key="op.value" :label="op.label" :value="op.value" />
          </el-select>
        </template>
      </el-table-column>
      <el-table-column label="期望值" min-width="140">
        <template #default="{ row }">
          <el-input
            v-model="row.expected"
            :disabled="isUnaryOp(row.operator)"
            :placeholder="isUnaryOp(row.operator) ? '-' : '期望值'"
            size="small"
            @input="emitUpdate"
          />
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
      <el-icon><Plus /></el-icon>添加断言
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
import { ASSERTION_TYPES, ASSERTION_OPERATORS } from '@/types/api'
import type { AssertionItem, AssertionType, AssertionOperator } from '@/types/api'

const props = defineProps<{
  modelValue: Record<string, any>
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, any>]
}>()

const assertions = ref<AssertionItem[]>([...(props.modelValue?.assertions || [])])

watch(() => props.modelValue, (val) => {
  assertions.value = [...(val?.assertions || [])]
}, { deep: true })

function needsPath(type: AssertionType): boolean {
  return ['jsonpath', 'header'].includes(type)
}

function getPathPlaceholder(type: AssertionType): string {
  const map: Record<string, string> = {
    status_code: '',
    jsonpath: '$.data.id',
    header: 'Content-Type',
    response_time: '',
    body_contains: '',
    regex: '',
    json_schema: '',
    script: ''
  }
  return map[type] || ''
}

function isUnaryOp(operator: AssertionOperator): boolean {
  return ['is_empty', 'not_empty'].includes(operator)
}

function addRow() {
  assertions.value.push({
    type: 'status_code',
    operator: 'eq',
    expected: 200,
    message: ''
  })
  emitUpdate()
}

function removeRow(index: number) {
  assertions.value.splice(index, 1)
  emitUpdate()
}

function emitUpdate() {
  emit('update:modelValue', { ...props.modelValue, assertions: assertions.value })
}
</script>

<style scoped>
.assertion-config {
  width: 100%;
}
</style>
