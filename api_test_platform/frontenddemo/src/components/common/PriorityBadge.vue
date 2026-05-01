<template>
  <span class="priority-badge" :class="priority.toLowerCase()">
    {{ priority }}
  </span>
</template>

<script setup lang="ts">
defineProps<{
  priority: string
}>()
</script>

<style scoped>
.priority-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  padding: 2px 6px;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: var(--radius-sm);
}

.priority-badge.p0 {
  background-color: var(--color-error-bg);
  color: var(--color-p0);
}

.priority-badge.p1 {
  background-color: var(--color-warning-bg);
  color: var(--color-p1);
}

.priority-badge.p2 {
  background-color: var(--color-info-bg);
  color: var(--color-p2);
}

.priority-badge.p3 {
  background-color: var(--color-bg-hover);
  color: var(--color-p3);
}
</style>