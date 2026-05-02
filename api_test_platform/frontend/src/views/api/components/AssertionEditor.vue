<template>
  <div class="assertion-editor">
    <div class="action-toolbar">
      <el-dropdown trigger="click" @command="handleAdd">
        <el-button type="primary" link size="small">
          <el-icon style="margin-right: 4px"><Plus /></el-icon>添加断言
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item disabled class="dropdown-group-title">状态断言</el-dropdown-item>
            <el-dropdown-item v-for="at in STATUS_ASSERTION_TYPES" :key="at.value" :command="at.value">
              {{ at.label }}
            </el-dropdown-item>
            <el-dropdown-item divided disabled class="dropdown-group-title">内容断言</el-dropdown-item>
            <el-dropdown-item v-for="at in CONTENT_ASSERTION_TYPES" :key="at.value" :command="at.value">
              {{ at.label }}
            </el-dropdown-item>
            <el-dropdown-item divided disabled class="dropdown-group-title">高级断言</el-dropdown-item>
            <el-dropdown-item v-for="at in ADVANCED_ASSERTION_TYPES" :key="at.value" :command="at.value">
              {{ at.label }}
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <div v-if="assertions.length === 0" class="empty-tip">
      <el-icon :size="28" color="#c0c4cc"><Document /></el-icon>
      <p>暂无断言</p>
    </div>

    <div v-else class="assertion-list">
      <div
        v-for="(assertion, index) in assertions"
        :key="assertion.id"
        class="assertion-item"
        :class="{ 'assertion-disabled': !assertion.enabled, 'assertion-failed': assertion._lastFailed }"
      >
        <div class="assertion-header">
          <div class="assertion-left">
            <span class="assertion-order" :class="getOrderClass(assertion.type)">{{ index + 1 }}</span>
            <el-tag size="small" :type="getTypeTagType(assertion.type)" effect="plain">
              {{ getTypeLabel(assertion.type) }}
            </el-tag>
            <el-select v-model="assertion.config.severity" size="small" style="width: 72px" @change="emitUpdate">
              <el-option v-for="sl in SEVERITY_LEVELS" :key="sl.value" :label="sl.label" :value="sl.value" />
            </el-select>
          </div>
          <div class="assertion-right">
            <el-switch v-model="assertion.enabled" size="small" @change="emitUpdate" />
            <el-button size="small" link @click="moveUp(index)" :disabled="index === 0">
              <el-icon><Top /></el-icon>
            </el-button>
            <el-button size="small" link @click="moveDown(index)" :disabled="index === assertions.length - 1">
              <el-icon><Bottom /></el-icon>
            </el-button>
            <el-button type="danger" link size="small" @click="removeAssertion(index)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>

        <div class="assertion-config-area">
          <component
            :is="getConfigComponent(assertion.type)"
            :modelValue="assertion.config"
            @update:modelValue="(val: Record<string, any>) => updateConfig(assertion, val)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Plus, Delete, Top, Bottom, Document } from '@element-plus/icons-vue'
import { SEVERITY_LEVELS } from '@/types/api'
import type { Assertion, AssertionType } from '@/types/api'
import StatusCodeConfig from './config-editors/assertion-types/StatusCodeConfig.vue'
import HeaderAssertConfig from './config-editors/assertion-types/HeaderAssertConfig.vue'
import ResponseTimeConfig from './config-editors/assertion-types/ResponseTimeConfig.vue'
import BodyAssertConfig from './config-editors/assertion-types/BodyAssertConfig.vue'
import JsonSchemaConfig from './config-editors/assertion-types/JsonSchemaConfig.vue'
import ScriptAssertConfig from './config-editors/assertion-types/ScriptAssertConfig.vue'

const STATUS_ASSERTION_TYPES = [
  { value: 'status_code', label: '状态码' },
  { value: 'response_time', label: '响应时间' },
]

const CONTENT_ASSERTION_TYPES = [
  { value: 'header', label: '响应头' },
  { value: 'body', label: '响应体' },
]

const ADVANCED_ASSERTION_TYPES = [
  { value: 'json_schema', label: 'JSON Schema' },
  { value: 'script', label: 'Python脚本' },
]

const ALL_ASSERTION_TYPES = [...STATUS_ASSERTION_TYPES, ...CONTENT_ASSERTION_TYPES, ...ADVANCED_ASSERTION_TYPES]

const props = defineProps<{
  modelValue: Assertion[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Assertion[]]
}>()

const assertions = ref<Assertion[]>([...(props.modelValue || [])])

watch(() => props.modelValue, (val) => {
  assertions.value = [...(val || [])]
}, { deep: true })

const CONFIG_COMPONENT_MAP: Record<string, any> = {
  status_code: StatusCodeConfig,
  header: HeaderAssertConfig,
  response_time: ResponseTimeConfig,
  body: BodyAssertConfig,
  json_schema: JsonSchemaConfig,
  script: ScriptAssertConfig,
}

function getConfigComponent(type: string) {
  return CONFIG_COMPONENT_MAP[type] || StatusCodeConfig
}

function getTypeLabel(type: string): string {
  return ALL_ASSERTION_TYPES.find(t => t.value === type)?.label || type
}

function getTypeTagType(type: string): string {
  const map: Record<string, string> = {
    status_code: '',
    header: 'success',
    response_time: 'warning',
    body: '',
    json_schema: 'info',
    script: 'danger',
  }
  return map[type] || ''
}

function getOrderClass(type: string): string {
  if (STATUS_ASSERTION_TYPES.some(t => t.value === type)) return 'order-status'
  if (CONTENT_ASSERTION_TYPES.some(t => t.value === type)) return 'order-content'
  return 'order-advanced'
}

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

function getDefaultConfig(type: string): Record<string, any> {
  const defaults: Record<string, Record<string, any>> = {
    status_code: { operator: 'eq', expected: 200, message: '', severity: 'critical' },
    header: { header_name: '', operator: 'contains', expected: '', message: '', severity: 'critical' },
    response_time: { operator: 'lt', expected: 1000, message: '', severity: 'warning' },
    body: { mode: 'contains', expected: '', message: '', severity: 'critical' },
    json_schema: { schema_source: 'inline', schema_text: '', message: '', severity: 'critical' },
    script: { script: '', timeout: 10000, message: '', severity: 'critical' },
  }
  return { ...(defaults[type] || { severity: 'critical' }) }
}

function handleAdd(type: string) {
  const newAssertion: Assertion = {
    id: generateId(),
    enabled: true,
    name: getTypeLabel(type),
    type: type as AssertionType,
    phase: 'assertion',
    order: assertions.value.length,
    config: getDefaultConfig(type),
    description: ''
  }
  assertions.value.push(newAssertion)
  emitUpdate()
}

function removeAssertion(index: number) {
  assertions.value.splice(index, 1)
  emitUpdate()
}

function moveUp(index: number) {
  if (index <= 0) return
  const temp = assertions.value[index]
  assertions.value[index] = assertions.value[index - 1]
  assertions.value[index - 1] = temp
  emitUpdate()
}

function moveDown(index: number) {
  if (index >= assertions.value.length - 1) return
  const temp = assertions.value[index]
  assertions.value[index] = assertions.value[index + 1]
  assertions.value[index + 1] = temp
  emitUpdate()
}

function updateConfig(assertion: Assertion, config: Record<string, any>) {
  assertion.config = config
  emitUpdate()
}

function emitUpdate() {
  emit('update:modelValue', assertions.value.map((a, i) => ({ ...a, order: i })))
}
</script>

<style scoped>
.assertion-editor { width: 100%; }
.action-toolbar { margin-bottom: 12px; }
.empty-tip { color: #909399; font-size: 13px; text-align: center; padding: 20px; }
.empty-tip p { margin-top: 6px; }
.assertion-list { display: flex; flex-direction: column; gap: 8px; }
.assertion-item { background-color: #fafafa; border-radius: 6px; border: 1px solid #e5e4e7; overflow: hidden; transition: border-color 0.2s; }
.assertion-item:hover { border-color: #aa3bff; }
.assertion-disabled { opacity: 0.5; }
.assertion-header { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background-color: #f5f5f7; border-bottom: 1px solid #e5e4e7; }
.assertion-left { display: flex; align-items: center; gap: 8px; }
.assertion-order { width: 18px; height: 18px; border-radius: 50%; color: #fff; font-size: 11px; font-weight: 600; display: flex; align-items: center; justify-content: center; }
.order-status { background-color: #409eff; }
.order-content { background-color: #67c23a; }
.order-advanced { background-color: #e6a23c; }
.assertion-right { display: flex; align-items: center; gap: 2px; }
.assertion-config-area { padding: 12px; }
.dropdown-group-title { font-size: 12px; color: #909399; font-weight: 600; cursor: default !important; }
</style>
