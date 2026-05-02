<template>
  <div class="action-detail-renderer">
    <template v-if="action.type === 'set_variable'">
      <div v-if="variables.length" class="var-table">
        <div v-for="(v, i) in variables" :key="i" class="var-row">
          <el-tag size="small" effect="plain">{{ v.name || '-' }}</el-tag>
          <span class="var-arrow">=</span>
          <span class="var-value">{{ v.value ?? '-' }}</span>
        </div>
      </div>
      <span v-else class="detail-hint">无变量设置</span>
    </template>

    <template v-else-if="action.type === 'wait'">
      <span class="detail-hint">等待 {{ action.config?.duration ?? action.output?.duration ?? '-' }}{{ action.config?.unit === 'ms' ? 'ms' : 's' }}</span>
    </template>

    <template v-else-if="action.type === 'script'">
      <div v-if="scriptContent" class="script-preview">
        <pre class="script-code">{{ scriptContent }}</pre>
      </div>
      <div v-if="scriptLogs" class="script-logs">
        <span class="logs-label">输出日志:</span>
        <pre class="logs-content">{{ scriptLogs }}</pre>
      </div>
    </template>

    <template v-else-if="action.type === 'database'">
      <div class="db-detail">
        <div class="db-row"><span class="db-label">查询类型:</span> <el-tag size="small" effect="plain">{{ action.config?.query_type || 'select' }}</el-tag></div>
        <div v-if="action.config?.sql" class="db-row"><span class="db-label">SQL:</span> <code class="db-sql">{{ action.config.sql }}</code></div>
        <div v-if="action.output" class="db-row"><span class="db-label">结果:</span> <pre class="db-output">{{ formatOutput(action.output) }}</pre></div>
      </div>
    </template>

    <template v-else-if="action.type === 'extract'">
      <div v-if="extractors.length" class="extract-table">
        <div v-for="(e, i) in extractors" :key="i" class="extract-row">
          <el-tag size="small" type="success" effect="plain">{{ e.target_variable || e.variable_name || '-' }}</el-tag>
          <span class="extract-arrow">&larr;</span>
          <el-tag size="small" effect="plain">{{ e.source || '-' }}</el-tag>
          <code class="extract-expr">{{ e.expression || '-' }}</code>
          <span v-if="e.value !== undefined" class="extract-value">= {{ e.value }}</span>
          <span v-if="e.default_value" class="extract-default">(默认: {{ e.default_value }})</span>
        </div>
      </div>
      <div v-else-if="action.output && Object.keys(action.output).length" class="extract-kv">
        <div v-for="(val, key) in action.output" :key="key" class="extract-row">
          <el-tag size="small" type="success" effect="plain">{{ key }}</el-tag>
          <span class="extract-arrow">=</span>
          <span class="extract-value">{{ val }}</span>
        </div>
      </div>
      <span v-else class="detail-hint">无提取规则</span>
    </template>

    <template v-else>
      <div v-if="action.output && Object.keys(action.output).length">
        <pre class="fallback-output">{{ formatOutput(action.output) }}</pre>
      </div>
      <div v-if="action.error" class="action-error">{{ action.error }}</div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  action: any
}>()

const variables = computed(() => {
  const config = props.action.config
  if (!config) return []
  if (Array.isArray(config.variables)) return config.variables
  return []
})

const extractors = computed(() => {
  const config = props.action.config
  if (!config) return []
  if (Array.isArray(config.extractors)) return config.extractors
  return []
})

const scriptContent = computed(() => {
  const config = props.action.config
  if (!config?.script) return ''
  const s = config.script
  return s.length > 500 ? s.substring(0, 500) + '\n...' : s
})

const scriptLogs = computed(() => {
  const output = props.action.output
  if (!output) return ''
  if (typeof output === 'string') return output
  if (output.logs) return output.logs
  if (output.stdout) return output.stdout
  return ''
})

function formatOutput(output: any) {
  if (!output) return ''
  if (typeof output === 'string') return output
  try { return JSON.stringify(output, null, 2) } catch { return String(output) }
}
</script>

<style scoped>
.action-detail-renderer { font-size: 13px; }
.detail-hint { color: #909399; font-size: 12px; }

.var-table { display: flex; flex-direction: column; gap: 4px; }
.var-row { display: flex; align-items: center; gap: 6px; }
.var-arrow { color: #909399; font-weight: 600; }
.var-value { color: #303133; word-break: break-all; }

.script-preview { margin-bottom: 8px; }
.script-code { background: #1e1e1e; color: #d4d4d4; padding: 8px 10px; border-radius: 4px; font-family: ui-monospace, Consolas, monospace; font-size: 12px; margin: 0; white-space: pre-wrap; word-break: break-all; max-height: 200px; overflow-y: auto; line-height: 1.5; }
.script-logs { margin-top: 4px; }
.logs-label { font-size: 12px; color: #909399; }
.logs-content { background: #f5f7fa; padding: 6px 8px; border-radius: 4px; font-family: ui-monospace, Consolas, monospace; font-size: 11px; margin: 4px 0 0; white-space: pre-wrap; word-break: break-all; max-height: 100px; overflow-y: auto; }

.db-detail { display: flex; flex-direction: column; gap: 6px; }
.db-row { display: flex; align-items: flex-start; gap: 6px; }
.db-label { color: #909399; white-space: nowrap; font-size: 12px; min-width: 60px; }
.db-sql { font-family: ui-monospace, Consolas, monospace; font-size: 12px; background: #f5f7fa; padding: 2px 6px; border-radius: 3px; word-break: break-all; }
.db-output { font-family: ui-monospace, Consolas, monospace; font-size: 11px; margin: 0; white-space: pre-wrap; word-break: break-all; max-height: 150px; overflow-y: auto; background: #f5f7fa; padding: 6px; border-radius: 4px; }

.extract-table, .extract-kv { display: flex; flex-direction: column; gap: 4px; }
.extract-row { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.extract-arrow { color: #909399; font-weight: 600; }
.extract-expr { font-family: ui-monospace, Consolas, monospace; font-size: 12px; background: #f5f7fa; padding: 1px 4px; border-radius: 3px; }
.extract-value { color: #303133; font-weight: 500; word-break: break-all; }
.extract-default { color: #909399; font-size: 11px; }

.fallback-output { font-family: ui-monospace, Consolas, monospace; font-size: 12px; margin: 0; white-space: pre-wrap; word-break: break-all; background: #f5f7fa; padding: 6px; border-radius: 4px; max-height: 150px; overflow-y: auto; }
.action-error { color: #f56c6c; font-size: 12px; margin-top: 4px; }
</style>
