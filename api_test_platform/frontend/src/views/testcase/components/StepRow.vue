<template>
  <div class="step-row" :class="{ 'step-row--disabled': !step.enabled }">
    <div class="step-row__main">
      <div class="step-row__left">
        <svg viewBox="0 0 10 16" width="10" height="16" class="step-drag-handle">
          <circle cx="2" cy="2" r="1.5" fill="currentColor"/>
          <circle cx="8" cy="2" r="1.5" fill="currentColor"/>
          <circle cx="2" cy="8" r="1.5" fill="currentColor"/>
          <circle cx="8" cy="8" r="1.5" fill="currentColor"/>
          <circle cx="2" cy="14" r="1.5" fill="currentColor"/>
          <circle cx="8" cy="14" r="1.5" fill="currentColor"/>
        </svg>
        <span class="step-row__index">{{ stepIndex }}</span>

        <template v-if="step.step_type === 'api'">
          <MethodTag v-if="apiMethod" :method="apiMethod" />
          <span v-if="apiPath" class="step-row__path">{{ apiPath }}</span>
          <span class="step-row__name">{{ step.step_name || '未命名步骤' }}</span>
        </template>

        <template v-else>
          <el-tag
            size="small"
            :style="conditionTagStyle"
            effect="light"
            round
          >
            {{ conditionLabel }}
          </el-tag>
          <span class="step-row__condition-desc">{{ conditionDesc }}</span>
        </template>
      </div>

      <div class="step-row__right">
        <el-button type="primary" link size="small" @click="$emit('edit', step)">
          <el-icon><Edit /></el-icon>
        </el-button>
        <el-button type="primary" link size="small" @click="$emit('copy', step)">
          <el-icon><CopyDocument /></el-icon>
        </el-button>
        <el-button type="danger" link size="small" @click="$emit('delete', step)">
          <el-icon><Delete /></el-icon>
        </el-button>
        <el-switch
          :model-value="step.enabled"
          size="small"
          @change="$emit('toggle-enabled', step, $event)"
        />
      </div>
    </div>

    <template v-if="step.step_type !== 'api'">
      <div class="step-children-line" :style="{ '--condition-color': conditionColor }">
        <StepRow
          v-for="(child, cIdx) in step.children"
          :key="child.id || cIdx"
          :step="child"
          :step-index="`${stepIndex}.${cIdx + 1}`"
          :depth="depth + 1"
          :max-depth="maxDepth"
          :api-list="apiList"
          @edit="$emit('edit', $event)"
          @copy="$emit('copy', $event)"
          @delete="$emit('delete', $event)"
          @toggle-enabled="(s: any, e: boolean) => $emit('toggle-enabled', s, e)"
          @add-child="(s: any, t: string) => $emit('add-child', s, t)"
        />
        <div class="step-add-child">
          <el-dropdown trigger="click" @command="(cmd: string) => $emit('add-child', step, cmd)">
            <el-button size="small" type="primary" link>
              <el-icon><Plus /></el-icon> 添加子步骤
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="api">API步骤</el-dropdown-item>
                <el-dropdown-item command="if" :disabled="depth >= maxDepth">IF条件</el-dropdown-item>
                <el-dropdown-item command="for" :disabled="depth >= maxDepth">FOR循环</el-dropdown-item>
                <el-dropdown-item command="while" :disabled="depth >= maxDepth">WHILE循环</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Edit, Delete, CopyDocument, Plus } from '@element-plus/icons-vue'
import MethodTag from '@/views/api/components/MethodTag.vue'
import type { TestCaseStep } from '@/types/testcase'

const props = withDefaults(defineProps<{
  step: TestCaseStep
  stepIndex: string
  depth: number
  maxDepth: number
  apiList: Array<any>
}>(), {
  depth: 0,
  maxDepth: 3,
  apiList: () => []
})

defineEmits<{
  edit: [step: TestCaseStep]
  copy: [step: TestCaseStep]
  delete: [step: TestCaseStep]
  'toggle-enabled': [step: TestCaseStep, enabled: boolean]
  'add-child': [parentStep: TestCaseStep, stepType: string]
}>()

const CONDITION_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  if: { bg: '#fdf6ec', text: '#e6a23c', border: '#faecd8' },
  for: { bg: '#ecf5ff', text: '#409eff', border: '#d9ecff' },
  while: { bg: '#f0f9eb', text: '#67c23a', border: '#e1f3d8' }
}

const apiInfo = computed(() => {
  if (props.step.step_type !== 'api' || !props.step.api_id) return null
  return props.apiList.find((a: any) => a.id === props.step.api_id) || null
})

const apiMethod = computed(() => apiInfo.value?.method?.toUpperCase() || '')

const apiPath = computed(() => apiInfo.value?.path || '')

const conditionLabel = computed(() => {
  const type = props.step.step_type
  if (type === 'if') return 'IF'
  if (type === 'for') return 'FOR'
  if (type === 'while') return 'WHILE'
  return type.toUpperCase()
})

const conditionColor = computed(() => {
  const colors = CONDITION_COLORS[props.step.step_type]
  return colors?.text || '#909399'
})

const conditionTagStyle = computed(() => {
  const colors = CONDITION_COLORS[props.step.step_type]
  if (!colors) return {}
  return {
    backgroundColor: colors.bg,
    color: colors.text,
    borderColor: colors.border,
    fontWeight: 600,
    fontFamily: 'ui-monospace, Consolas, monospace',
    fontSize: '12px',
    minWidth: '48px',
    textAlign: 'center'
  }
})

const conditionDesc = computed(() => {
  const cond = props.step.execution_condition
  if (!cond) return props.step.step_name || ''
  if (props.step.step_type === 'if') return cond.expression || cond.description || props.step.step_name || ''
  if (props.step.step_type === 'for') {
    const parts: string[] = []
    if (cond.loop_variable) parts.push(cond.loop_variable)
    if (cond.loop_count) parts.push(`x${cond.loop_count}`)
    return parts.join(' ') || cond.description || props.step.step_name || ''
  }
  if (props.step.step_type === 'while') return cond.expression || cond.description || props.step.step_name || ''
  return props.step.step_name || ''
})
</script>

<style scoped>
.step-row {
  margin-bottom: 4px;
}

.step-row--disabled {
  opacity: 0.5;
}

.step-row__main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #ffffff;
  border: 1px solid #e5e4e7;
  border-radius: 6px;
  transition: border-color 0.2s;
}

.step-row__main:hover {
  border-color: #aa3bff;
  box-shadow: 0 2px 8px rgba(170, 59, 255, 0.08);
}

.step-row__left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.step-drag-handle {
  cursor: grab;
  color: #c0c4cc;
  flex-shrink: 0;
  transition: color 0.2s;
}

.step-drag-handle:hover {
  color: #909399;
}

.step-drag-handle:active {
  cursor: grabbing;
}

.step-row__index {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #aa3bff;
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.step-row__path {
  font-family: ui-monospace, Consolas, monospace;
  font-size: 12px;
  color: #6b6375;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}

.step-row__name {
  font-size: 13px;
  font-weight: 500;
  color: #08060d;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 240px;
}

.step-row__condition-desc {
  font-size: 13px;
  color: #6b6375;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 300px;
}

.step-row__right {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.step-children-line {
  border-left: 2px solid var(--condition-color, #e6a23c);
  margin-left: 20px;
  padding-left: 20px;
  margin-top: 4px;
}

.step-add-child {
  padding: 4px 0;
}
</style>
