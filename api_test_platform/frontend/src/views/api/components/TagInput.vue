<template>
  <div class="tag-input">
    <el-tag
      v-for="tag in modelValue"
      :key="tag"
      closable
      :disable-transitions="false"
      size="small"
      @close="handleRemove(tag)"
      class="tag-item"
    >
      {{ tag }}
    </el-tag>
    <el-input
      v-if="inputVisible"
      ref="inputRef"
      v-model="inputValue"
      size="small"
      style="width: 100px"
      @keyup.enter="handleInputConfirm"
      @blur="handleInputConfirm"
    />
    <el-button
      v-else
      size="small"
      @click="showInput"
      :disabled="modelValue.length >= maxTags"
    >
      + 添加标签
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'

const props = withDefaults(defineProps<{
  modelValue: string[]
  maxTags?: number
}>(), {
  maxTags: 10
})

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

const inputVisible = ref(false)
const inputValue = ref('')
const inputRef = ref<any>()

function handleRemove(tag: string) {
  const newValue = props.modelValue.filter(t => t !== tag)
  emit('update:modelValue', newValue)
}

function showInput() {
  inputVisible.value = true
  nextTick(() => {
    inputRef.value?.focus()
  })
}

function handleInputConfirm() {
  const value = inputValue.value.trim()
  if (value && !props.modelValue.includes(value)) {
    emit('update:modelValue', [...props.modelValue, value])
  }
  inputVisible.value = false
  inputValue.value = ''
}
</script>

<style scoped>
.tag-input {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.tag-item {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
