<template>
  <div class="testcase-list">
    <PageHeader title="测试用例" subtitle="创建和管理测试用例执行计划">
      <template #actions>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">
          新建用例
        </el-button>
      </template>
    </PageHeader>

    <div class="testcase-layout">
      <aside class="testcase-sidebar">
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
            <span>全部用例</span>
            <span class="count">{{ testCases.length }}</span>
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
            <span class="count">{{ mod.case_count || 0 }}</span>
          </div>
        </div>
      </aside>

      <main class="testcase-main">
        <div v-if="loading" class="loading-state">
          <el-icon class="is-loading"><Loading /></el-icon>
        </div>

        <div v-else-if="filteredTestCases.length === 0" class="empty-state">
          <el-empty description="暂无测试用例">
            <el-button type="primary" @click="openCreateDialog">创建第一个用例</el-button>
          </el-empty>
        </div>

        <div v-else class="testcase-grid">
          <el-card
            v-for="tc in filteredTestCases"
            :key="tc.id"
            class="testcase-card"
            shadow="hover"
          >
            <div class="tc-header">
              <span class="tc-name">{{ tc.name }}</span>
              <PriorityBadge :priority="tc.priority" />
            </div>
            <p v-if="tc.description" class="tc-desc">{{ tc.description }}</p>
            <div class="tc-meta">
              <StatusBadge :status="tc.status" />
              <span class="tc-steps">{{ tc.steps?.length || 0 }} 个步骤</span>
            </div>
            <div class="tc-actions">
              <el-button size="small" type="primary" @click="handleExecute(tc)">执行</el-button>
              <el-button size="small" @click="openEditDialog(tc)">编辑</el-button>
              <el-button size="small" type="danger" plain @click="handleDelete(tc)">删除</el-button>
            </div>
          </el-card>
        </div>
      </main>
    </div>

    <TestCaseEdit
      v-model="drawerVisible"
      :testcase="currentTestCase"
      @success="handleSuccess"
    />

    <TestCaseExecute
      v-model="executeDrawerVisible"
      :testcase="executeTarget"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Folder, FolderOpened, Loading } from '@element-plus/icons-vue'
import { useTestCaseStore } from '@/stores/testcase'
import type { TestCase } from '@/types'
import PageHeader from '@/components/layout/PageHeader.vue'
import PriorityBadge from '@/components/common/PriorityBadge.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import TestCaseEdit from './TestCaseEdit.vue'
import TestCaseExecute from './TestCaseExecute.vue'

const store = useTestCaseStore()
const { testCases, modules, loading, selectedModuleId, filteredTestCases } = store

const drawerVisible = ref(false)
const currentTestCase = ref<TestCase | null>(null)
const executeDrawerVisible = ref(false)
const executeTarget = ref<TestCase | null>(null)

onMounted(() => {
  store.fetchTestCases()
  store.fetchModules()
})

const openCreateDialog = () => {
  currentTestCase.value = null
  drawerVisible.value = true
}

const openEditDialog = (tc: TestCase) => {
  currentTestCase.value = { ...tc }
  drawerVisible.value = true
}

const handleExecute = (tc: TestCase) => {
  executeTarget.value = tc
  executeDrawerVisible.value = true
}

const handleDelete = async (tc: TestCase) => {
  try {
    await ElMessageBox.confirm(
      `确定删除测试用例 "${tc.name}" 吗？`,
      '删除确认',
      { type: 'warning' }
    )
    await store.deleteTestCase(tc.id!)
    ElMessage.success('删除成功')
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSuccess = () => {
  drawerVisible.value = false
  store.fetchTestCases()
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
</script>

<style scoped>
.testcase-list {
  height: calc(100vh - var(--header-height) - var(--spacing-lg) * 2);
  display: flex;
  flex-direction: column;
}

.testcase-layout {
  display: flex;
  flex: 1;
  gap: var(--spacing-lg);
  min-height: 0;
}

.testcase-sidebar {
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

.testcase-main {
  flex: 1;
  background: var(--color-bg-card);
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border);
  padding: var(--spacing-lg);
  overflow: auto;
}

.loading-state,
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 300px;
}

.testcase-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--spacing-md);
}

.testcase-card {
  border-radius: var(--radius-xl);
  transition: all var(--transition-fast);
}

.testcase-card:hover {
  transform: translateY(-2px);
}

.tc-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-sm);
}

.tc-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.tc-desc {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-md);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.tc-meta {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}

.tc-actions {
  display: flex;
  gap: var(--spacing-sm);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border-light);
}
</style>