<script setup lang="ts">
interface Props {
  loading?: boolean
  data: any[]
  total?: number
  currentPage?: number
  pageSize?: number
  pageSizes?: number[]
  stripe?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  data: () => [],
  total: 0,
  currentPage: 1,
  pageSize: 20,
  pageSizes: () => [10, 20, 50, 100],
  stripe: false
})

const emit = defineEmits<{
  (e: 'update:current-page', page: number): void
  (e: 'update:page-size', size: number): void
  (e: 'selection-change', selection: any[]): void
}>()

function handlePageChange(page: number) {
  emit('update:current-page', page)
}

function handleSizeChange(size: number) {
  emit('update:page-size', size)
}
</script>

<template>
  <div class="table-wrapper">
    <el-table
      ref="tableRef"
      :data="data"
      v-loading="loading"
      :stripe="stripe"
      style="width: 100%"
      @selection-change="emit('selection-change', $event)"
      class="data-table"
    >
      <slot />
    </el-table>

    <div class="pagination-wrapper">
      <el-pagination
        :current-page="props.currentPage"
        :page-size="props.pageSize"
        :page-sizes="pageSizes"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        background
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<style scoped>
.table-wrapper {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  background-color: #fff;
  border-radius: 0.5rem;
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

.data-table {
  flex: 1;
}

.data-table :deep(.el-table__header th) {
  font-weight: 600;
  color: var(--color-neutral-700);
  background-color: var(--color-surface-100) !important;
}

.data-table :deep(.el-table__cell) {
  padding-top: 0.75rem;
  padding-bottom: 0.75rem;
}

.data-table :deep(.el-table__cell .cell) {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.data-table :deep(.el-button + .el-button) {
  margin-left: 0;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--color-neutral-200);
  background-color: var(--color-surface-100);
}
</style>