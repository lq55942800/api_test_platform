<template>
  <div class="response-viewer">
    <div v-if="!result" class="empty-state">
      <el-empty description="发送请求后查看响应结果" :image-size="80" />
    </div>
    <div v-else class="response-content">
      <div class="status-bar">
        <span class="status-code" :class="statusClass">{{ result.status_code || '-' }}</span>
        <span class="elapsed" :class="elapsedClass">{{ result.elapsed_ms ? result.elapsed_ms + 'ms' : '-' }}</span>
      </div>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="Response" name="body">
          <div class="body-content">
            <pre class="response-body">{{ formatBody }}</pre>
          </div>
        </el-tab-pane>
        <el-tab-pane label="Request URL" name="requestUrl">
          <div class="url-content">
            <div class="url-info">
              <span class="url-label">完整URL：</span>
              <span class="url-value">{{ fullRequestUrl }}</span>
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="Request Headers" name="requestHeaders">
          <el-table :data="requestHeaderList" border size="small" v-if="requestHeaderList.length > 0">
            <el-table-column prop="key" label="名称" min-width="200" />
            <el-table-column prop="value" label="值" min-width="300" />
          </el-table>
          <el-empty v-else description="无请求头" :image-size="60" />
        </el-tab-pane>
        <el-tab-pane label="Response Headers" name="headers">
          <el-table :data="headerList" border size="small" v-if="headerList.length > 0">
            <el-table-column prop="key" label="名称" min-width="200" />
            <el-table-column prop="value" label="值" min-width="300" />
          </el-table>
          <el-empty v-else description="无响应头" :image-size="60" />
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { DebugResult } from '@/types/api'

const props = defineProps<{
  result: DebugResult | null
}>()

const activeTab = ref('body')

const statusClass = computed(() => {
  const code = props.result?.status_code
  if (!code) return ''
  if (code >= 200 && code < 300) return 'status-success'
  if (code >= 300 && code < 400) return 'status-redirect'
  if (code >= 400 && code < 500) return 'status-client-error'
  return 'status-server-error'
})

const elapsedClass = computed(() => {
  const ms = props.result?.elapsed_ms
  if (!ms) return ''
  if (ms < 100) return 'elapsed-fast'
  if (ms < 500) return 'elapsed-normal'
  return 'elapsed-slow'
})

const formatBody = computed(() => {
  const body = props.result?.body
  if (!body) return ''
  try {
    return JSON.stringify(JSON.parse(body), null, 2)
  } catch {
    return body
  }
})

const headerList = computed(() => {
  const headers = props.result?.headers
  if (!headers) return []
  return Object.entries(headers).map(([key, value]) => ({ key, value: String(value) }))
})

const fullRequestUrl = computed(() => {
  return props.result?.request_url || '无'
})

const requestHeaderList = computed(() => {
  const headers = props.result?.request_headers
  if (!headers) return []
  return Object.entries(headers).map(([key, value]) => ({ key, value: String(value) }))
})
</script>

<style scoped>
.response-viewer {
  width: 100%;
}

.empty-state {
  padding: 24px 0;
}

.status-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
  padding: 8px 12px;
  background-color: #f9fafb;
  border-radius: 6px;
}

.status-code {
  font-size: 16px;
  font-weight: 700;
  font-family: ui-monospace, Consolas, monospace;
}

.status-success { color: #67C23A; }
.status-redirect { color: #409EFF; }
.status-client-error { color: #E6A23C; }
.status-server-error { color: #F56C6C; }

.elapsed {
  font-size: 13px;
  font-family: ui-monospace, Consolas, monospace;
}

.elapsed-fast { color: #67C23A; }
.elapsed-normal { color: #E6A23C; }
.elapsed-slow { color: #F56C6C; }

.body-content {
  max-height: 400px;
  overflow: auto;
}

.response-body {
  font-family: ui-monospace, Consolas, monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
  padding: 12px;
  background-color: #f9fafb;
  border-radius: 6px;
  border: 1px solid #e5e4e7;
}

.url-content {
  padding: 12px;
  background-color: #f9fafb;
  border-radius: 6px;
}

.url-info {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.url-label {
  font-weight: 600;
  color: #606266;
  flex-shrink: 0;
}

.url-value {
  font-family: ui-monospace, Consolas, monospace;
  font-size: 13px;
  word-break: break-all;
  color: #08060d;
}
</style>
