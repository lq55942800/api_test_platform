<template>
  <span class="status-badge" :class="status">
    <span class="status-dot"></span>
    {{ label }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  status: string
}>()

const label = computed(() => {
  const map: Record<string, string> = {
    enabled: '已启用',
    disabled: '已禁用',
    draft: '草稿',
    active: '激活',
  }
  return map[props.status] || props.status
})
</script>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--color-text-muted);
}

.status-badge.enabled .status-dot,
.status-badge.active .status-dot {
  background-color: var(--color-success);
}

.status-badge.disabled .status-dot {
  background-color: var(--color-text-muted);
}

.status-badge.draft .status-dot {
  background-color: var(--color-warning);
}
</style>