<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="导入变量"
    width="520px"
    :close-on-click-modal="false"
  >
    <el-input
      v-model="importText"
      type="textarea"
      :rows="12"
      placeholder="每行一个 key=value 格式&#10;# 开头为注释行&#10;&#10;示例：&#10;# 环境配置&#10;base_url=https://api.example.com&#10;timeout=30"
      class="code-textarea"
    />
    <div v-if="parseResult" class="parse-result">
      <div class="parse-info">
        解析到 <strong>{{ parseResult.variables.length }}</strong> 个变量
        <span v-if="parseResult.duplicates.length" class="warn-text">
          ，其中 {{ parseResult.duplicates.length }} 个变量名已存在将被覆盖
        </span>
      </div>
    </div>
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" @click="handleImport" :disabled="!importText.trim()">解析并导入</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { TestCaseVariable } from '@/types/testcase'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'import': [variables: TestCaseVariable[]]
}>()

const importText = ref('')
const parseResult = ref<{ variables: TestCaseVariable[]; duplicates: string[] } | null>(null)

watch(() => props.modelValue, (val) => {
  if (val) {
    importText.value = ''
    parseResult.value = null
  }
})

function parseImportText(): { variables: TestCaseVariable[]; duplicates: string[] } {
  const variables: TestCaseVariable[] = []
  const seen = new Set<string>()
  const lines = importText.value.split('\n')
  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed || trimmed.startsWith('#')) continue
    const eqIndex = trimmed.indexOf('=')
    if (eqIndex === -1) continue
    const key = trimmed.substring(0, eqIndex).trim()
    const value = trimmed.substring(eqIndex + 1).trim()
    if (!key) continue
    seen.add(key)
    variables.push({
      key,
      value,
      default_value: value,
      description: '',
      enabled: true
    })
  }
  return { variables, duplicates: [] }
}

async function handleImport() {
  const result = parseImportText()
  if (result.variables.length === 0) {
    ElMessage.warning('未解析到有效变量')
    return
  }
  parseResult.value = result
  if (result.duplicates.length > 0) {
    try {
      await ElMessageBox.confirm(
        `以下变量名已存在将被覆盖: ${result.duplicates.join(', ')}，是否继续？`,
        '覆盖确认',
        { type: 'warning' }
      )
    } catch {
      return
    }
  }
  emit('import', result.variables)
  emit('update:modelValue', false)
  ElMessage.success(`成功导入 ${result.variables.length} 个变量`)
}
</script>

<style scoped>
.code-textarea :deep(.el-textarea__inner) {
  font-family: ui-monospace, Consolas, monospace;
  font-size: 13px;
  line-height: 1.6;
}

.parse-result {
  margin-top: 12px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.parse-info {
  font-size: 13px;
  color: #606266;
}

.warn-text {
  color: #e6a23c;
  font-weight: 500;
}
</style>
