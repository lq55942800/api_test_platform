<template>
  <el-drawer
    :model-value="modelValue"
    @update:model-value="$emit('update:model-value', $event)"
    title="版本历史"
    direction="rtl"
    size="480px"
  >
    <div class="version-panel" v-loading="loading">
      <div v-if="versions.length === 0" class="empty-state">
        <el-empty description="暂无版本记录" />
      </div>
      <div v-else class="version-list">
        <div
          v-for="v in versions"
          :key="v.id"
          class="version-item"
          :class="{ current: v.is_current }"
        >
          <div class="version-header">
            <span class="version-number">v{{ v.version_number }}</span>
            <span v-if="v.is_current" class="current-badge">当前</span>
            <span class="version-time">{{ formatDate(v.created_at) }}</span>
          </div>
          <div class="version-meta">
            <span class="version-author">{{ v.changed_by_name || '系统' }}</span>
          </div>
          <div class="version-summary">{{ v.change_summary || '无变更描述' }}</div>
          <div class="version-actions">
            <el-button size="small" @click="handleCompare(v.version_number)">对比</el-button>
            <el-button size="small" type="primary" plain @click="handleRollback(v.version_number)" v-if="!v.is_current">
              回滚
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </el-drawer>

  <VersionCompare
    v-model="showCompare"
    :api-id="apiId"
    :version1="compareVersion"
    :version2="currentVersion"
  />
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useVersionStore } from '@/stores/api'
import VersionCompare from './VersionCompare.vue'

const props = defineProps<{
  modelValue: boolean
  apiId: number | null
}>()

const emit = defineEmits<{
  'update:model-value': [value: boolean]
}>()

const versionStore = useVersionStore()
const loading = ref(false)
const showCompare = ref(false)
const compareVersion = ref(0)

const versions = computed(() => versionStore.versions)
const currentVersion = computed(() => {
  const current = versions.value.find(v => v.is_current)
  return current?.version_number || 0
})

watch(() => props.modelValue, async (val) => {
  if (val && props.apiId) {
    loading.value = true
    try {
      await versionStore.fetchVersions(props.apiId)
    } finally {
      loading.value = false
    }
  }
})

function formatDate(date: string) {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

function handleCompare(version: number) {
  compareVersion.value = version
  showCompare.value = true
}

async function handleRollback(version: number) {
  try {
    await ElMessageBox.confirm(
      `确定回滚到版本 v${version}？将创建新版本。`,
      '版本回滚',
      { type: 'warning' }
    )
    await versionStore.rollback(props.apiId!, version)
    ElMessage.success('回滚成功')
    await versionStore.fetchVersions(props.apiId!)
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('回滚失败')
    }
  }
}
</script>

<style scoped>
.version-panel {
  padding: 0 4px;
}

.empty-state {
  padding: 40px 0;
}

.version-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.version-item {
  padding: 16px;
  background-color: #fafafa;
  border-radius: 8px;
  border: 1px solid #e5e4e7;
  transition: all 0.2s;
}

.version-item:hover {
  border-color: #aa3bff;
}

.version-item.current {
  background-color: rgba(170, 59, 255, 0.05);
  border-color: #aa3bff;
}

.version-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.version-number {
  font-size: 16px;
  font-weight: 600;
  color: #08060d;
}

.current-badge {
  font-size: 11px;
  padding: 2px 6px;
  background-color: #aa3bff;
  color: #ffffff;
  border-radius: 4px;
}

.version-time {
  margin-left: auto;
  font-size: 12px;
  color: #909399;
}

.version-meta {
  margin-bottom: 8px;
}

.version-author {
  font-size: 12px;
  color: #6b6375;
}

.version-summary {
  font-size: 13px;
  color: #606266;
  margin-bottom: 12px;
  line-height: 1.5;
}

.version-actions {
  display: flex;
  gap: 8px;
}
</style>
