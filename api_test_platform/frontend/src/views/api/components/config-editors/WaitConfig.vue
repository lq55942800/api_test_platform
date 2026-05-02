<template>
  <div class="wait-config">
    <el-form label-width="80px" label-position="left" size="small">
      <el-form-item label="等待类型">
        <el-radio-group v-model="config.wait_type" @change="emitUpdate">
          <el-radio value="fixed">固定等待</el-radio>
          <el-radio value="conditional">条件等待</el-radio>
        </el-radio-group>
      </el-form-item>

      <template v-if="config.wait_type === 'fixed'">
        <el-form-item label="等待时长">
          <el-input-number
            v-model="config.duration"
            :min="0.1"
            :max="300"
            :step="0.5"
            :precision="1"
            size="small"
            style="width: 140px"
            @change="emitUpdate"
          />
          <el-select v-model="config.unit" size="small" style="width: 80px; margin-left: 8px" @change="emitUpdate">
            <el-option label="秒" value="s" />
            <el-option label="毫秒" value="ms" />
          </el-select>
        </el-form-item>
      </template>

      <template v-else>
        <el-form-item label="最大等待">
          <el-input-number
            v-model="config.max_wait"
            :min="1"
            :max="300"
            :step="1"
            size="small"
            style="width: 140px"
            @change="emitUpdate"
          />
          <span style="margin-left: 8px; color: #909399; font-size: 12px">秒</span>
        </el-form-item>
        <el-form-item label="检查间隔">
          <el-input-number
            v-model="config.poll_interval"
            :min="100"
            :max="10000"
            :step="100"
            size="small"
            style="width: 140px"
            @change="emitUpdate"
          />
          <span style="margin-left: 8px; color: #909399; font-size: 12px">毫秒</span>
        </el-form-item>
        <el-form-item label="条件变量">
          <el-input v-model="config.condition.variable_name" placeholder="变量名" size="small" @input="emitUpdate" />
        </el-form-item>
        <el-form-item label="比较方式">
          <el-select v-model="config.condition.operator" size="small" style="width: 120px" @change="emitUpdate">
            <el-option label="等于" value="eq" />
            <el-option label="不等于" value="neq" />
            <el-option label="包含" value="contains" />
            <el-option label="大于" value="gt" />
            <el-option label="小于" value="lt" />
          </el-select>
        </el-form-item>
        <el-form-item label="期望值">
          <el-input v-model="config.condition.expected_value" placeholder="期望值" size="small" @input="emitUpdate" />
        </el-form-item>
      </template>

      <el-form-item label="错误处理">
        <el-select v-model="config.on_error" size="small" style="width: 120px" @change="emitUpdate">
          <el-option label="终止执行" value="abort" />
          <el-option label="跳过继续" value="skip" />
        </el-select>
      </el-form-item>
    </el-form>
  </div>
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
  wait_type: 'fixed',
  duration: 1,
  unit: 's',
  max_wait: 30,
  poll_interval: 1000,
  condition: {
    variable_name: '',
    operator: 'eq',
    expected_value: ''
  },
  on_error: 'abort',
  ...props.modelValue
})

watch(() => props.modelValue, (val) => {
  Object.assign(config, {
    wait_type: 'fixed', duration: 1, unit: 's',
    max_wait: 30, poll_interval: 1000,
    condition: { variable_name: '', operator: 'eq', expected_value: '' },
    on_error: 'abort',
    ...val
  })
}, { deep: true })

function emitUpdate() {
  emit('update:modelValue', { ...config })
}
</script>

<style scoped>
.wait-config {
  width: 100%;
}
</style>
