<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="批量编辑"
    width="480px"
    :close-on-click-modal="false"
  >
    <div class="batch-section">
      <div class="batch-section-title">批量设置默认值</div>
      <div class="batch-row">
        <el-input v-model="batchDefaultValue" placeholder="输入默认值" style="flex: 1" />
        <el-button type="primary" @click="handleBatchAction('set_default', batchDefaultValue)" :disabled="!batchDefaultValue">应用</el-button>
      </div>
    </div>

    <el-divider />

    <div class="batch-section">
      <div class="batch-section-title">批量启用/禁用</div>
      <div class="batch-row">
        <el-button type="success" @click="handleBatchAction('enable_all')">全部启用</el-button>
        <el-button type="warning" @click="handleBatchAction('disable_all')">全部禁用</el-button>
      </div>
    </div>

    <el-divider />

    <div class="batch-section">
      <div class="batch-section-title">批量删除</div>
      <div class="batch-row">
        <el-button type="danger" @click="handleBatchDelete">删除选中 ({{ selectedCount }})</el-button>
      </div>
    </div>

    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessageBox } from 'element-plus'

const props = defineProps<{
  modelValue: boolean
  selectedCount: number
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'batch-action': [action: string, data?: any]
}>()

const batchDefaultValue = ref('')

watch(() => props.modelValue, (val) => {
  if (val) {
    batchDefaultValue.value = ''
  }
})

function handleBatchAction(action: string, data?: any) {
  emit('batch-action', action, data)
}

async function handleBatchDelete() {
  try {
    await ElMessageBox.confirm(
      `确定删除选中的 ${props.selectedCount} 个变量吗？此操作不可恢复。`,
      '警告',
      { type: 'warning' }
    )
    emit('batch-action', 'delete_selected')
  } catch {}
}
</script>

<style scoped>
.batch-section {
  margin-bottom: 4px;
}

.batch-section-title {
  font-size: 14px;
  font-weight: 600;
  color: #08060d;
  margin-bottom: 12px;
}

.batch-row {
  display: flex;
  gap: 8px;
  align-items: center;
}
</style>
