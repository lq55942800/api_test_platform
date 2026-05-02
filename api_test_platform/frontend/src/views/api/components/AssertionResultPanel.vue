<template>
  <div class="assertion-result-panel">
    <div v-if="!assertionResults || assertionResults.length === 0" class="empty-tip">
      暂无断言结果
    </div>
    <template v-else>
      <div class="summary-bar" v-if="summary">
        <span class="summary-item">
          <span class="summary-label">总计</span>
          <span class="summary-value">{{ summary.total }}</span>
        </span>
        <span class="summary-item passed">
          <span class="summary-label">通过</span>
          <span class="summary-value">{{ summary.passed }}</span>
        </span>
        <span class="summary-item failed">
          <span class="summary-label">失败</span>
          <span class="summary-value">{{ summary.failed }}</span>
        </span>
        <el-tag v-if="summary.all_passed" type="success" size="small">全部通过</el-tag>
        <el-tag v-else-if="summary.critical_failed > 0" type="danger" size="small">关键断言失败</el-tag>
        <el-tag v-else type="warning" size="small">存在失败</el-tag>
      </div>

      <div class="result-list">
        <div
          v-for="result in assertionResults"
          :key="result.id"
          class="result-item"
          :class="{ 'result-passed': result.passed, 'result-failed': !result.passed }"
        >
          <div class="result-header">
            <span class="result-icon">{{ result.passed ? '✓' : '✗' }}</span>
            <span class="result-name">{{ result.name }}</span>
            <el-tag size="small" :type="getSeverityType(result.severity)">
              {{ getSeverityLabel(result.severity) }}
            </el-tag>
            <span class="result-type">{{ result.type }}</span>
            <span class="result-duration" v-if="result.duration_ms">{{ result.duration_ms }}ms</span>
          </div>
          <div v-if="!result.passed" class="result-detail">
            <div class="detail-row" v-if="result.operator">
              <span class="detail-label">运算符：</span>
              <span class="detail-value">{{ result.operator }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">期望值：</span>
              <span class="detail-value expected">{{ formatValue(result.expected) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">实际值：</span>
              <span class="detail-value actual">{{ formatValue(result.actual) }}</span>
            </div>
            <div class="detail-message" v-if="result.message">{{ result.message }}</div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { AssertionExecutionResult, AssertionSummary } from '@/types/api'

defineProps<{
  assertionResults: AssertionExecutionResult[] | null | undefined
  summary: AssertionSummary | null | undefined
}>()

function getSeverityType(severity: string): string {
  const map: Record<string, string> = { critical: 'danger', warning: 'warning', info: 'info' }
  return map[severity] || 'info'
}

function getSeverityLabel(severity: string): string {
  const map: Record<string, string> = { critical: '严重', warning: '警告', info: '信息' }
  return map[severity] || severity
}

function formatValue(val: any): string {
  if (val === null || val === undefined) return '(空)'
  if (typeof val === 'object') return JSON.stringify(val)
  return String(val)
}
</script>

<style scoped>
.assertion-result-panel {
  width: 100%;
}

.empty-tip {
  color: #909399;
  font-size: 13px;
  text-align: center;
  padding: 16px;
}

.summary-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 12px;
  background-color: #f9fafb;
  border-radius: 6px;
  margin-bottom: 12px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.summary-label {
  font-size: 12px;
  color: #6b6375;
}

.summary-value {
  font-size: 14px;
  font-weight: 600;
  color: #08060d;
}

.summary-item.passed .summary-value {
  color: #67C23A;
}

.summary-item.failed .summary-value {
  color: #F56C6C;
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

.result-passed {
  background-color: #f0f9eb;
  border-left-color: #67C23A;
}

.result-failed {
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

.result-passed .result-icon {
  color: #67C23A;
}

.result-failed .result-icon {
  color: #F56C6C;
}

.result-name {
  font-weight: 500;
  color: #08060d;
}

.result-type {
  color: #6b6375;
  font-size: 12px;
}

.result-duration {
  color: #909399;
  font-size: 12px;
  margin-left: auto;
  font-family: ui-monospace, Consolas, monospace;
}

.result-detail {
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.detail-row {
  display: flex;
  align-items: flex-start;
  gap: 4px;
  font-size: 12px;
  margin-bottom: 2px;
}

.detail-label {
  color: #6b6375;
  white-space: nowrap;
}

.detail-value {
  font-family: ui-monospace, Consolas, monospace;
  word-break: break-all;
}

.detail-value.expected {
  color: #67C23A;
}

.detail-value.actual {
  color: #F56C6C;
}

.detail-message {
  font-size: 12px;
  color: #6b6375;
  margin-top: 4px;
  font-style: italic;
}
</style>
