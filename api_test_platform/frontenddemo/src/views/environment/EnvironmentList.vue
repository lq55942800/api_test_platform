<template>
  <div class="environment-list">
    <PageHeader title="环境管理" subtitle="管理测试环境和服务配置">
      <template #actions>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">
          新建环境
        </el-button>
      </template>
    </PageHeader>

    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <div v-else-if="environments.length === 0" class="empty-state">
      <el-empty description="暂无环境">
        <el-button type="primary" @click="openCreateDialog">创建第一个环境</el-button>
      </el-empty>
    </div>

    <div v-else class="env-grid">
      <el-card
        v-for="env in environments"
        :key="env.id"
        class="env-card"
        shadow="hover"
      >
        <div class="env-card-header">
          <h3 class="env-name">{{ env.name }}</h3>
          <el-tag v-if="env.is_default" type="success" size="small">默认</el-tag>
        </div>
        <p v-if="env.description" class="env-desc">{{ env.description }}</p>
        <div class="env-meta">
          <span class="meta-item">
            <el-icon><Connection /></el-icon>
            {{ env.services?.length || 0 }} 个服务
          </span>
          <span class="meta-item">
            <el-icon><Setting /></el-icon>
            {{ env.variables?.length || 0 }} 个变量
          </span>
        </div>
        <div class="env-actions">
          <el-button size="small" @click="openEditDialog(env)">编辑</el-button>
          <el-button size="small" type="danger" plain @click="handleDelete(env)">删除</el-button>
        </div>
      </el-card>
    </div>

    <EnvironmentEdit
      v-model="dialogVisible"
      :environment="currentEnvironment"
      @success="handleSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Connection, Setting, Loading } from '@element-plus/icons-vue'
import { useEnvironmentStore } from '@/stores/environment'
import type { Environment } from '@/types'
import PageHeader from '@/components/layout/PageHeader.vue'
import EnvironmentEdit from './EnvironmentEdit.vue'

const store = useEnvironmentStore()
const { environments, loading } = store

const dialogVisible = ref(false)
const currentEnvironment = ref<Environment | null>(null)

onMounted(() => {
  store.fetchEnvironments()
})

const openCreateDialog = () => {
  currentEnvironment.value = null
  dialogVisible.value = true
}

const openEditDialog = (env: Environment) => {
  currentEnvironment.value = { ...env }
  dialogVisible.value = true
}

const handleDelete = async (env: Environment) => {
  try {
    await ElMessageBox.confirm(
      `确定删除环境 "${env.name}" 吗？`,
      '删除确认',
      { type: 'warning' }
    )
    await store.deleteEnvironment(env.id!)
    ElMessage.success('删除成功')
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSuccess = () => {
  dialogVisible.value = false
  store.fetchEnvironments()
}
</script>

<style scoped>
.environment-list {
  max-width: 1200px;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-2xl);
  color: var(--color-text-muted);
}

.empty-state {
  padding: var(--spacing-2xl);
}

.env-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--spacing-lg);
}

.env-card {
  border-radius: var(--radius-xl);
  transition: all var(--transition-fast);
}

.env-card:hover {
  transform: translateY(-2px);
}

.env-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-sm);
}

.env-name {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.env-desc {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-md);
}

.env-meta {
  display: flex;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-md);
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.env-actions {
  display: flex;
  gap: var(--spacing-sm);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border-light);
}
</style>