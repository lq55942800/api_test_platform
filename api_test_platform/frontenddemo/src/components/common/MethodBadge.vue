<template>
  <span class="method-badge" :class="method.toLowerCase()">
    {{ method }}
  </span>
</template>

<script setup lang="ts">
defineProps<{
  method: string
}>()
</script>

<style scoped>
.method-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 48px;
  padding: 2px 8px;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: var(--radius-sm);
  text-transform: uppercase;
}

.method-badge.get {
  background-color: var(--color-success-bg);
  color: var(--color-get);
}

.method-badge.post {
  background-color: var(--color-info-bg);
  color: var(--color-post);
}

.method-badge.put {
  background-color: var(--color-warning-bg);
  color: var(--color-put);
}

.method-badge.delete {
  background-color: var(--color-error-bg);
  color: var(--color-delete);
}

.method-badge.patch {
  background-color: rgba(155, 89, 182, 0.1);
  color: var(--color-patch);
}

.method-badge.head,
.method-badge.options {
  background-color: var(--color-bg-hover);
  color: var(--color-text-secondary);
}
</style>