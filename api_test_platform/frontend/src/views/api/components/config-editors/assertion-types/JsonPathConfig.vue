<template>
  <el-form label-width="100px" label-position="left" size="small">
    <el-form-item label="JSONPath">
      <el-input v-model="config.expression" placeholder="$.data.user.id" @input="emitUpdate" />
    </el-form-item>
    <el-form-item label="断言值">
      <el-switch v-model="config.assert_value" @change="emitUpdate" />
      <span class="hint">关闭则只验证路径存在</span>
    </el-form-item>
    <template v-if="config.assert_value">
      <el-form-item label="运算符">
        <el-select v-model="config.operator" @change="emitUpdate">
          <el-option label="等于" value="eq" />
          <el-option label="不等于" value="neq" />
          <el-option label="包含" value="contains" />
          <el-option label="不包含" value="not_contains" />
          <el-option label="大于" value="gt" />
          <el-option label="小于" value="lt" />
          <el-option label="大于等于" value="gte" />
          <el-option label="小于等于" value="lte" />
          <el-option label="为空" value="is_empty" />
          <el-option label="不为空" value="not_empty" />
          <el-option label="包含字段" value="has_key" />
          <el-option label="类型为" value="type_eq" />
          <el-option label="长度等于" value="length_eq" />
          <el-option label="长度大于" value="length_gt" />
          <el-option label="长度小于" value="length_lt" />
          <el-option label="匹配正则" value="matches" />
        </el-select>
      </el-form-item>
      <el-form-item label="期望值" v-if="!['is_empty', 'not_empty', 'has_key'].includes(config.operator)">
        <el-input v-model="config.expected" placeholder="期望值" @input="emitUpdate" />
      </el-form-item>
    </template>
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
  assert_value: true,
  operator: 'eq',
  expected: '',
  message: '',
  ...props.modelValue
})

watch(() => props.modelValue, (val) => {
  Object.assign(config, { expression: '', assert_value: true, operator: 'eq', expected: '', message: '', ...val })
}, { deep: true })

function emitUpdate() {
  emit('update:modelValue', { ...config })
}
</script>

<style scoped>
.hint { margin-left: 8px; color: #909399; font-size: 12px; }
</style>
