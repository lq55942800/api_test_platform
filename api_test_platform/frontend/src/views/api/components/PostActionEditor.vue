<template>
  <div class="post-action-editor">
    <div class="action-toolbar">
      <el-dropdown trigger="click" @command="handleAdd">
        <el-button type="primary" link size="small">
          <el-icon style="margin-right: 4px"><Plus /></el-icon>添加后置操作
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item v-for="at in POST_ACTION_TYPES" :key="at.value" :command="at.value">
              {{ at.label }}
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <div v-if="actions.length === 0" class="empty-tip">
      <el-icon :size="28" color="#c0c4cc"><Document /></el-icon>
      <p>暂无后置操作</p>
    </div>

    <div v-else class="action-list">
      <div
        v-for="(action, index) in actions"
        :key="action.id"
        class="action-item"
        :class="{ 'action-disabled': !action.enabled }"
      >
        <div class="action-header">
          <div class="action-left">
            <span class="action-order">{{ index + 1 }}</span>
            <el-tag size="small" :type="getTypeTagType(action.type)" effect="plain">
              {{ getTypeLabel(action.type) }}
            </el-tag>
          </div>
          <div class="action-right">
            <el-switch v-model="action.enabled" size="small" @change="emitUpdate" />
            <el-button size="small" link @click="moveUp(index)" :disabled="index === 0">
              <el-icon><Top /></el-icon>
            </el-button>
            <el-button size="small" link @click="moveDown(index)" :disabled="index === actions.length - 1">
              <el-icon><Bottom /></el-icon>
            </el-button>
            <el-button type="danger" link size="small" @click="removeAction(index)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>

        <div class="action-config-area">
          <ExtractConfig
            v-if="action.type === 'extract'"
            :modelValue="action.config"
            @update:modelValue="(val: Record<string, any>) => updateConfig(action, val)"
          />
          <ScriptConfig
            v-else-if="action.type === 'script'"
            :modelValue="action.config"
            @update:modelValue="(val: Record<string, any>) => updateConfig(action, val)"
          />
          <DatabaseConfig
            v-else-if="action.type === 'database'"
            :modelValue="action.config"
            @update:modelValue="(val: Record<string, any>) => updateConfig(action, val)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Plus, Delete, Top, Bottom, Document } from '@element-plus/icons-vue'
import { POST_ACTION_TYPES } from '@/types/api'
import type { PostRequestAction, PostRequestActionType } from '@/types/api'
import ExtractConfig from './config-editors/ExtractConfig.vue'
import ScriptConfig from './config-editors/ScriptConfig.vue'
import DatabaseConfig from './config-editors/DatabaseConfig.vue'

const props = defineProps<{
  modelValue: PostRequestAction[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: PostRequestAction[]]
}>()

const actions = ref<PostRequestAction[]>([...(props.modelValue || [])])

watch(() => props.modelValue, (val) => {
  actions.value = [...(val || [])]
}, { deep: true })

function getTypeLabel(type: string): string {
  return POST_ACTION_TYPES.find(t => t.value === type)?.label || type
}

function getTypeTagType(type: string): string {
  const map: Record<string, string> = {
    extract: '',
    script: 'warning',
    database: 'danger'
  }
  return map[type] || ''
}

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

function getDefaultConfig(type: string): Record<string, any> {
  const defaults: Record<string, Record<string, any>> = {
    extract: { extractors: [] },
    script: { script: '', timeout: 10000 },
    database: { environment_id: undefined, service_id: undefined, query_type: 'select', sql: '', variable_mapping: [], on_error: 'abort', timeout: 30000 }
  }
  return { ...(defaults[type] || {}) }
}

function handleAdd(type: string) {
  const newAction: PostRequestAction = {
    id: generateId(),
    enabled: true,
    name: getTypeLabel(type),
    type: type as PostRequestActionType,
    phase: 'post_request',
    order: actions.value.length,
    config: getDefaultConfig(type),
    description: ''
  }
  actions.value.push(newAction)
  emitUpdate()
}

function removeAction(index: number) {
  actions.value.splice(index, 1)
  emitUpdate()
}

function moveUp(index: number) {
  if (index <= 0) return
  const temp = actions.value[index]
  actions.value[index] = actions.value[index - 1]
  actions.value[index - 1] = temp
  emitUpdate()
}

function moveDown(index: number) {
  if (index >= actions.value.length - 1) return
  const temp = actions.value[index]
  actions.value[index] = actions.value[index + 1]
  actions.value[index + 1] = temp
  emitUpdate()
}

function updateConfig(action: PostRequestAction, config: Record<string, any>) {
  action.config = config
  emitUpdate()
}

function emitUpdate() {
  emit('update:modelValue', actions.value.map((a, i) => ({ ...a, order: i })))
}
</script>

<style scoped>
.post-action-editor { width: 100%; }
.action-toolbar { margin-bottom: 12px; }
.empty-tip { color: #909399; font-size: 13px; text-align: center; padding: 20px; }
.empty-tip p { margin-top: 6px; }
.action-list { display: flex; flex-direction: column; gap: 8px; }
.action-item { background-color: #fafafa; border-radius: 6px; border: 1px solid #e5e4e7; overflow: hidden; transition: border-color 0.2s; }
.action-item:hover { border-color: #aa3bff; }
.action-disabled { opacity: 0.5; }
.action-header { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background-color: #f5f5f7; border-bottom: 1px solid #e5e4e7; }
.action-left { display: flex; align-items: center; gap: 8px; }
.action-order { width: 18px; height: 18px; border-radius: 50%; background-color: #67c23a; color: #fff; font-size: 11px; font-weight: 600; display: flex; align-items: center; justify-content: center; }
.action-right { display: flex; align-items: center; gap: 2px; }
.action-config-area { padding: 12px; }
</style>
