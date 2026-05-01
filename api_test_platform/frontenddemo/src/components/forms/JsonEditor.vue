<template>
  <div class="json-editor">
    <div class="editor-toolbar">
      <el-button-group>
        <el-button size="small" :type="isFormatted ? 'primary' : 'default'" @click="format">
          格式化
        </el-button>
        <el-button size="small" @click="compress">
          压缩
        </el-button>
      </el-button-group>
      <span v-if="error" class="editor-error">{{ error }}</span>
    </div>
    <el-input
      v-model="content"
      type="textarea"
      :rows="12"
      :class="{ 'has-error': error }"
      placeholder="输入 JSON 格式数据..."
      @blur="validate"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const content = ref(props.modelValue || '')
const error = ref('')

watch(() => props.modelValue, (val) => {
  content.value = val || ''
})

watch(content, (val) => {
  emit('update:modelValue', val)
})

const validate = () => {
  if (!content.value.trim()) {
    error.value = ''
    return
  }
  try {
    JSON.parse(content.value)
    error.value = ''
  } catch (e: any) {
    error.value = e.message
  }
}

const format = () => {
  try {
    const obj = JSON.parse(content.value)
    content.value = JSON.stringify(obj, null, 2)
    error.value = ''
  } catch (e: any) {
    error.value = e.message
  }
}

const compress = () => {
  try {
    const obj = JSON.parse(content.value)
    content.value = JSON.stringify(obj)
    error.value = ''
  } catch (e: any) {
    error.value = e.message
  }
}
</script>

<style scoped>
.json-editor {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.editor-toolbar {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.editor-error {
  font-size: 0.8125rem;
  color: var(--color-error);
}

.json-editor :deep(.el-textarea__inner) {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.875rem;
  line-height: 1.6;
}

.json-editor :deep(.has-error .el-textarea__inner) {
  border-color: var(--color-error);
}
</style>