<template>
  <div class="action-manager">
    <div class="action-toolbar">
      <el-dropdown trigger="click" @command="handleAdd" split-button type="primary" size="small" plain>
        <el-icon style="margin-right: 4px"><Plus /></el-icon>添加操作
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item disabled class="dropdown-group-title">前置操作</el-dropdown-item>
            <el-dropdown-item v-for="at in PRE_ACTION_TYPES" :key="at.value" :command="'pre:' + at.value">
              <el-icon style="margin-right: 4px"><component :is="getIcon(at.icon)" /></el-icon>
              {{ at.label }}
            </el-dropdown-item>
            <el-dropdown-item divided disabled class="dropdown-group-title">后置操作</el-dropdown-item>
            <el-dropdown-item v-for="at in POST_ACTION_TYPES" :key="at.value" :command="'post:' + at.value">
              <el-icon style="margin-right: 4px"><component :is="getIcon(at.icon)" /></el-icon>
              {{ at.label }}
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <div v-if="allActions.length === 0" class="empty-tip">
      <el-icon :size="28" color="#c0c4cc"><Document /></el-icon>
      <p>暂无操作，点击上方按钮添加</p>
    </div>

    <div v-else class="action-sections">
      <div v-if="preActions.length > 0" class="action-section">
        <div class="section-header">
          <el-tag size="small" type="primary" effect="dark">前置操作</el-tag>
          <span class="section-count">{{ preActions.length }} 项</span>
        </div>
        <div class="action-list">
          <div
            v-for="(action, index) in preActions"
            :key="action.id"
            class="action-item"
            :class="{ 'action-disabled': !action.enabled }"
          >
            <div class="action-header">
              <div class="action-left">
                <span class="action-order">{{ index + 1 }}</span>
                <el-tag size="small" :type="getPreTypeTagType(action.type)" effect="plain">
                  {{ getPreTypeLabel(action.type) }}
                </el-tag>
              </div>
              <div class="action-right">
                <el-switch v-model="action.enabled" size="small" @change="emitUpdate" />
                <el-button size="small" link @click="movePreUp(index)" :disabled="index === 0">
                  <el-icon><Top /></el-icon>
                </el-button>
                <el-button size="small" link @click="movePreDown(index)" :disabled="index === preActions.length - 1">
                  <el-icon><Bottom /></el-icon>
                </el-button>
                <el-button type="danger" link size="small" @click="removePreAction(index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
            <div class="action-config-area">
              <SetVariableConfig
                v-if="action.type === 'set_variable'"
                :modelValue="action.config"
                @update:modelValue="(val: Record<string, any>) => updatePreConfig(action, val)"
              />
              <WaitConfig
                v-else-if="action.type === 'wait'"
                :modelValue="action.config"
                @update:modelValue="(val: Record<string, any>) => updatePreConfig(action, val)"
              />
              <ScriptConfig
                v-else-if="action.type === 'script'"
                :modelValue="action.config"
                @update:modelValue="(val: Record<string, any>) => updatePreConfig(action, val)"
              />
              <DatabaseConfig
                v-else-if="action.type === 'database'"
                :modelValue="action.config"
                @update:modelValue="(val: Record<string, any>) => updatePreConfig(action, val)"
              />
            </div>
          </div>
        </div>
      </div>

      <div v-if="postActions.length > 0" class="action-section">
        <div class="section-header">
          <el-tag size="small" type="success" effect="dark">后置操作</el-tag>
          <span class="section-count">{{ postActions.length }} 项</span>
        </div>
        <div class="action-list">
          <div
            v-for="(action, index) in postActions"
            :key="action.id"
            class="action-item"
            :class="{ 'action-disabled': !action.enabled }"
          >
            <div class="action-header">
              <div class="action-left">
                <span class="action-order post-order">{{ index + 1 }}</span>
                <el-tag size="small" :type="getPostTypeTagType(action.type)" effect="plain">
                  {{ getPostTypeLabel(action.type) }}
                </el-tag>
              </div>
              <div class="action-right">
                <el-switch v-model="action.enabled" size="small" @change="emitUpdate" />
                <el-button size="small" link @click="movePostUp(index)" :disabled="index === 0">
                  <el-icon><Top /></el-icon>
                </el-button>
                <el-button size="small" link @click="movePostDown(index)" :disabled="index === postActions.length - 1">
                  <el-icon><Bottom /></el-icon>
                </el-button>
                <el-button type="danger" link size="small" @click="removePostAction(index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
            <div class="action-config-area">
              <ExtractConfig
                v-if="action.type === 'extract'"
                :modelValue="action.config"
                @update:modelValue="(val: Record<string, any>) => updatePostConfig(action, val)"
              />
              <ScriptConfig
                v-else-if="action.type === 'script'"
                :modelValue="action.config"
                @update:modelValue="(val: Record<string, any>) => updatePostConfig(action, val)"
              />
              <DatabaseConfig
                v-else-if="action.type === 'database'"
                :modelValue="action.config"
                @update:modelValue="(val: Record<string, any>) => updatePostConfig(action, val)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { Plus, Delete, Top, Bottom, Document, Coin, Timer, Download } from '@element-plus/icons-vue'
import { PRE_ACTION_TYPES, POST_ACTION_TYPES } from '@/types/api'
import type { PreRequestAction, PostRequestAction, PreRequestActionType, PostRequestActionType } from '@/types/api'
import SetVariableConfig from './config-editors/SetVariableConfig.vue'
import WaitConfig from './config-editors/WaitConfig.vue'
import ScriptConfig from './config-editors/ScriptConfig.vue'
import DatabaseConfig from './config-editors/DatabaseConfig.vue'
import ExtractConfig from './config-editors/ExtractConfig.vue'

const props = defineProps<{
  preActions: PreRequestAction[]
  postActions: PostRequestAction[]
}>()

const emit = defineEmits<{
  'update:preActions': [value: PreRequestAction[]]
  'update:postActions': [value: PostRequestAction[]]
}>()

const preActions = ref<PreRequestAction[]>([...(props.preActions || [])])
const postActions = ref<PostRequestAction[]>([...(props.postActions || [])])

const allActions = computed(() => [...preActions.value, ...postActions.value])

watch(() => props.preActions, (val) => {
  preActions.value = [...(val || [])]
}, { deep: true })

watch(() => props.postActions, (val) => {
  postActions.value = [...(val || [])]
}, { deep: true })

function getIcon(iconName: string) {
  const iconMap: Record<string, any> = {
    Coin, Timer, Document, Download
  }
  return iconMap[iconName] || Document
}

function getPreTypeLabel(type: string): string {
  return PRE_ACTION_TYPES.find(t => t.value === type)?.label || type
}

function getPostTypeLabel(type: string): string {
  return POST_ACTION_TYPES.find(t => t.value === type)?.label || type
}

function getPreTypeTagType(type: string): string {
  const map: Record<string, string> = {
    set_variable: '',
    wait: 'info',
    script: 'warning',
    database: 'danger'
  }
  return map[type] || ''
}

function getPostTypeTagType(type: string): string {
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

function getDefaultPreConfig(type: string): Record<string, any> {
  const defaults: Record<string, Record<string, any>> = {
    set_variable: { variables: [] },
    wait: { wait_type: 'fixed', duration: 1, unit: 's' },
    script: { script: '', timeout: 10000 },
    database: { environment_id: undefined, service_id: undefined, query_type: 'select', sql: '', variable_mapping: [], on_error: 'abort', timeout: 30000 }
  }
  return { ...(defaults[type] || {}) }
}

function getDefaultPostConfig(type: string): Record<string, any> {
  const defaults: Record<string, Record<string, any>> = {
    extract: { extractors: [] },
    script: { script: '', timeout: 10000 },
    database: { environment_id: undefined, service_id: undefined, query_type: 'select', sql: '', variable_mapping: [], on_error: 'abort', timeout: 30000 }
  }
  return { ...(defaults[type] || {}) }
}

function handleAdd(command: string) {
  const [phase, type] = command.split(':')
  if (phase === 'pre') {
    const newAction: PreRequestAction = {
      id: generateId(),
      enabled: true,
      name: getPreTypeLabel(type),
      type: type as PreRequestActionType,
      phase: 'pre_request',
      order: preActions.value.length,
      config: getDefaultPreConfig(type),
      description: ''
    }
    preActions.value.push(newAction)
  } else if (phase === 'post') {
    const newAction: PostRequestAction = {
      id: generateId(),
      enabled: true,
      name: getPostTypeLabel(type),
      type: type as PostRequestActionType,
      phase: 'post_request',
      order: postActions.value.length,
      config: getDefaultPostConfig(type),
      description: ''
    }
    postActions.value.push(newAction)
  }
  emitUpdate()
}

function removePreAction(index: number) {
  preActions.value.splice(index, 1)
  emitUpdate()
}

function removePostAction(index: number) {
  postActions.value.splice(index, 1)
  emitUpdate()
}

function movePreUp(index: number) {
  if (index <= 0) return
  const temp = preActions.value[index]
  preActions.value[index] = preActions.value[index - 1]
  preActions.value[index - 1] = temp
  emitUpdate()
}

function movePreDown(index: number) {
  if (index >= preActions.value.length - 1) return
  const temp = preActions.value[index]
  preActions.value[index] = preActions.value[index + 1]
  preActions.value[index + 1] = temp
  emitUpdate()
}

function movePostUp(index: number) {
  if (index <= 0) return
  const temp = postActions.value[index]
  postActions.value[index] = postActions.value[index - 1]
  postActions.value[index - 1] = temp
  emitUpdate()
}

function movePostDown(index: number) {
  if (index >= postActions.value.length - 1) return
  const temp = postActions.value[index]
  postActions.value[index] = postActions.value[index + 1]
  postActions.value[index + 1] = temp
  emitUpdate()
}

function updatePreConfig(action: PreRequestAction, config: Record<string, any>) {
  action.config = config
  emitUpdate()
}

function updatePostConfig(action: PostRequestAction, config: Record<string, any>) {
  action.config = config
  emitUpdate()
}

function emitUpdate() {
  emit('update:preActions', preActions.value.map((a, i) => ({ ...a, order: i })))
  emit('update:postActions', postActions.value.map((a, i) => ({ ...a, order: i })))
}
</script>

<style scoped>
.action-manager { width: 100%; }
.action-toolbar { margin-bottom: 12px; }
.empty-tip { color: #909399; font-size: 13px; text-align: center; padding: 20px; }
.empty-tip p { margin-top: 6px; }
.action-sections { display: flex; flex-direction: column; gap: 16px; }
.action-section { border: 1px solid #e5e4e7; border-radius: 8px; overflow: hidden; }
.section-header { display: flex; align-items: center; gap: 8px; padding: 8px 12px; background-color: #f5f7fa; border-bottom: 1px solid #e5e4e7; }
.section-count { font-size: 12px; color: #909399; }
.action-list { display: flex; flex-direction: column; gap: 0; }
.action-item { border-bottom: 1px solid #f0f0f0; transition: background-color 0.2s; }
.action-item:last-child { border-bottom: none; }
.action-disabled { opacity: 0.5; }
.action-header { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background-color: #f5f5f7; border-bottom: 1px solid #e5e4e7; }
.action-left { display: flex; align-items: center; gap: 8px; }
.action-order { width: 18px; height: 18px; border-radius: 50%; background-color: #409eff; color: #fff; font-size: 11px; font-weight: 600; display: flex; align-items: center; justify-content: center; }
.post-order { background-color: #67c23a; }
.action-right { display: flex; align-items: center; gap: 2px; }
.action-config-area { padding: 12px; }
.dropdown-group-title { font-size: 12px; color: #909399; font-weight: 600; cursor: default !important; }
</style>
