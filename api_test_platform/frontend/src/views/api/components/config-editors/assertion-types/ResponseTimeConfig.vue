<template>
  <el-form label-width="100px" label-position="left" size="small">
    <el-form-item label="比较方式">
      <el-select v-model="config.operator" @change="onOperatorChange">
        <el-option label="小于" value="lt" />
        <el-option label="在范围内" value="between" />
      </el-select>
    </el-form-item>
    <el-form-item v-if="config.operator === 'between'" label="时间范围(ms)">
      <div style="display: flex; align-items: center; gap: 8px;">
        <el-input-number v-model="config.expected_min" :min="0" placeholder="最小值" @change="emitUpdate" />
        <span>-</span>
        <el-input-number v-model="config.expected_max" :min="0" placeholder="最大值" @change="emitUpdate" />
        <span>ms</span>
      </div>
    </el-form-item>
    <el-form-item v-else label="期望时间(ms)">
      <div style="display: flex; align-items: center; gap: 8px;">
        <el-input-number v-model="config.expected" :min="0" @change="emitUpdate" />
        <span>ms</span>
      </div>
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
  operator: 'lt',
  expected: 1000,
  expected_min: 0,
  expected_max: 3000,
  message: '',
  severity: 'warning',
  ...props.modelValue
})

watch(() => props.modelValue, (val) => {
  Object.assign(config, { operator: 'lt', expected: 1000, expected_min: 0, expected_max: 3000, message: '', severity: 'warning', ...val })
}, { deep: true })

function onOperatorChange() {
  emitUpdate()
}

function emitUpdate() {
  emit('update:modelValue', { ...config })
}
</script>
