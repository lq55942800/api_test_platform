<template>
  <div class="app-layout">
    <el-container>
      <el-aside :width="isCollapsed ? '64px' : '220px'" class="layout-aside">
        <SideMenu :is-collapsed="isCollapsed" />
      </el-aside>
      <el-container class="layout-main-container">
        <el-header class="layout-header" height="56px">
          <NavBar :is-collapsed="isCollapsed" @toggle-sidebar="toggleSidebar" />
        </el-header>
        <el-main class="layout-main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import SideMenu from './SideMenu.vue'
import NavBar from './NavBar.vue'

const isCollapsed = ref(false)

function toggleSidebar() {
  isCollapsed.value = !isCollapsed.value
}
</script>

<style scoped>
.app-layout {
  height: 100vh;
  overflow: hidden;
  display: flex;
}

.layout-aside {
  background: #1e1e2d;
  transition: width 0.3s ease;
  overflow: hidden;
}

.layout-main-container {
  flex-direction: column;
  overflow: hidden;
}

.layout-header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
  display: flex;
  align-items: center;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  z-index: 10;
}

.layout-main {
  background: #f5f7fa;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
}
</style>
