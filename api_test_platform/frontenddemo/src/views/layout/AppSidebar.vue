<template>
  <aside class="app-sidebar" :class="{ collapsed }">
    <div class="sidebar-toggle" @click="toggleSidebar">
      <el-icon :size="18">
        <ArrowLeft v-if="!collapsed" />
        <ArrowRight v-else />
      </el-icon>
    </div>

    <nav class="sidebar-nav">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :class="{ active: isActive(item.path) }"
      >
        <el-icon :size="20">
          <component :is="item.icon" />
        </el-icon>
        <span v-if="!collapsed" class="nav-text">{{ item.label }}</span>
        <el-tooltip v-if="collapsed" :content="item.label" placement="right">
          <span class="nav-tooltip-placeholder"></span>
        </el-tooltip>
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <router-link to="/settings" class="nav-item">
        <el-icon :size="20"><Setting /></el-icon>
        <span v-if="!collapsed" class="nav-text">设置</span>
      </router-link>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import {
  ArrowLeft,
  ArrowRight,
  Connection,
  Document,
  SetUp,
  Setting,
} from '@element-plus/icons-vue'

defineProps<{
  collapsed: boolean
}>()

const emit = defineEmits<{
  'update:collapsed': [value: boolean]
}>()

const route = useRoute()

const navItems = [
  { path: '/environments', label: '环境管理', icon: Connection },
  { path: '/apis', label: '接口管理', icon: Document },
  { path: '/testcases', label: '测试用例', icon: SetUp },
]

const isActive = (path: string) => {
  return route.path.startsWith(path)
}

const toggleSidebar = () => {
  emit('update:collapsed', !collapsed)
}
</script>

<style scoped>
.app-sidebar {
  position: fixed;
  top: var(--header-height);
  left: 0;
  bottom: 0;
  width: var(--sidebar-width-expanded);
  background: var(--color-bg-sidebar);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-normal);
  z-index: var(--z-sidebar);
}

.app-sidebar.collapsed {
  width: var(--sidebar-width-collapsed);
}

.sidebar-toggle {
  position: absolute;
  top: var(--spacing-md);
  right: calc(-1 * var(--spacing-md));
  width: 24px;
  height: 24px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 1;
  transition: all var(--transition-fast);
}

.sidebar-toggle:hover {
  background: var(--color-bg-hover);
}

.sidebar-nav {
  flex: 1;
  padding: var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-lg);
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: all var(--transition-fast);
  white-space: nowrap;
  overflow: hidden;
}

.nav-item:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-primary);
}

.nav-item.active {
  background: var(--color-primary-bg);
  color: var(--color-primary);
}

.nav-text {
  font-size: 0.9375rem;
  font-weight: 500;
}

.nav-tooltip-placeholder {
  display: none;
}

.app-sidebar.collapsed .nav-item {
  justify-content: center;
  padding: var(--spacing-sm);
}

.app-sidebar.collapsed .sidebar-toggle {
  right: calc(-1 * var(--spacing-md) + 20px);
}

.sidebar-footer {
  padding: var(--spacing-md);
  border-top: 1px solid var(--color-border);
}
</style>