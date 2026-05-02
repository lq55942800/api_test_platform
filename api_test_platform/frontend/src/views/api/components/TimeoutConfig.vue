<template>
  <div class="timeout-config">
    <el-form label-width="120px" label-position="left" size="small">
      <el-form-item label="启用自定义超时">
        <el-switch v-model="config.timeout_enabled" @change="emitUpdate" />
      </el-form-item>

      <template v-if="config.timeout_enabled">
        <div class="timeout-grid">
          <el-form-item label="连接超时(ms)">
            <el-input-number v-model="config.connect_timeout" :min="1" :max="60000" :step="500" @change="emitUpdate" />
          </el-form-item>
          <el-form-item label="读取超时(ms)">
            <el-input-number v-model="config.read_timeout" :min="1" :max="300000" :step="1000" @change="emitUpdate" />
          </el-form-item>
          <el-form-item label="发送超时(ms)">
            <el-input-number v-model="config.write_timeout" :min="1" :max="60000" :step="1000" @change="emitUpdate" />
          </el-form-item>
          <el-form-item label="连接池超时(ms)">
            <el-input-number v-model="config.pool_timeout" :min="1" :max="30000" :step="500" @change="emitUpdate" />
          </el-form-item>
          <el-form-item label="全局超时(ms)">
            <el-input-number v-model="config.sample_timeout" :min="1" :max="600000" :step="5000" @change="emitUpdate" />
          </el-form-item>
          <el-form-item label="SQL超时(ms)">
            <el-input-number v-model="config.sql_timeout" :min="1" :max="300000" :step="1000" @change="emitUpdate" />
          </el-form-item>
          <el-form-item label="脚本超时(ms)">
            <el-input-number v-model="config.script_timeout" :min="1" :max="120000" :step="1000" @change="emitUpdate" />
          </el-form-item>
        </div>

        <el-divider content-position="left">预设模板</el-divider>
        <div class="preset-buttons">
          <el-button
            v-for="preset in TIMEOUT_PRESETS"
            :key="preset.label"
            size="small"
            :type="isCurrentPreset(preset) ? 'primary' : 'default'"
            @click="applyPreset(preset)"
          >
            {{ preset.label }}
          </el-button>
        </div>
      </template>

      <template v-else>
        <div class="disabled-tip">使用环境/项目/系统默认超时配置</div>
      </template>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import { TIMEOUT_PRESETS, type TimeoutConfig } from '@/types/api'

const props = defineProps<{
  modelValue: Partial<TimeoutConfig> & Record<string, any>
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Partial<TimeoutConfig> & Record<string, any>]
}>()

const config = reactive({
  connect_timeout: 5000,
  read_timeout: 30000,
  write_timeout: 10000,
  pool_timeout: 5000,
  sample_timeout: 60000,
  sql_timeout: 30000,
  script_timeout: 10000,
  timeout_enabled: true,
  ...props.modelValue
})

watch(() => props.modelValue, (val) => {
  Object.assign(config, {
    connect_timeout: 5000, read_timeout: 30000, write_timeout: 10000, pool_timeout: 5000,
    sample_timeout: 60000, sql_timeout: 30000, script_timeout: 10000, timeout_enabled: true, ...val
  })
}, { deep: true })

function applyPreset(preset: typeof TIMEOUT_PRESETS[number]) {
  config.connect_timeout = preset.connect_timeout
  config.read_timeout = preset.read_timeout
  config.write_timeout = preset.write_timeout
  config.pool_timeout = preset.pool_timeout
  config.sample_timeout = preset.sample_timeout
  config.sql_timeout = preset.sql_timeout
  config.script_timeout = preset.script_timeout
  emitUpdate()
}

function isCurrentPreset(preset: typeof TIMEOUT_PRESETS[number]): boolean {
  return (
    config.connect_timeout === preset.connect_timeout &&
    config.read_timeout === preset.read_timeout &&
    config.write_timeout === preset.write_timeout &&
    config.pool_timeout === preset.pool_timeout &&
    config.sample_timeout === preset.sample_timeout &&
    config.sql_timeout === preset.sql_timeout &&
    config.script_timeout === preset.script_timeout
  )
}

function emitUpdate() {
  emit('update:modelValue', { ...config })
}
</script>

<style scoped>
.timeout-config {
  width: 100%;
}

.timeout-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 24px;
}

.preset-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.disabled-tip {
  color: #909399;
  font-size: 13px;
  padding: 12px;
  background-color: #f9fafb;
  border-radius: 4px;
}
</style>
