<template>
  <div class="action-result-panel">
    <div v-if="!results || results.length === 0" class="empty-tip">
      暂无操作结果
    </div>
    <div v-else class="result-list">
      <div
        v-for="result in results"
        :key="result.id"
        class="result-item"
        :class="{ 'result-success': result.success, 'result-error': !result.success }"
      >
        <div class="result-header">
          <span class="result-icon">{{ result.success ? '✓' : '✗' }}</span>
          <span class="result-name">{{ result.name }}</span>
          <el-tag size="small" :type="getTypeTagType(result.type)">{{ getTypeLabel(result.type) }}</el-tag>
          <span class="result-duration" v-if="result.duration_ms">{{ result.duration_ms }}ms</span>
        </div>
        <div v-if="!result.success && result.error" class="result-error-msg">
          {{ result.error }}
        </div>
        <div v-if="result.output && Object.keys(result.output).length > 0" class="result-output">
          <div v-for="(val, key) in result.output" :key="key" class="output-row">
            <span class="output-key">{{ key }}:</span>
            <span class="output-value">{{ formatValue(val) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { PRE_ACTION_TYPES, POST_ACTION_TYPES } from '@/types/api'
import type { ActionExecutionResult } from '@/types/api'

defineProps<{
  results: ActionExecutionResult[] | null | undefined
  phase?: 'pre_request' | 'post_request'
}>()

function getTypeLabel(type: string): string {
  const preType = PRE_ACTION_TYPES.find(t => t.value === type)
  if (preType) return preType.label
  const postType = POST_ACTION_TYPES.find(t => t.value === type)
  if (postType) return postType.label
  return type
}

function getTypeTagType(type: string): string {
  const map: Record<string, string> = {
    set_variable: '', param_builder: 'success', script: 'danger', database: 'warning',
    extract: 'success', assertion: '', post_script: 'danger'
  }
  return map[type] || ''
}

function formatValue(val: any): string {
  if (val === null || val === undefined) return '(空)'
  if (typeof val === 'object') return JSON.stringify(val)
  return String(val)
}
</script>

<style scoped>
.action-result-panel {
  width: 100%;
}

.empty-tip {
  color: #909399;
  font-size: 13px;
  text-align: center;
  padding: 16px;
}

.result-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.result-item {
  padding: 8px 12px;
  border-radius: 4px;
  border-left: 3px solid transparent;
}

.result-success {
  background-color: #f0f9eb;
  border-left-color: #67C23A;
}

.result-error {
  background-color: #fef0f0;
  border-left-color: #F56C6C;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.result-icon {
  font-weight: 700;
  font-size: 14px;
}

.result-success .result-icon {
  color: #67C23A;
}

.result-error .result-icon {
  color: #F56C6C;
}

.result-name {
  font-weight: 500;
  color: #08060d;
}

.result-duration {
  color: #909399;
  font-size: 12px;
  margin-left: auto;
  font-family: ui-monospace, Consolas, monospace;
}

.result-error-msg {
  margin-top: 4px;
  font-size: 12px;
  color: #F56C6C;
  font-family: ui-monospace, Consolas, monospace;
  word-break: break-all;
}

.result-output {
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.output-row {
  display: flex;
  align-items: flex-start;
  gap: 4px;
  font-size: 12px;
  margin-bottom: 2px;
}

.output-key {
  color: #6b6375;
  white-space: nowrap;
  font-family: ui-monospace, Consolas, monospace;
}

.output-value {
  color: #08060d;
  font-family: ui-monospace, Consolas, monospace;
  word-break: break-all;
}
</style>
