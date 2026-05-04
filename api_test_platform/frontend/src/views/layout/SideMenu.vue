<template>
  <div class="side-menu">
    <div class="menu-logo" @click="router.push('/')">
      <div class="logo-icon">A</div>
      <span v-show="!isCollapsed" class="logo-text">AutoTest</span>
    </div>
    <el-menu
      :default-active="activeMenu"
      :collapse="isCollapsed"
      :collapse-transition="false"
      background-color="#1e1e2d"
      text-color="#a2a3b7"
      active-text-color="#aa3bff"
      router
      class="side-menu-list"
    >
      <el-menu-item index="/environments">
        <el-icon><Monitor /></el-icon>
        <template #title>环境管理</template>
      </el-menu-item>

      <el-menu-item index="/apis">
        <el-icon><Connection /></el-icon>
        <template #title>接口管理</template>
      </el-menu-item>

      <el-menu-item index="/testcase">
        <el-icon><DocumentChecked /></el-icon>
        <template #title>测试用例</template>
      </el-menu-item>

      <el-sub-menu index="test-management">
        <template #title>
          <el-icon><DataAnalysis /></el-icon>
          <span>测试管理</span>
        </template>
        <el-menu-item index="/scenarios">
          <el-icon><Film /></el-icon>
          <template #title>测试场景</template>
        </el-menu-item>
        <el-menu-item index="/plans">
          <el-icon><Calendar /></el-icon>
          <template #title>测试计划</template>
        </el-menu-item>
        <el-menu-item index="/reports">
          <el-icon><TrendCharts /></el-icon>
          <template #title>测试报告</template>
        </el-menu-item>
      </el-sub-menu>

      <el-sub-menu v-if="authStore.user?.is_superuser" index="system">
        <template #title>
          <el-icon><Setting /></el-icon>
          <span>系统管理</span>
        </template>
        <el-menu-item index="/admin/teams">
          <el-icon><OfficeBuilding /></el-icon>
          <template #title>团队管理</template>
        </el-menu-item>
        <el-menu-item index="/admin/users">
          <el-icon><UserFilled /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>
      </el-sub-menu>
    </el-menu>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Monitor,
  Connection,
  DocumentChecked,
  DataAnalysis,
  Film,
  Calendar,
  TrendCharts,
  Setting,
  OfficeBuilding,
  UserFilled,
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

defineProps<{
  isCollapsed: boolean
}>()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/environments')) return '/environments'
  if (path.startsWith('/apis')) return '/apis'
  if (path.startsWith('/testcase') || path.startsWith('/execution')) return '/testcase'
  if (path.startsWith('/scenarios')) return '/scenarios'
  if (path.startsWith('/plans')) return '/plans'
  if (path.startsWith('/reports')) return '/reports'
  if (path.startsWith('/admin/teams')) return '/admin/teams'
  if (path.startsWith('/admin/users')) return '/admin/users'
  return path
})
</script>

<style scoped>
.side-menu {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #1e1e2d;
}

.menu-logo {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  cursor: pointer;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  padding: 0 16px;
  flex-shrink: 0;
}

.logo-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #aa3bff, #6c5ce7);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  flex-shrink: 0;
}

.logo-text {
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
}

.side-menu-list {
  flex: 1;
  overflow-y: auto;
  border-right: none;
}

.side-menu-list:not(.el-menu--collapse) {
  width: 220px;
}

.side-menu-list::-webkit-scrollbar {
  width: 4px;
}

.side-menu-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

:deep(.el-menu-item.is-active) {
  background-color: rgba(170, 59, 255, 0.1) !important;
  border-right: 3px solid #aa3bff;
}

:deep(.el-sub-menu .el-menu-item) {
  padding-left: 52px !important;
}

:deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.05) !important;
}
</style>
