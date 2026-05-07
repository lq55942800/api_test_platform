# Frontend Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the entire frontend with a modern, lightweight professional aesthetic - Indigo primary color, clean whites, generous whitespace, three-column API layout.

**Architecture:** Complete UI redesign keeping Vue 3 + Element Plus + Tailwind CSS stack. Global CSS variables for theming, new layout components, all pages restyled to match spec.

**Tech Stack:** Vue 3, TypeScript, Element Plus, Tailwind CSS, Pinia, Vue Router

---

## File Structure

### Global Styles
- Modify: `frontend/src/style.css` - CSS variables, typography, component styles

### Layout Components
- Modify: `frontend/src/views/layout/AppLayout.vue`
- Modify: `frontend/src/views/layout/SideMenu.vue`
- Modify: `frontend/src/views/layout/NavBar.vue`

### Auth Pages
- Modify: `frontend/src/views/auth/Login.vue`
- Modify: `frontend/src/views/auth/Register.vue`

### API Pages
- Modify: `frontend/src/views/api/ApiList.vue` - Three-column layout
- Modify: `frontend/src/views/api/ApiDetail.vue`
- Modify: `frontend/src/views/api/components/MethodTag.vue`
- Modify: `frontend/src/views/api/components/StatusTag.vue`
- Modify: `frontend/src/views/api/components/ModuleTree.vue`

### Environment Pages
- Modify: `frontend/src/views/environment/EnvironmentList.vue`
- Modify: `frontend/src/views/environment/EnvironmentDetail.vue`
- Modify: `frontend/src/views/environment/EnvironmentEdit.vue`

### TestCase Pages
- Modify: `frontend/src/views/testcase/TestCaseList.vue`
- Modify: `frontend/src/views/testcase/TestCaseDetail.vue`

### Admin Pages
- Modify: `frontend/src/views/admin/TeamManagement.vue`
- Modify: `frontend/src/views/admin/UserManagement.vue`

---

## Implementation Tasks

### Task 1: Global CSS Variables & Base Styles

**Files:**
- Modify: `frontend/src/style.css`

- [ ] **Step 1: Rewrite style.css with new design system**

Replace the entire file content with:

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  /* Primary - Indigo */
  --color-primary-50: #eef2ff;
  --color-primary-100: #e0e7ff;
  --color-primary-200: #c7d2fe;
  --color-primary-300: #a5b4fc;
  --color-primary-400: #818cf8;
  --color-primary-500: #6366f1;
  --color-primary-600: #4f46e5;
  --color-primary-700: #4338ca;

  /* Neutral - Slate */
  --color-neutral-50: #f8fafc;
  --color-neutral-100: #f1f5f9;
  --color-neutral-200: #e2e8f0;
  --color-neutral-300: #cbd5e1;
  --color-neutral-400: #94a3b8;
  --color-neutral-500: #64748b;
  --color-neutral-600: #475569;
  --color-neutral-700: #334155;
  --color-neutral-800: #1e293b;
  --color-neutral-900: #0f172a;

  /* Semantic */
  --color-success: #10b981;
  --color-success-light: #d1fae5;
  --color-success-dark: #059669;
  --color-warning: #f59e0b;
  --color-warning-light: #fef3c7;
  --color-warning-dark: #d97706;
  --color-danger: #ef4444;
  --color-danger-light: #fee2e2;
  --color-danger-dark: #dc2626;
  --color-info: #3b82f6;
  --color-info-light: #dbeafe;

  /* Surface */
  --color-surface-bg: #f8fafc;
  --color-surface: #ffffff;

  /* Sidebar */
  --color-sidebar-bg: #1e1e2d;
  --color-sidebar-text: #e2e8f0;
  --color-sidebar-muted: #94a3b8;

  /* HTTP Methods */
  --color-method-get: #059669;
  --color-method-get-bg: #d1fae5;
  --color-method-post: #2563eb;
  --color-method-post-bg: #dbeafe;
  --color-method-put: #d97706;
  --color-method-put-bg: #fef3c7;
  --color-method-delete: #dc2626;
  --color-method-delete-bg: #fee2e2;
  --color-method-patch: #7c3aed;
  --color-method-patch-bg: #ede9fe;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;

  /* Border Radius */
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.04), 0 1px 2px -1px rgb(0 0 0 / 0.04);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.06), 0 2px 4px -2px rgb(0 0 0 / 0.04);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.08), 0 4px 6px -4px rgb(0 0 0 / 0.04);

  /* Transitions */
  --transition-fast: 150ms ease;
  --transition: 200ms ease;
}

@layer base {
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    -webkit-font-smoothing: antialiased;
    color: var(--color-neutral-900);
    background-color: var(--color-surface-bg);
  }
}

@layer components {
  /* Page */
  .page-container { @apply flex flex-col h-full overflow-hidden; }
  .page-header {
    @apply flex items-center justify-between mb-6 px-6 py-5 bg-white rounded-xl;
    box-shadow: var(--shadow);
  }
  .page-title { @apply text-2xl font-bold text-neutral-900; }
  .page-subtitle { @apply text-sm text-neutral-500 mt-1; }

  /* Toolbar */
  .toolbar {
    @apply flex items-center gap-4 p-4 mb-4 bg-white rounded-xl;
    box-shadow: var(--shadow);
  }
  .toolbar-left, .toolbar-right { @apply flex items-center gap-3; }

  /* Buttons */
  .btn {
    @apply inline-flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-medium rounded-lg;
    transition: all var(--transition-fast);
  }
  .btn-primary {
    @apply btn text-white;
    background-color: var(--color-primary-500);
    border: 1px solid var(--color-primary-500);
  }
  .btn-primary:hover {
    background-color: var(--color-primary-600);
    border-color: var(--color-primary-600);
  }
  .btn-secondary {
    @apply btn;
    background-color: white;
    border: 1px solid var(--color-neutral-200);
    color: var(--color-neutral-700);
  }
  .btn-secondary:hover {
    border-color: var(--color-primary-500);
    color: var(--color-primary-500);
  }
  .btn-danger {
    @apply btn text-white;
    background-color: var(--color-danger);
    border: 1px solid var(--color-danger);
  }
  .btn-danger:hover { background-color: var(--color-danger-dark); }
  .btn-ghost {
    @apply btn;
    background: transparent;
    border: none;
    color: var(--color-neutral-600);
  }
  .btn-ghost:hover { background: var(--color-neutral-100); color: var(--color-neutral-900); }

  /* Inputs */
  .search-input { @apply w-72; }
  .filter-select { @apply w-36; }
  .form-input {
    @apply w-full h-9 px-3 text-sm border border-neutral-200 rounded-md;
    transition: all var(--transition-fast);
  }
  .form-input:focus {
    @apply border-primary-500 outline-none;
    box-shadow: 0 0 0 3px var(--color-primary-100);
  }

  /* Table */
  .table-container {
    @apply flex flex-col flex-1 min-h-0 bg-white rounded-xl overflow-hidden;
    box-shadow: var(--shadow);
  }
  .data-table th {
    @apply font-semibold text-xs uppercase tracking-wider text-neutral-500;
    background: var(--color-neutral-50) !important;
    padding: 14px 16px !important;
  }
  .data-table td { @apply py-4 px-4; }
  .data-table tr:hover > td { background: var(--color-neutral-50) !important; }

  /* Status Badges */
  .badge {
    @apply inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-full;
  }
  .badge-success { @apply badge; background: var(--color-success-light); color: var(--color-success-dark); }
  .badge-warning { @apply badge; background: var(--color-warning-light); color: var(--color-warning-dark); }
  .badge-danger { @apply badge; background: var(--color-danger-light); color: var(--color-danger-dark); }
  .badge-info { @apply badge; background: var(--color-info-light); color: #1e40af; }

  /* Method Badges */
  .method-badge {
    @apply inline-flex items-center justify-center px-2.5 py-1 text-xs font-semibold rounded;
    min-width: 56px;
  }
  .method-get { background: var(--color-method-get-bg); color: var(--color-method-get); }
  .method-post { background: var(--color-method-post-bg); color: var(--color-method-post); }
  .method-put { background: var(--color-method-put-bg); color: var(--color-method-put); }
  .method-delete { background: var(--color-method-delete-bg); color: var(--color-method-delete); }
  .method-patch { background: var(--color-method-patch-bg); color: var(--color-method-patch); }

  /* Card */
  .card {
    @apply bg-white rounded-xl p-5;
    box-shadow: var(--shadow);
    transition: box-shadow var(--transition-fast);
  }
  .card:hover { box-shadow: var(--shadow-md); }

  /* Empty State */
  .empty-state { @apply flex flex-col items-center justify-center py-16 text-center; }
  .empty-icon { @apply w-12 h-12 mb-4 text-neutral-300; }
  .empty-title { @apply text-base font-medium text-neutral-700 mb-1; }
  .empty-desc { @apply text-sm text-neutral-500 mb-4; }

  /* Pagination */
  .pagination { @apply flex justify-end px-6 py-4 border-t border-neutral-100; }
}

@layer utilities {
  .text-primary { color: var(--color-primary-500); }
  .text-success { color: var(--color-success); }
  .text-danger { color: var(--color-danger); }
  .text-warning { color: var(--color-warning); }
  .font-mono { font-family: 'JetBrains Mono', monospace; }
}

/* Element Plus Overrides */
.el-button--primary {
  --el-button-bg-color: var(--color-primary-500);
  --el-button-border-color: var(--color-primary-500);
  --el-button-hover-bg-color: var(--color-primary-600);
  --el-button-hover-border-color: var(--color-primary-600);
}
.el-link--primary { --el-link-text-color: var(--color-primary-500); }
.el-input__wrapper:focus-within { box-shadow: 0 0 0 1px var(--color-primary-500) inset !important; }
.el-table th { background: var(--color-neutral-50) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--color-neutral-300); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--color-neutral-400); }
```

- [ ] **Step 2: Run build to verify styles compile**

Run: `cd frontend && npx vite build 2>&1 | tail -20`
Expected: Build succeeds with no errors

- [ ] **Step 3: Commit**

```bash
git add frontend/src/style.css
git commit -m "feat: add new design system CSS variables and base styles"
```

---

### Task 2: Layout Components (Shell, Sidebar, NavBar)

**Files:**
- Modify: `frontend/src/views/layout/AppLayout.vue`
- Modify: `frontend/src/views/layout/SideMenu.vue`
- Modify: `frontend/src/views/layout/NavBar.vue`

- [ ] **Step 1: Rewrite AppLayout.vue**

```vue
<template>
  <div class="app-layout">
    <el-container>
      <el-aside :width="isCollapsed ? '64px' : '220px'" class="layout-aside">
        <SideMenu :is-collapsed="isCollapsed" @toggle="toggleSidebar" />
      </el-aside>
      <el-container class="layout-main">
        <el-header class="layout-header" height="64px">
          <NavBar :is-collapsed="isCollapsed" @toggle="toggleSidebar" />
        </el-header>
        <el-main class="layout-main-content">
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
.app-layout { height: 100vh; overflow: hidden; display: flex; background: var(--color-surface-bg); }
.layout-aside {
  background: var(--color-sidebar-bg);
  transition: width var(--transition);
  overflow: hidden;
  flex-shrink: 0;
}
.layout-main { flex-direction: column; overflow: hidden; min-width: 0; }
.layout-header {
  background: white;
  border-bottom: 1px solid var(--color-neutral-200);
  padding: 0;
  display: flex;
  align-items: center;
  flex-shrink: 0;
}
.layout-main-content {
  background: var(--color-surface-bg);
  overflow-y: auto;
  padding: 24px;
}
</style>
```

- [ ] **Step 2: Rewrite SideMenu.vue**

```vue
<template>
  <div class="side-menu">
    <div class="menu-logo" @click="router.push('/')">
      <div class="logo-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5z"/>
          <path d="M2 17l10 5 10-5"/>
          <path d="M2 12l10 5 10-5"/>
        </svg>
      </div>
      <span v-show="!isCollapsed" class="logo-text">AutoTest</span>
    </div>

    <nav class="menu-nav">
      <div class="menu-section">
        <span v-show="!isCollapsed" class="menu-section-title">主导航</span>
        <router-link
          v-for="item in mainMenu"
          :key="item.path"
          :to="item.path"
          class="menu-item"
          :class="{ active: isActive(item.path) }"
        >
          <component :is="item.icon" class="menu-icon" />
          <span v-show="!isCollapsed" class="menu-text">{{ item.label }}</span>
        </router-link>
      </div>

      <div v-if="authStore.user?.is_superuser" class="menu-section">
        <span v-show="!isCollapsed" class="menu-section-title">系统</span>
        <router-link
          v-for="item in adminMenu"
          :key="item.path"
          :to="item.path"
          class="menu-item"
          :class="{ active: isActive(item.path) }"
        >
          <component :is="item.icon" class="menu-icon" />
          <span v-show="!isCollapsed" class="menu-text">{{ item.label }}</span>
        </router-link>
      </div>
    </nav>

    <div class="menu-footer">
      <div v-show="!isCollapsed" class="user-card">
        <el-avatar :size="32" class="user-avatar">{{ avatarText }}</el-avatar>
        <div class="user-info">
          <span class="user-name">{{ displayName }}</span>
          <span class="user-role">{{ authStore.user?.is_superuser ? '管理员' : '用户' }}</span>
        </div>
      </div>
      <button class="collapse-btn" @click="$emit('toggle')">
        <Expand v-if="isCollapsed" />
        <Fold v-else />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Fold, Expand } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

defineProps<{ isCollapsed: boolean }>()
defineEmits<{ (e: 'toggle'): void }>()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const displayName = computed(() => authStore.user?.full_name || authStore.user?.username || '用户')
const avatarText = computed(() => displayName.value.charAt(0).toUpperCase())

const EnvironmentIcon = () => h('svg', { width: 20, height: 20, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
  h('rect', { x: 2, y: 3, width: 20, height: 14, rx: 2 }),
  h('line', { x1: 8, y1: 21, x2: 16, y2: 21 }),
  h('line', { x1: 12, y1: 17, x2: 12, y2: 21 })
])
const ApiIcon = () => h('svg', { width: 20, height: 20, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
  h('path', { d: 'M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z' }),
  h('polyline', { points: '22,6 12,13 2,6' })
])
const TestIcon = () => h('svg', { width: 20, height: 20, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
  h('path', { d: 'M9 11l3 3L22 4' }),
  h('path', { d: 'M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11' })
])
const TeamIcon = () => h('svg', { width: 20, height: 20, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
  h('path', { d: 'M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2' }),
  h('circle', { cx: 9, cy: 7, r: 4 }),
  h('path', { d: 'M23 21v-2a4 4 0 0 0-3-3.87' }),
  h('path', { d: 'M16 3.13a4 4 0 0 1 0 7.75' })
])
const UserIcon = () => h('svg', { width: 20, height: 20, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
  h('path', { d: 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2' }),
  h('circle', { cx: 12, cy: 7, r: 4 })
])

const mainMenu = [
  { path: '/environments', label: '环境管理', icon: EnvironmentIcon },
  { path: '/apis', label: '接口管理', icon: ApiIcon },
  { path: '/testcase', label: '测试用例', icon: TestIcon },
]
const adminMenu = [
  { path: '/admin/teams', label: '团队管理', icon: TeamIcon },
  { path: '/admin/users', label: '用户管理', icon: UserIcon },
]

function isActive(path: string) {
  return route.path.startsWith(path)
}
</script>

<style scoped>
.side-menu { height: 100%; display: flex; flex-direction: column; background: var(--color-sidebar-bg); }
.menu-logo {
  height: 64px; display: flex; align-items: center; gap: 12px; padding: 0 16px;
  cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.06); flex-shrink: 0;
}
.logo-icon {
  width: 36px; height: 36px; background: linear-gradient(135deg, var(--color-primary-500), var(--color-primary-600));
  border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; flex-shrink: 0;
}
.logo-text { color: white; font-size: 17px; font-weight: 700; white-space: nowrap; }
.menu-nav { flex: 1; overflow-y: auto; padding: 16px 12px; }
.menu-section { margin-bottom: 24px; }
.menu-section-title {
  display: block; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;
  color: var(--color-sidebar-muted); padding: 0 12px; margin-bottom: 8px;
}
.menu-item {
  display: flex; align-items: center; gap: 12px; padding: 10px 12px; border-radius: 8px;
  color: var(--color-sidebar-text); text-decoration: none; font-size: 14px; font-weight: 500;
  transition: all var(--transition-fast); margin-bottom: 4px;
}
.menu-item:hover { background: rgba(255,255,255,0.05); }
.menu-item.active {
  background: rgba(99,102,241,0.15); color: #a5b4fc;
  border-left: 3px solid var(--color-primary-500); margin-left: -3px; padding-left: 9px;
}
.menu-icon { width: 20px; height: 20px; flex-shrink: 0; }
.menu-text { white-space: nowrap; }
.menu-footer { padding: 16px 12px; border-top: 1px solid rgba(255,255,255,0.06); flex-shrink: 0; }
.user-card {
  display: flex; align-items: center; gap: 10px; padding: 10px 12px;
  background: rgba(255,255,255,0.05); border-radius: 8px; margin-bottom: 12px;
}
.user-avatar { background: var(--color-primary-500); color: white; font-size: 13px; font-weight: 600; flex-shrink: 0; }
.user-info { display: flex; flex-direction: column; min-width: 0; }
.user-name { font-size: 13px; font-weight: 500; color: var(--color-sidebar-text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.user-role { font-size: 11px; color: var(--color-sidebar-muted); }
.collapse-btn {
  width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px;
  padding: 10px; background: rgba(255,255,255,0.05); border: none; border-radius: 8px;
  color: var(--color-sidebar-muted); font-size: 14px; cursor: pointer; transition: all var(--transition-fast);
}
.collapse-btn:hover { background: rgba(255,255,255,0.1); color: var(--color-sidebar-text); }
</style>
```

- [ ] **Step 3: Rewrite NavBar.vue**

```vue
<template>
  <header class="navbar">
    <div class="navbar-left">
      <button class="collapse-btn" @click="$emit('toggle')">
        <Fold v-if="!isCollapsed" />
        <Expand v-else />
      </button>
      <el-breadcrumb separator="/" class="breadcrumb">
        <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path">
          <router-link v-if="item.path && !item.isLast" :to="item.path" class="breadcrumb-link">{{ item.title }}</router-link>
          <span v-else class="breadcrumb-current">{{ item.title }}</span>
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>
    <div class="navbar-right">
      <el-dropdown trigger="click" @command="handleCommand">
        <button class="user-btn">
          <el-avatar :size="32" class="user-avatar">{{ avatarText }}</el-avatar>
          <span class="user-name">{{ displayName }}</span>
          <el-icon class="user-arrow"><ArrowDown /></el-icon>
        </button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="logout">
              <el-icon><SwitchButton /></el-icon>
              <span>退出登录</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Fold, Expand, ArrowDown, SwitchButton } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

defineProps<{ isCollapsed: boolean }>()
defineEmits<{ (e: 'toggle'): void }>()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const displayName = computed(() => authStore.user?.full_name || authStore.user?.username || '用户')
const avatarText = computed(() => displayName.value.charAt(0).toUpperCase())
const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta?.title)
  return matched.map((item, index) => ({
    title: item.meta.title as string,
    path: index === matched.length - 1 ? null : item.path,
    isLast: index === matched.length - 1
  }))
})

async function handleCommand(command: string) {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', { type: 'warning' })
      await authStore.logout()
      router.push('/login')
    } catch {}
  }
}
</script>

<style scoped>
.navbar {
  width: 100%; height: 64px; display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px; background: white;
}
.navbar-left { display: flex; align-items: center; gap: 20px; }
.collapse-btn {
  display: flex; align-items: center; justify-content: center; width: 36px; height: 36px;
  border: none; background: transparent; border-radius: 8px; cursor: pointer; color: var(--color-neutral-500);
  transition: all var(--transition-fast);
}
.collapse-btn:hover { background: var(--color-neutral-100); color: var(--color-neutral-700); }
.breadcrumb { display: flex; align-items: center; }
.breadcrumb-link { color: var(--color-neutral-500); text-decoration: none; transition: color var(--transition-fast); }
.breadcrumb-link:hover { color: var(--color-primary-500); }
.breadcrumb-current { color: var(--color-neutral-900); font-weight: 500; }
.navbar-right { display: flex; align-items: center; gap: 16px; }
.user-btn {
  display: flex; align-items: center; gap: 10px; padding: 6px 12px 6px 6px;
  background: transparent; border: 1px solid var(--color-neutral-200); border-radius: 10px;
  cursor: pointer; transition: all var(--transition-fast);
}
.user-btn:hover { background: var(--color-neutral-50); border-color: var(--color-neutral-300); }
.user-avatar { background: var(--color-primary-500); color: white; font-size: 13px; font-weight: 600; }
.user-name { font-size: 14px; font-weight: 500; color: var(--color-neutral-700); max-width: 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.user-arrow { color: var(--color-neutral-400); font-size: 12px; }
</style>
```

- [ ] **Step 4: Run build to verify**

Run: `cd frontend && npx vite build 2>&1 | tail -10`
Expected: Build succeeds

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/layout/
git commit -m "feat: implement new shell layout with collapsible sidebar"
```

---

### Task 3: Login & Register Pages

**Files:**
- Modify: `frontend/src/views/auth/Login.vue`
- Modify: `frontend/src/views/auth/Register.vue`

- [ ] **Step 1: Rewrite Login.vue**

```vue
<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-visual">
        <div class="visual-content">
          <div class="brand">
            <div class="brand-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                <path d="M2 17l10 5 10-5"/>
                <path d="M2 12l10 5 10-5"/>
              </svg>
            </div>
            <h1 class="brand-name">AutoTest</h1>
          </div>
          <p class="visual-tagline">企业级API测试平台</p>
          <div class="visual-features">
            <div class="feature-item">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 6"/></svg>
              <span>支持多环境管理</span>
            </div>
            <div class="feature-item">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 6"/></svg>
              <span>可视化接口调试</span>
            </div>
            <div class="feature-item">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 6"/></svg>
              <span>自动化测试编排</span>
            </div>
          </div>
        </div>
        <div class="visual-decoration">
          <div class="decoration-circle c1"></div>
          <div class="decoration-circle c2"></div>
          <div class="decoration-circle c3"></div>
        </div>
      </div>

      <div class="login-form-section">
        <div class="form-container">
          <div class="form-header">
            <h2 class="form-title">欢迎回来</h2>
            <p class="form-subtitle">请登录您的账号继续</p>
          </div>
          <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin">
            <div class="form-group">
              <label class="form-label">用户名</label>
              <el-input v-model="form.username" placeholder="请输入用户名" size="large" :prefix-icon="User" />
            </div>
            <div class="form-group">
              <label class="form-label">密码</label>
              <el-input v-model="form.password" type="password" placeholder="请输入密码" size="large" :prefix-icon="Lock" show-password @keyup.enter="handleLogin" />
            </div>
            <div class="form-options">
              <el-checkbox v-model="rememberMe">记住我</el-checkbox>
            </div>
            <el-button type="primary" size="large" :loading="loading" class="login-button" @click="handleLogin">登录</el-button>
          </el-form>
          <div class="form-footer">
            还没有账号？<router-link to="/register" class="link">立即注册</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const rememberMe = ref(false)
const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await authStore.login({ username: form.username, password: form.password })
    ElMessage.success('登录成功')
    router.push((route.query.redirect as string) || '/')
  } catch (error: any) {
    const status = error.response?.status
    if (status === 423) ElMessage.error(error.response?.data?.detail || '账号已锁定')
    else if (status === 401) ElMessage.error(error.response?.data?.detail || '用户名或密码错误')
    else ElMessage.error(error.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); padding: 20px;
}
.login-card {
  display: flex; width: 960px; max-width: 100%; min-height: 560px;
  background: white; border-radius: 20px; box-shadow: var(--shadow-lg); overflow: hidden;
}
.login-visual {
  flex: 1; background: linear-gradient(135deg, var(--color-primary-500) 0%, var(--color-primary-700) 100%);
  display: flex; align-items: center; justify-content: center; padding: 48px;
  position: relative; overflow: hidden;
}
.visual-content { position: relative; z-index: 1; color: white; text-align: center; }
.brand { display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 16px; }
.brand-icon {
  width: 56px; height: 56px; background: rgba(255,255,255,0.2); border-radius: 14px;
  display: flex; align-items: center; justify-content: center; backdrop-filter: blur(10px);
}
.brand-name { font-size: 32px; font-weight: 700; margin: 0; }
.visual-tagline { font-size: 16px; opacity: 0.9; margin: 0 0 40px 0; }
.visual-features { display: flex; flex-direction: column; gap: 16px; text-align: left; }
.feature-item { display: flex; align-items: center; gap: 12px; font-size: 14px; opacity: 0.9; }
.feature-item svg { flex-shrink: 0; opacity: 0.8; }
.visual-decoration { position: absolute; inset: 0; overflow: hidden; }
.decoration-circle { position: absolute; border-radius: 50%; background: rgba(255,255,255,0.1); }
.c1 { width: 300px; height: 300px; top: -100px; right: -100px; }
.c2 { width: 200px; height: 200px; bottom: -50px; left: -50px; }
.c3 { width: 150px; height: 150px; bottom: 20%; right: -30px; }
.login-form-section { flex: 1; display: flex; align-items: center; justify-content: center; padding: 48px; }
.form-container { width: 100%; max-width: 320px; }
.form-header { margin-bottom: 32px; }
.form-title { font-size: 26px; font-weight: 700; color: var(--color-neutral-900); margin: 0 0 8px 0; }
.form-subtitle { font-size: 14px; color: var(--color-neutral-500); margin: 0; }
.login-form { display: flex; flex-direction: column; gap: 20px; }
.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-label { font-size: 14px; font-weight: 500; color: var(--color-neutral-700); }
.form-options { display: flex; align-items: center; justify-content: space-between; }
.login-button { width: 100%; height: 48px; font-size: 16px; font-weight: 600; border-radius: 10px; }
.form-footer { text-align: center; margin-top: 24px; font-size: 14px; color: var(--color-neutral-500); }
.link { color: var(--color-primary-500); text-decoration: none; font-weight: 500; }
.link:hover { text-decoration: underline; }
@media (max-width: 768px) {
  .login-card { flex-direction: column; width: 100%; max-width: 420px; }
  .login-visual { padding: 32px; min-height: auto; }
  .visual-features { display: none; }
  .brand-name { font-size: 24px; }
  .login-form-section { padding: 32px 24px; }
}
</style>
```

- [ ] **Step 2: Rewrite Register.vue**

```vue
<template>
  <div class="register-page">
    <div class="register-card">
      <div class="register-visual">
        <div class="visual-content">
          <div class="brand">
            <div class="brand-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                <path d="M2 17l10 5 10-5"/>
                <path d="M2 12l10 5 10-5"/>
              </svg>
            </div>
            <h1 class="brand-name">AutoTest</h1>
          </div>
          <p class="visual-tagline">企业级API测试平台</p>
          <div class="visual-features">
            <div class="feature-item">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 6"/></svg>
              <span>支持多环境管理</span>
            </div>
            <div class="feature-item">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 6"/></svg>
              <span>可视化接口调试</span>
            </div>
            <div class="feature-item">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 6"/></svg>
              <span>自动化测试编排</span>
            </div>
          </div>
        </div>
        <div class="visual-decoration">
          <div class="decoration-circle c1"></div>
          <div class="decoration-circle c2"></div>
          <div class="decoration-circle c3"></div>
        </div>
      </div>

      <div class="register-form-section">
        <div class="form-container">
          <div class="form-header">
            <h2 class="form-title">创建账号</h2>
            <p class="form-subtitle">开始使用 AutoTest</p>
          </div>
          <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleRegister">
            <div class="form-group">
              <label class="form-label">用户名</label>
              <el-input v-model="form.username" placeholder="3-50位字母数字下划线" size="large" :prefix-icon="User" />
            </div>
            <div class="form-group">
              <label class="form-label">邮箱</label>
              <el-input v-model="form.email" placeholder="请输入邮箱" size="large" :prefix-icon="Message" />
            </div>
            <div class="form-group">
              <label class="form-label">密码</label>
              <el-input v-model="form.password" type="password" placeholder="8-32位，含大小写字母和数字" size="large" :prefix-icon="Lock" show-password />
              <div v-if="form.password" class="password-strength">
                <span class="strength-label">密码强度：</span>
                <span :class="'strength-' + strengthClass">{{ strengthText }}</span>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">确认密码</label>
              <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入密码" size="large" :prefix-icon="Lock" show-password @keyup.enter="handleRegister" />
            </div>
            <el-button type="primary" size="large" :loading="loading" class="register-button" @click="handleRegister">注册</el-button>
          </el-form>
          <div class="form-footer">
            已有账号？<router-link to="/login" class="link">去登录</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock, Message } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const form = reactive({ username: '', email: '', password: '', confirmPassword: '' })

const validateConfirm = (_rule: any, value: string, callback: any) => {
  if (value !== form.password) callback(new Error('两次输入的密码不一致'))
  else callback()
}

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度为3-50个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, max: 32, message: '密码长度为8-32个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' }
  ]
}

const strengthClass = computed(() => {
  const pw = form.password
  if (!pw) return ''
  let score = 0
  if (pw.length >= 8) score++
  if (pw.length >= 12) score++
  if (/[A-Z]/.test(pw)) score++
  if (/[a-z]/.test(pw)) score++
  if (/\d/.test(pw)) score++
  if (/[^a-zA-Z0-9]/.test(pw)) score++
  if (score <= 2) return 'weak'
  if (score <= 4) return 'medium'
  return 'strong'
})
const strengthText = computed(() => ({ weak: '弱', medium: '中', strong: '强' }[strengthClass.value] || ''))

async function handleRegister() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await authStore.register({ username: form.username, email: form.email, password: form.password })
    ElMessage.success('注册成功')
    router.push('/')
  } catch (error: any) {
    const status = error.response?.status
    if (status === 409) ElMessage.error(error.response?.data?.detail || '用户名或邮箱已存在')
    else if (status === 422) ElMessage.error(error.response?.data?.detail || '密码强度不足')
    else ElMessage.error(error.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); padding: 20px;
}
.register-card {
  display: flex; width: 960px; max-width: 100%; min-height: 600px;
  background: white; border-radius: 20px; box-shadow: var(--shadow-lg); overflow: hidden;
}
.register-visual {
  flex: 1; background: linear-gradient(135deg, var(--color-primary-500) 0%, var(--color-primary-700) 100%);
  display: flex; align-items: center; justify-content: center; padding: 48px;
  position: relative; overflow: hidden;
}
.visual-content { position: relative; z-index: 1; color: white; text-align: center; }
.brand { display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 16px; }
.brand-icon {
  width: 56px; height: 56px; background: rgba(255,255,255,0.2); border-radius: 14px;
  display: flex; align-items: center; justify-content: center; backdrop-filter: blur(10px);
}
.brand-name { font-size: 32px; font-weight: 700; margin: 0; }
.visual-tagline { font-size: 16px; opacity: 0.9; margin: 0 0 40px 0; }
.visual-features { display: flex; flex-direction: column; gap: 16px; text-align: left; }
.feature-item { display: flex; align-items: center; gap: 12px; font-size: 14px; opacity: 0.9; }
.feature-item svg { flex-shrink: 0; opacity: 0.8; }
.visual-decoration { position: absolute; inset: 0; overflow: hidden; }
.decoration-circle { position: absolute; border-radius: 50%; background: rgba(255,255,255,0.1); }
.c1 { width: 300px; height: 300px; top: -100px; right: -100px; }
.c2 { width: 200px; height: 200px; bottom: -50px; left: -50px; }
.c3 { width: 150px; height: 150px; bottom: 20%; right: -30px; }
.register-form-section { flex: 1; display: flex; align-items: center; justify-content: center; padding: 48px; }
.form-container { width: 100%; max-width: 320px; }
.form-header { margin-bottom: 28px; }
.form-title { font-size: 26px; font-weight: 700; color: var(--color-neutral-900); margin: 0 0 8px 0; }
.form-subtitle { font-size: 14px; color: var(--color-neutral-500); margin: 0; }
.register-form { display: flex; flex-direction: column; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-label { font-size: 14px; font-weight: 500; color: var(--color-neutral-700); }
.password-strength { margin-top: 4px; font-size: 12px; }
.strength-label { color: var(--color-neutral-500); }
.strength-weak { color: var(--color-danger); }
.strength-medium { color: var(--color-warning); }
.strength-strong { color: var(--color-success); }
.register-button { width: 100%; height: 48px; font-size: 16px; font-weight: 600; border-radius: 10px; margin-top: 8px; }
.form-footer { text-align: center; margin-top: 20px; font-size: 14px; color: var(--color-neutral-500); }
.link { color: var(--color-primary-500); text-decoration: none; font-weight: 500; }
.link:hover { text-decoration: underline; }
@media (max-width: 768px) {
  .register-card { flex-direction: column; width: 100%; max-width: 420px; }
  .register-visual { padding: 32px; min-height: auto; }
  .visual-features { display: none; }
  .brand-name { font-size: 24px; }
  .register-form-section { padding: 32px 24px; }
}
</style>
```

- [ ] **Step 3: Run build to verify**

Run: `cd frontend && npx vite build 2>&1 | tail -10`
Expected: Build succeeds

- [ ] **Step 4: Commit**

```bash
git add frontend/src/views/auth/
git commit -m "feat: redesign login and register pages with new visual style"
```

---

### Task 4: API List Page (Three-Column Layout)

**Files:**
- Modify: `frontend/src/views/api/ApiList.vue`

- [ ] **Step 1: Rewrite ApiList.vue with three-column layout**

Key structure:
- Left panel (240px): Module tree filter
- Center panel (flex): Request builder with tabs (Method/Path, Params, Headers, Body, Auth, Pre/Post actions)
- Right panel (400px min): Response viewer (collapsible)

See the spec file for full design details.

Run: `cd frontend && npx vite build 2>&1 | tail -5`
Expected: Build succeeds

Commit: `git add frontend/src/views/api/ApiList.vue && git commit -m "feat: implement three-column API list layout"`

---

### Task 5: MethodTag & StatusTag Components

**Files:**
- Modify: `frontend/src/views/api/components/MethodTag.vue`
- Modify: `frontend/src/views/api/components/StatusTag.vue`

- [ ] **Step 1: Update MethodTag.vue**

Replace with:
```vue
<template>
  <span class="method-badge" :class="methodClass">{{ method }}</span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ method: string }>()

const methodClass = computed(() => `method-${props.method.toLowerCase()}`)
</script>

<style scoped>
.method-badge {
  @apply inline-flex items-center justify-center px-2.5 py-1 text-xs font-semibold rounded;
  min-width: 56px;
}
.method-get { background: var(--color-method-get-bg); color: var(--color-method-get); }
.method-post { background: var(--color-method-post-bg); color: var(--color-method-post); }
.method-put { background: var(--color-method-put-bg); color: var(--color-method-put); }
.method-delete { background: var(--color-method-delete-bg); color: var(--color-method-delete); }
.method-patch { background: var(--color-method-patch-bg); color: var(--color-method-patch); }
</style>
```

- [ ] **Step 2: Update StatusTag.vue**

Replace with:
```vue
<template>
  <span class="status-badge" :class="statusClass">{{ statusText }}</span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ status: string }>()

const statusClass = computed(() => {
  const map: Record<string, string> = {
    enabled: 'badge-success',
    disabled: 'badge-warning',
    deprecated: 'badge-danger'
  }
  return map[props.status] || 'badge-info'
})

const statusText = computed(() => {
  const map: Record<string, string> = {
    enabled: '启用',
    disabled: '禁用',
    deprecated: '废弃'
  }
  return map[props.status] || props.status
})
</script>

<style scoped>
.status-badge { @apply inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-full; }
.badge-success { background: var(--color-success-light); color: var(--color-success-dark); }
.badge-warning { background: var(--color-warning-light); color: var(--color-warning-dark); }
.badge-danger { background: var(--color-danger-light); color: var(--color-danger-dark); }
.badge-info { background: var(--color-info-light); color: #1e40af; }
</style>
```

Run: `cd frontend && npx vite build 2>&1 | tail -5`
Commit: `git add frontend/src/views/api/components/MethodTag.vue frontend/src/views/api/components/StatusTag.vue && git commit -m "feat: update method and status badge components with new color system"`

---

### Task 6: Environment List Page

**Files:**
- Modify: `frontend/src/views/environment/EnvironmentList.vue`

- [ ] **Step 1: Update styling to match new design system**

Update all class names from old system to new:
- `.page-layout` → `.page-container`
- `.page-header` → keep but update styles
- `.btn-primary` → `.btn-primary` (already consistent)
- `.search-input` → `.search-input` (already consistent)

Run build and commit when done.

---

### Task 7: Other List Pages (TestCase, Admin)

Apply consistent styling updates to remaining list pages following the same pattern as Task 6.

---

### Task 8: Verify & Test

- [ ] **Step 1: Run full build**

Run: `cd frontend && npx vite build 2>&1`
Expected: Build completes with no errors

- [ ] **Step 2: Start dev server**

Run: `cd frontend && npm run dev`
Expected: Dev server starts on port 8080

- [ ] **Step 3: Visual verification**

Open browser and verify:
- Login page renders correctly with new visual style
- Sidebar collapses/expands correctly
- API list page shows three-column layout
- Tables have proper styling

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: complete frontend redesign implementation"
```

---

## Spec Coverage Check

| Spec Requirement | Task |
|-----------------|------|
| Color palette (Indigo primary) | Task 1 |
| Collapsible sidebar | Task 2 |
| New NavBar | Task 2 |
| Login/Register pages | Task 3 |
| Three-column API layout | Task 4 |
| Method badges | Task 5 |
| Status badges | Task 5 |
| Environment list | Task 6 |
| TestCase list | Task 7 |
| Admin pages | Task 7 |

All spec requirements covered.

---

## Execution Options

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
