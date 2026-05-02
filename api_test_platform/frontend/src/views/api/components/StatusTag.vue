<template>
  <el-tag
    :type="statusConfig.type"
    size="small"
    effect="light"
  >
    {{ statusConfig.label }}
  </el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { API_STATUSES, ApiStatus } from '@/types/api'

const props = defineProps<{
  status: string
}>()

const statusConfig = computed(() => {
  const found = API_STATUSES.find(s => s.value === props.status)
  if (found) return found
  const typeMap: Record<string, string> = {
    draft: 'warning',
    enabled: 'success',
    disabled: 'info',
    deprecated: 'danger'
  }
  const labelMap: Record<string, string> = {
    draft: '草稿',
    enabled: '启用',
    disabled: '禁用',
    deprecated: '废弃'
  }
  return {
    value: props.status,
    label: labelMap[props.status] || props.status,
    type: typeMap[props.status] || 'info'
  }
})
</script>
