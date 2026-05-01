<template>
  <div class="api-list">
    <PageHeader title="接口管理" subtitle="管理 API 接口定义和调试">
      <template #actions>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">
          新建接口
        </el-button>
      </template>
    </PageHeader>

    <div class="api-layout">
      <aside class="api-sidebar">
        <div class="sidebar-header">
          <span class="sidebar-title">模块</span>
          <el-button size="small" :icon="Plus" @click="addModule" />
        </div>
        <div class="module-tree">
          <div
            class="tree-item"
            :class="{ active: selectedModuleId === null }"
            @click="selectedModuleId = null"
          >
            <el-icon><Folder /></el-icon>
            <span>全部接口</span>
            <span class="count">{{ apis.length }}</span>
          </div>
          <div
            v-for="mod in modules"
            :key="mod.id"
            class="tree-item"
            :class="{ active: selectedModuleId === mod.id }"
            @click="selectedModuleId = mod.id"
          >
            <el-icon><FolderOpened /></el-icon>
            <span>{{ mod.name }}</span>
            <span class="count">{{ mod.api_count || 0 }}</span>
          </div>
        </div>
      </aside>

      <main class="api-main">
        <div v-if="loading" class="loading-state">
          <el-icon class="is-loading"><Loading /></el-icon>
        </div>

        <el-table v-else :data="filteredApis" stripe style="width: 100%">
          <el-table-column label="接口名称" min-width="200">
            <template #default="{ row }">
              <div class="api-name-cell">
                <MethodBadge :method="row.method" />
                <span class="api-name">{{ row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="路径" min-width="200">
            <template #default="{ row }">
              <code class="api-path">{{ row.path }}</code>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <StatusBadge :status="row.status" />
            </template>
          </el-table-column>
          <el-table-column label="更新时间" width="160">
            <template #default="{ row }">
              {{ row.updated_at ? formatDate(row.updated_at) : '-' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="handleDebug(row)">调试</el-button>
              <el-button size="small" type="primary" plain @click="openEditDialog(row)">编辑</el-button>
              <el-button size="small" type="danger" plain @click="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </main>
    </div>

    <ApiEdit
      v-model="drawerVisible"
      :api="currentApi"
      @success="handleSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Folder, FolderOpened, Loading } from '@element-plus/icons-vue'
import { useApiStore } from '@/stores/api'
import type { ApiDefinition } from '@/types'
import PageHeader from '@/components/layout/PageHeader.vue'
import MethodBadge from '@/components/common/MethodBadge.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import ApiEdit from './ApiEdit.vue'

const store = useApiStore()
const { apis, modules, loading, selectedModuleId, filteredApis } = store

const drawerVisible = ref(false)
const currentApi = ref<ApiDefinition | null>(null)

onMounted(() => {
  store.fetchApis()
  store.fetchModules()
})

const openCreateDialog = () => {
  currentApi.value = null
  drawerVisible.value = true
}

const openEditDialog = (api: ApiDefinition) => {
  currentApi.value = { ...api }
  drawerVisible.value = true
}

const handleDebug = (api: ApiDefinition) => {
  ElMessage.info(`调试 API: ${api.name}`)
  // TODO: Open debug dialog
}

const handleDelete = async (api: ApiDefinition) => {
  try {
    await ElMessageBox.confirm(
      `确定删除接口 "${api.name}" 吗？`,
      '删除确认',
      { type: 'warning' }
    )
    await store.deleteApi(api.id!)
    ElMessage.success('删除成功')
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSuccess = () => {
  drawerVisible.value = false
  store.fetchApis()
}

const addModule = async () => {
  try {
    const { value: name } = await ElMessageBox.prompt('请输入模块名称', '新建模块')
    if (name) {
      await store.createModule({ name, team_id: 1 })
      store.fetchModules()
    }
  } catch (e) {
    // User cancelled
  }
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<style scoped>
.api-list {
  height: calc(100vh - var(--header-height) - var(--spacing-lg) * 2);
  display: flex;
  flex-direction: column;
}

.api-layout {
  display: flex;
  flex: 1;
  gap: var(--spacing-lg);
  min-height: 0;
}

.api-sidebar {
  width: 240px;
  background: var(--color-bg-card);
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
}

.sidebar-title {
  font-weight: 600;
  color: var(--color-text-primary);
}

.module-tree {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-sm);
}

.tree-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-lg);
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}

.tree-item:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-primary);
}

.tree-item.active {
  background: var(--color-primary-bg);
  color: var(--color-primary);
}

.tree-item .count {
  margin-left: auto;
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.api-main {
  flex: 1;
  background: var(--color-bg-card);
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border);
  padding: var(--spacing-lg);
  overflow: auto;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--color-text-muted);
}

.api-name-cell {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.api-name {
  font-weight: 500;
}

.api-path {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  background: var(--color-bg-hover);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
}
</style>