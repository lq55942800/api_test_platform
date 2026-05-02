<template>
  <el-form label-width="100px" label-position="left" size="small">
    <el-form-item label="检查来源">
      <el-select v-model="config.source" @change="emitUpdate">
        <el-option label="响应体" value="body" />
        <el-option label="响应头" value="header" />
        <el-option label="状态码" value="status_code" />
        <el-option label="URL" value="url" />
      </el-select>
    </el-form-item>
    <el-form-item label="正则表达式">
      <el-input v-model="config.pattern" placeholder="正则表达式" @input="emitUpdate" />
    </el-form-item>
    <el-form-item label="匹配规则">
      <el-select v-model="config.match_rule" @change="emitUpdate">
        <el-option label="包含" value="contains" />
        <el-option label="完全匹配" value="matches" />
        <el-option label="不包含" value="not_contains" />
        <el-option label="不匹配" value="not_matches" />
      </el-select>
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
  source: 'body',
  pattern: '',
  match_rule: 'contains',
  message: '',
  ...props.modelValue
})

watch(() => props.modelValue, (val) => {
  Object.assign(config, { source: 'body', pattern: '', match_rule: 'contains', message: '', ...val })
}, { deep: true })

function emitUpdate() {
  emit('update:modelValue', { ...config })
}
</script>
