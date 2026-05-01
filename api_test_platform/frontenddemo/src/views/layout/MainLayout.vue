<template>
  <div class="main-layout">
    <AppHeader />
    <div class="layout-body">
      <AppSidebar v-model:collapsed="sidebarCollapsed" />
      <main class="main-content" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'

const sidebarCollapsed = ref(false)
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.layout-body {
  display: flex;
  flex: 1;
  padding-top: var(--header-height);
}

.main-content {
  flex: 1;
  margin-left: var(--sidebar-width-expanded);
  padding: var(--spacing-lg);
  transition: margin-left var(--transition-normal);
  background-color: var(--color-bg-page);
  min-height: calc(100vh - var(--header-height));
}

.main-content.sidebar-collapsed {
  margin-left: var(--sidebar-width-collapsed);
}
</style>