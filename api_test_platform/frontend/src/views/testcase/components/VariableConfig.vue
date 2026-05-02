<template>
  <div class="variable-config">
    <div class="var-toolbar">
      <el-input
        v-model="searchText"
        placeholder="搜索变量名"
        prefix-icon="Search"
        clearable
        size="small"
        style="width: 200px"
      />
      <el-select v-model="filterType" size="small" style="width: 140px" placeholder="筛选">
        <el-option label="全部" value="all" />
        <el-option label="有空值" value="empty" />
        <el-option label="有默认值" value="has_default" />
      </el-select>
      <div class="var-toolbar-right">
        <el-button size="small" @click="showBatchEdit = true" :disabled="selectedKeys.size === 0">
          批量编辑 ({{ selectedKeys.size }})
        </el-button>
        <el-button size="small" @click="showImportDialog = true">
          批量导入
        </el-button>
        <el-button type="primary" size="small" @click="addVariable">
          添加变量
        </el-button>
      </div>
    </div>

    <el-table :data="filteredVariables" border size="small" style="width: 100%" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="40" />
      <el-table-column label="变量名" min-width="140">
        <template #default="{ row, $index }">
          <el-input
            v-if="editingIndex === $index"
            v-model="editForm.key"
            size="small"
            placeholder="变量名"
            @blur="validateKey($index)"
          />
          <span v-else class="var-key">{{ row.key }}</span>
        </template>
      </el-table-column>
      <el-table-column label="变量值" min-width="140">
        <template #default="{ row, $index }">
          <el-input
            v-if="editingIndex === $index"
            v-model="editForm.value"
            size="small"
            placeholder="变量值"
          />
          <span v-else>{{ row.value }}</span>
        </template>
      </el-table-column>
      <el-table-column label="默认值" min-width="120">
        <template #default="{ row, $index }">
          <el-input
            v-if="editingIndex === $index"
            v-model="editForm.default_value"
            size="small"
            placeholder="默认值"
          />
          <span v-else>{{ row.default_value }}</span>
        </template>
      </el-table-column>
      <el-table-column label="备注" min-width="140">
        <template #default="{ row, $index }">
          <el-input
            v-if="editingIndex === $index"
            v-model="editForm.description"
            size="small"
            placeholder="备注"
          />
          <span v-else>{{ row.description }}</span>
        </template>
      </el-table-column>
      <el-table-column label="启用" width="70" align="center">
        <template #default="{ row, $index }">
          <el-switch
            v-if="editingIndex === $index"
            v-model="editForm.enabled"
            size="small"
          />
          <el-switch
            v-else
            v-model="row.enabled"
            size="small"
            @change="emitUpdate"
          />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" align="center" fixed="right">
        <template #default="{ $index }">
          <template v-if="editingIndex === $index">
            <el-button type="primary" link size="small" @click="saveEdit($index)">保存</el-button>
            <el-button link size="small" @click="cancelEdit">取消</el-button>
          </template>
          <template v-else>
            <el-button type="primary" link size="small" @click="startEdit($index)">编辑</el-button>
            <el-button type="danger" link size="small" @click="removeVariable($index)">删除</el-button>
          </template>
        </template>
      </el-table-column>
    </el-table>

    <VariableImportDialog
      v-model="showImportDialog"
      @import="handleImport"
    />

    <VariableBatchEditDialog
      v-model="showBatchEdit"
      :selected-count="selectedKeys.size"
      @batch-action="handleBatchAction"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { TestCaseVariable } from '@/types/testcase'
import VariableImportDialog from './VariableImportDialog.vue'
import VariableBatchEditDialog from './VariableBatchEditDialog.vue'

const KEY_REGEX = /^[a-zA-Z_][a-zA-Z0-9_]*$/

const props = withDefaults(defineProps<{
  modelValue: TestCaseVariable[]
}>(), {
  modelValue: () => []
})

const emit = defineEmits<{
  'update:modelValue': [value: TestCaseVariable[]]
}>()

const searchText = ref('')
const filterType = ref('all')
const editingIndex = ref(-1)
const editForm = ref<TestCaseVariable>({ key: '', value: '', default_value: '', description: '', enabled: true })
const showImportDialog = ref(false)
const showBatchEdit = ref(false)
const selectedKeys = ref<Set<string>>(new Set())

const variables = computed({
  get: () => props.modelValue || [],
  set: (val) => emit('update:modelValue', val)
})

const filteredVariables = computed(() => {
  let list = variables.value
  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    list = list.filter(v => v.key.toLowerCase().includes(keyword))
  }
  if (filterType.value === 'empty') {
    list = list.filter(v => !v.value)
  } else if (filterType.value === 'has_default') {
    list = list.filter(v => v.default_value)
  }
  return list
})

function emitUpdate() {
  emit('update:modelValue', [...variables.value])
}

function addVariable() {
  const newList = [...variables.value, { key: '', value: '', default_value: '', description: '', enabled: true }]
  emit('update:modelValue', newList)
  const realIndex = newList.length - 1
  startEdit(realIndex)
}

function removeVariable(index: number) {
  const varItem = filteredVariables.value[index]
  const realIndex = variables.value.findIndex(v => v === varItem)
  if (realIndex >= 0) {
    const newList = [...variables.value]
    newList.splice(realIndex, 1)
    emit('update:modelValue', newList)
  }
}

function startEdit(index: number) {
  const varItem = filteredVariables.value[index]
  editingIndex.value = index
  editForm.value = { ...varItem }
}

function cancelEdit() {
  editingIndex.value = -1
  editForm.value = { key: '', value: '', default_value: '', description: '', enabled: true }
}

function validateKey(index: number): boolean {
  if (!editForm.value.key) {
    return false
  }
  if (!KEY_REGEX.test(editForm.value.key)) {
    ElMessage.warning('变量名只能包含字母、数字和下划线，且不能以数字开头')
    return false
  }
  const varItem = filteredVariables.value[index]
  const duplicate = variables.value.find(v => v.key === editForm.value.key && v !== varItem)
  if (duplicate) {
    ElMessage.warning(`变量名 "${editForm.value.key}" 已存在`)
    return false
  }
  return true
}

function saveEdit(index: number) {
  if (!validateKey(index)) return
  const varItem = filteredVariables.value[index]
  const realIndex = variables.value.findIndex(v => v === varItem)
  if (realIndex >= 0) {
    const newList = [...variables.value]
    newList[realIndex] = { ...editForm.value }
    emit('update:modelValue', newList)
  }
  editingIndex.value = -1
}

function handleSelectionChange(rows: TestCaseVariable[]) {
  selectedKeys.value = new Set(rows.map(r => r.key))
}

function handleImport(importedVars: TestCaseVariable[]) {
  const newList = [...variables.value]
  for (const iv of importedVars) {
    const existIdx = newList.findIndex(v => v.key === iv.key)
    if (existIdx >= 0) {
      newList[existIdx] = { ...iv }
    } else {
      newList.push({ ...iv })
    }
  }
  emit('update:modelValue', newList)
}

function handleBatchAction(action: string, data?: any) {
  const newList = [...variables.value]
  if (action === 'set_default') {
    for (const key of selectedKeys.value) {
      const item = newList.find(v => v.key === key)
      if (item) item.default_value = data
    }
  } else if (action === 'enable_all') {
    for (const key of selectedKeys.value) {
      const item = newList.find(v => v.key === key)
      if (item) item.enabled = true
    }
  } else if (action === 'disable_all') {
    for (const key of selectedKeys.value) {
      const item = newList.find(v => v.key === key)
      if (item) item.enabled = false
    }
  } else if (action === 'delete_selected') {
    const result = newList.filter(v => !selectedKeys.value.has(v.key))
    emit('update:modelValue', result)
    showBatchEdit.value = false
    selectedKeys.value = new Set()
    return
  }
  emit('update:modelValue', newList)
  showBatchEdit.value = false
}
</script>

<style scoped>
.variable-config {
  width: 100%;
}

.var-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.var-toolbar-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 8px;
}

.var-key {
  font-family: ui-monospace, Consolas, monospace;
  font-size: 13px;
  font-weight: 500;
  color: #aa3bff;
}

:deep(.el-table .el-table__cell) {
  padding: 4px 0;
}
</style>
