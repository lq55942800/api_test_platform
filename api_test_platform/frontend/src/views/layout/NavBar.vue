<template>
  <div class="navbar">
    <div class="navbar-left">
      <el-icon class="collapse-btn" @click="$emit('toggle-sidebar')">
        <Fold v-if="!isCollapsed" />
        <Expand v-else />
      </el-icon>
      <el-breadcrumb separator="/" class="navbar-breadcrumb">
        <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path">
          <router-link v-if="item.path" :to="item.path">{{ item.title }}</router-link>
          <span v-else>{{ item.title }}</span>
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>
    <div class="navbar-right">
      <el-dropdown trigger="click" @command="handleCommand">
        <div class="user-info">
          <el-avatar :size="32" class="user-avatar">
            {{ avatarText }}
          </el-avatar>
          <span class="user-name">{{ displayName }}</span>
          <el-icon class="el-icon--right"><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon>个人信息
            </el-dropdown-item>
            <el-dropdown-item command="password">
              <el-icon><Lock /></el-icon>修改密码
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon><SwitchButton /></el-icon>退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Fold, Expand, ArrowDown, User, Lock, SwitchButton } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

defineProps<{
  isCollapsed: boolean
}>()

defineEmits<{
  toggleSidebar: []
}>()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const displayName = computed(() => {
  return authStore.user?.full_name || authStore.user?.username || '用户'
})

const avatarText = computed(() => {
  const name = authStore.user?.full_name || authStore.user?.username || 'U'
  return name.charAt(0).toUpperCase()
})

const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta?.title)
  const crumbs: Array<{ title: string; path: string | null }> = [
    { title: '首页', path: '/' }
  ]
  matched.forEach((item, index) => {
    const isLast = index === matched.length - 1
    crumbs.push({
      title: item.meta.title as string,
      path: isLast ? null : item.path
    })
  })
  return crumbs
})

async function handleCommand(command: string) {
  switch (command) {
    case 'profile':
      break
    case 'password':
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        })
        await authStore.logout()
      } catch {
        // User cancelled
      }
      break
  }
}
</script>

<style scoped>
.navbar {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: #606266;
  transition: color 0.2s;
}

.collapse-btn:hover {
  color: #aa3bff;
}

.navbar-breadcrumb {
  line-height: 56px;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background 0.2s;
}

.user-info:hover {
  background: #f5f7fa;
}

.user-avatar {
  background: #aa3bff;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
}

.user-name {
  font-size: 14px;
  color: #303133;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
