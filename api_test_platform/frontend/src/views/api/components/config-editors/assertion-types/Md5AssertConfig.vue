<template>
  <el-form label-width="100px" label-position="left" size="small">
    <el-form-item label="期望MD5">
      <el-input v-model="config.expected_md5" placeholder="期望的MD5哈希值" @input="emitUpdate" />
    </el-form-item>
    <el-form-item label="自定义消息">
      <el-input v-model="config.message" placeholder="断言失败时的自定义消息" @input="emitUpdate" />
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'

const props = defineProps<{
  modelValue: Record<string, any>
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, any>]
}>()

const config = reactive({
  expected_md5: '',
  message: '',
  ...props.modelValue
})

watch(() => props.modelValue, (val) => {
  Object.assign(config, { expected_md5: '', message: '', ...val })
}, { deep: true })

function emitUpdate() {
  emit('update:modelValue', { ...config })
}
</script>
