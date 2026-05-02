<template>
  <el-form label-width="100px" label-position="left" size="small">
    <el-form-item label="XPath表达式">
      <el-input v-model="config.expression" placeholder="/response/status" @input="emitUpdate" />
    </el-form-item>
    <el-form-item label="期望值">
      <el-input v-model="config.expected" placeholder="期望值（为空则只验证匹配到内容）" @input="emitUpdate" />
    </el-form-item>
    <el-form-item label="运算符" v-if="config.expected">
      <el-select v-model="config.operator" @change="emitUpdate">
        <el-option label="等于" value="equals" />
        <el-option label="不等于" value="not_equals" />
        <el-option label="包含" value="contains" />
        <el-option label="不包含" value="not_contains" />
        <el-option label="匹配正则" value="matches" />
      </el-select>
    </el-form-item>
    <el-form-item label="使用Tidy">
      <el-switch v-model="config.use_tidy" @change="emitUpdate" />
      <span class="hint">HTML响应使用Tidy解析</span>
    </el-form-item>
    <el-form-item label="使用命名空间">
      <el-switch v-model="config.use_namespaces" @change="emitUpdate" />
    </el-form-item>
    <el-form-item label="验证XML">
      <el-switch v-model="config.validate_xml" @change="emitUpdate" />
    </el-form-item>
    <el-form-item label="无匹配为真">
      <el-switch v-model="config.true_if_no_match" @change="emitUpdate" />
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
  expression: '',
  expected: '',
  operator: 'equals',
  use_tidy: false,
  use_namespaces: false,
  validate_xml: false,
  true_if_no_match: false,
  message: '',
  ...props.modelValue
})

watch(() => props.modelValue, (val) => {
  Object.assign(config, { expression: '', expected: '', operator: 'equals', use_tidy: false, use_namespaces: false, validate_xml: false, true_if_no_match: false, message: '', ...val })
}, { deep: true })

function emitUpdate() {
  emit('update:modelValue', { ...config })
}
</script>

<style scoped>
.hint {
  margin-left: 8px;
  color: #909399;
  font-size: 12px;
}
</style>
