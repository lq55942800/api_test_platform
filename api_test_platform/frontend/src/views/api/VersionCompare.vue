<template>
  <el-dialog
    v-model="visible"
    title="版本对比"
    width="900px"
    :close-on-click-modal="false"
  >
    <div class="compare-header">
      <span>版本：</span>
      <el-select v-model="leftVersion" size="small" style="width: 100px">
        <el-option
          v-for="v in versions"
          :key="v.version_number"
          :label="`v${v.version_number}`"
          :value="v.version_number"
        />
      </el-select>
      <span class="compare-arrow">&larr;&rarr;</span>
      <el-select v-model="rightVersion" size="small" style="width: 100px">
        <el-option
          v-for="v in versions"
          :key="v.version_number"
          :label="`v${v.version_number}`"
          :value="v.version_number"
        />
      </el-select>
      <el-button type="primary" link size="small" @click="handleCompare">对比</el-button>
    </div>

    <div class="compare-content" v-loading="versionStore.loading">
      <div v-if="!versionDiff" class="empty-state">
        <el-empty description="选择版本后点击对比" :image-size="80" />
      </div>

      <div v-else>
        <div class="diff-summary" v-if="versionDiff.summary">
          <div class="summary-title">变更摘要：</div>
          <div class="summary-text">{{ versionDiff.summary }}</div>
        </div>

        <div class="diff-list" v-if="versionDiff.changes.length > 0">
          <div
            v-for="(change, index) in versionDiff.changes"
            :key="index"
            class="diff-item"
            :class="getChangeClass(change.type)"
          >
            <span class="diff-type">{{ getChangeLabel(change.type) }}</span>
            <span class="diff-field">{{ change.field }}</span>
            <span class="diff-detail" v-if="change.old_value">
              旧值: {{ JSON.stringify(change.old_value) }}
            </span>
            <span class="diff-detail" v-if="change.new_value">
              新值: {{ JSON.stringify(change.new_value) }}
            </span>
          </div>
        </div>

        <div v-else class="no-changes">
          两个版本无差异
        </div>
      </div>
    </div>

    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
      <el-button
        v-if="leftVersion && rightVersion"
        type="warning"
        @click="handleRollback"
      >
        回滚到v{{ Math.min(leftVersion, rightVersion) }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useVersionStore, useApiStore } from '@/stores/api'

const props = defineProps<{
  modelValue: boolean
  apiId?: number
  v1?: number
  v2?: number
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const versionStore = useVersionStore()
const apiStore = useApiStore()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const versions = computed(() => versionStore.versions)
const versionDiff = computed(() => versionStore.versionDiff)

const leftVersion = ref(props.v1 || 0)
const rightVersion = ref(props.v2 || 0)

watch(() => [props.v1, props.v2], ([v1, v2]) => {
  if (v1) leftVersion.value = v1
  if (v2) rightVersion.value = v2
  if (v1 && v2 && props.apiId) {
    handleCompare()
  }
})

async function handleCompare() {
  if (!props.apiId || !leftVersion.value || !rightVersion.value) return
  await versionStore.compareVersions(props.apiId, leftVersion.value, rightVersion.value)
}

async function handleRollback() {
  if (!props.apiId) return
  const targetVersion = Math.min(leftVersion.value, rightVersion.value)
  try {
    await ElMessageBox.confirm(
      `确定回滚到版本v${targetVersion}？将创建新版本。`,
      '提示',
      { type: 'warning' }
    )
    await versionStore.rollbackVersion(props.apiId, targetVersion)
    ElMessage.success('回滚成功')
    await apiStore.fetchApi(props.apiId)
  } catch (error: any) {
    if (error !== 'cancel') { /* handled */ }
  }
}

function getChangeClass(type: string) {
  if (type.includes('added') || type === 'param_added') return 'change-added'
  if (type.includes('removed') || type === 'param_removed') return 'change-removed'
  if (type.includes('modified') || type === 'param_modified') return 'change-modified'
  return ''
}

function getChangeLabel(type: string) {
  const labels: Record<string, string> = {
    param_added: '+ 新增',
    param_removed: '- 删除',
    param_modified: '~ 修改',
    path_changed: '~ 路径变更',
    method_changed: '~ 方法变更',
    body_changed: '~ 请求体变更',
    response_changed: '~ 响应变更',
    description_changed: '~ 描述变更'
  }
  return labels[type] || type
}
</script>

<style scoped>
.compare-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.compare-arrow {
  font-size: 16px;
  color: #6b6375;
}

.compare-content {
  min-height: 200px;
}

.empty-state {
  padding: 48px 0;
}

.diff-summary {
  margin-bottom: 16px;
  padding: 12px;
  background-color: #f9fafb;
  border-radius: 6px;
  border: 1px solid #e5e4e7;
}

.summary-title {
  font-size: 14px;
  font-weight: 600;
  color: #08060d;
  margin-bottom: 4px;
}

.summary-text {
  font-size: 13px;
  color: #6b6375;
  line-height: 1.5;
}

.diff-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.diff-item {
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.change-added {
  background-color: #E8F5E9;
  color: #2E7D32;
}

.change-removed {
  background-color: #FFEBEE;
  color: #C62828;
}

.change-modified {
  background-color: #FFF8E1;
  color: #F57F17;
}

.diff-type {
  font-weight: 600;
  font-family: ui-monospace, Consolas, monospace;
}

.diff-field {
  font-family: ui-monospace, Consolas, monospace;
}

.diff-detail {
  font-size: 12px;
  color: #6b6375;
}

.no-changes {
  text-align: center;
  padding: 48px 0;
  color: #6b6375;
  font-size: 14px;
}
</style>
