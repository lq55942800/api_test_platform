<script setup lang="ts">
interface Props {
  showBatchBar?: boolean
  batchCount?: number
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'batch-delete'): void
  (e: 'batch-action', action: string): void
  (e: 'clear-selection'): void
}>()
</script>

<template>
  <div class="toolbar-container">
    <div class="toolbar-left">
      <slot name="left" />
    </div>
    <div class="toolbar-right">
      <slot name="right" />
    </div>
  </div>

  <Transition name="fade">
    <div v-if="showBatchBar && batchCount && batchCount > 0" class="batch-bar">
      <span class="batch-bar-info">已选择 {{ batchCount }} 项</span>
      <el-button size="small" type="danger" plain @click="emit('batch-delete')">
        批量删除
      </el-button>
      <slot name="batch-actions" />
      <el-button size="small" plain @click="emit('clear-selection')">
        取消选择
      </el-button>
    </div>
  </Transition>
</template>

<style scoped>
.toolbar-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  padding: 0.75rem 1rem;
  background-color: #fff;
  border-radius: 0.5rem;
  box-shadow: var(--shadow-card);
  flex-wrap: wrap;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.batch-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
  color: #fff;
  border-radius: 0.375rem;
  background: linear-gradient(135deg, var(--color-primary-500) 0%, var(--color-primary-700) 100%);
  box-shadow: var(--shadow-card-md);
  flex-wrap: wrap;
}

.batch-bar-info {
  padding-right: 0.75rem;
  margin-right: 0.25rem;
  border-right: 1px solid rgba(255, 255, 255, 0.25);
  font-weight: 500;
}

.batch-bar :deep(.el-button) {
  height: 1.75rem;
  padding: 0 0.75rem;
  font-size: 0.8125rem;
  border-color: transparent;
  background-color: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.batch-bar :deep(.el-button:hover) {
  background-color: rgba(255, 255, 255, 0.35);
  border-color: transparent;
}

.batch-bar :deep(.el-button--danger) {
  background-color: #ef4444;
}

.batch-bar :deep(.el-button--danger:hover) {
  background-color: #dc2626;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>