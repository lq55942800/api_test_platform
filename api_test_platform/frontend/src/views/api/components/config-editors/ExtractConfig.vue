<template>
  <div class="extract-config">
    <div v-if="extractors.length === 0" class="empty-tip">
      <p>暂无提取规则</p>
    </div>

    <div v-else class="extract-list">
      <div
        v-for="(rule, index) in extractors"
        :key="index"
        class="extract-card"
      >
        <div class="card-header">
          <span class="card-index">{{ index + 1 }}</span>
          <span class="card-title">提取规则</span>
          <el-button type="danger" link size="small" style="margin-left: auto" @click="removeRule(index)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>

        <div class="card-body">
          <el-form label-width="80px" label-position="left" size="small">
            <el-form-item label="提取来源">
              <el-select v-model="rule.source" @change="onSourceChange(rule)">
                <el-option v-for="s in EXTRACT_SOURCES" :key="s.value" :label="s.label" :value="s.value" />
              </el-select>
            </el-form-item>

            <el-form-item v-if="rule.source !== 'elapsed_time'" label="表达式">
              <el-input
                v-model="rule.expression"
                :placeholder="getExpressionPlaceholder(rule.source)"
                @input="emitUpdate"
              />
            </el-form-item>

            <el-form-item v-if="rule.source !== 'elapsed_time'" label="默认值">
              <el-input
                v-model="rule.default_value"
                placeholder="提取为空时使用的默认值"
                @input="emitUpdate"
              />
            </el-form-item>

            <div class="var-row">
              <el-form-item label="变量名" class="var-name">
                <el-input v-model="rule.target_variable" placeholder="保存的变量名" @input="emitUpdate" />
              </el-form-item>
              <el-form-item label="作用域" class="var-scope">
                <el-select v-model="rule.target_scope" @change="emitUpdate">
                  <el-option v-for="s in VARIABLE_SCOPES" :key="s.value" :label="s.label" :value="s.value" />
                </el-select>
              </el-form-item>
            </div>
          </el-form>
        </div>
      </div>
    </div>

    <el-button size="small" plain style="margin-top: 8px; width: 100%" @click="addRule">
      <el-icon><Plus /></el-icon>添加提取规则
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
import { EXTRACT_SOURCES, VARIABLE_SCOPES, SOURCE_TYPE_MAP } from '@/types/api'
import type { ExtractorConfig } from '@/types/api'

const props = defineProps<{
  modelValue: Record<string, any>
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, any>]
}>()

const extractors = ref<ExtractorConfig[]>([...(props.modelValue?.extractors || [])])

watch(() => props.modelValue, (val) => {
  extractors.value = [...(val?.extractors || [])]
}, { deep: true })

function getExpressionPlaceholder(source: string): string {
  const map: Record<string, string> = {
    response_json: '$.data.field',
    response_text: '"key":"(.*?)"',
    response_header: 'Header名称，如 Content-Type',
    response_cookie: 'Cookie名称，如 session_id',
  }
  return map[source] || '表达式'
}

function onSourceChange(rule: ExtractorConfig) {
  rule.type = (SOURCE_TYPE_MAP as Record<string, string>)[rule.source] || 'jsonpath'
  rule.expression = ''
  rule.default_value = ''
  emitUpdate()
}

function addRule() {
  extractors.value.push({
    source: 'response_json',
    type: 'jsonpath',
    expression: '',
    default_value: '',
    target_variable: '',
    target_scope: 'temp',
  })
  emitUpdate()
}

function removeRule(index: number) {
  extractors.value.splice(index, 1)
  emitUpdate()
}

function emitUpdate() {
  emit('update:modelValue', { ...props.modelValue, extractors: extractors.value })
}
</script>

<style scoped>
.extract-config { width: 100%; }
.empty-tip { color: #909399; font-size: 13px; text-align: center; padding: 16px; }
.extract-list { display: flex; flex-direction: column; gap: 8px; }
.extract-card { background: #fafafa; border: 1px solid #e5e4e7; border-radius: 6px; overflow: hidden; }
.extract-card:hover { border-color: #aa3bff; }
.card-header { display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: #f5f5f7; border-bottom: 1px solid #e5e4e7; }
.card-index { width: 20px; height: 20px; border-radius: 50%; background: #aa3bff; color: #fff; font-size: 11px; font-weight: 600; display: flex; align-items: center; justify-content: center; }
.card-title { font-size: 13px; font-weight: 500; }
.card-body { padding: 12px; }
.var-row { display: flex; gap: 12px; }
.var-row .var-name { flex: 1; }
.var-row .var-scope { width: 140px; }
</style>
