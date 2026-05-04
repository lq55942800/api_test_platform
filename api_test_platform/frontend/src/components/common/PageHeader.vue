<script setup lang="ts">
interface Props {
  title: string
  subtitle?: string
}

defineProps<Props>()
</script>

<template>
  <div class="page-header">
    <div class="page-header-content">
      <h1 class="page-title">{{ title }}</h1>
      <p v-if="subtitle" class="page-subtitle">{{ subtitle }}</p>
    </div>
  </div>
</template>

<style scoped>
.page-header {
  margin-bottom: 1rem;
  flex-shrink: 0;
}

.page-header-content {
  padding: 1.25rem 1.25rem;
  background-color: #fff;
  border-radius: 0.5rem;
  box-shadow: var(--shadow-card);
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-neutral-900);
  margin: 0 0 0.25rem 0;
  line-height: 1.5;
}

.page-subtitle {
  font-size: 0.875rem;
  color: var(--color-neutral-500);
  margin: 0;
  line-height: 1.5;
}
</style>