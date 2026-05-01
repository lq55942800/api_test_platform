<template>
  <header class="app-header">
    <div class="header-left">
      <div class="logo">
        <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="28" height="28" rx="6" fill="#4A90A4"/>
          <path d="M8 14L12 18L20 10" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span class="logo-text">API Platform</span>
      </div>
    </div>
    <div class="header-center">
      <el-input
        v-model="searchQuery"
        placeholder="搜索环境、接口、测试用例..."
        class="global-search"
        :prefix-icon="Search"
      />
    </div>
    <div class="header-right">
      <el-dropdown trigger="click">
        <div class="user-menu">
          <el-avatar :size="32" icon="User" />
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item>个人设置</el-dropdown-item>
            <el-dropdown-item divided>退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Search } from '@element-plus/icons-vue'

const searchQuery = ref('')
</script>

<style scoped>
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: var(--header-height);
  background: var(--color-bg-card);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--spacing-lg);
  z-index: var(--z-header);
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.logo-text {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.header-center {
  flex: 1;
  max-width: 480px;
  margin: 0 var(--spacing-xl);
}

.global-search {
  width: 100%;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-menu {
  cursor: pointer;
  padding: var(--spacing-xs);
  border-radius: var(--radius-lg);
  transition: background-color var(--transition-fast);
}

.user-menu:hover {
  background-color: var(--color-bg-hover);
}
</style>