<template>
  <el-form label-width="100px" label-position="left" size="small">
    <el-form-item label="Cookie策略">
      <el-select v-model="config.policy" @change="emitUpdate">
        <el-option label="标准" value="standard" />
        <el-option label="忽略Cookie" value="ignore_cookies" />
        <el-option label="仅自定义" value="custom_only" />
      </el-select>
    </el-form-item>
    <el-form-item label="每次迭代清除">
      <el-switch v-model="config.clear_each_iteration" @change="emitUpdate" />
    </el-form-item>
    <el-divider content-position="left">自定义Cookie</el-divider>
    <div class="cookie-list">
      <div v-for="(cookie, index) in config.custom_cookies" :key="index" class="cookie-item">
        <div class="cookie-row">
          <el-input v-model="cookie.name" size="small" placeholder="名称" style="width: 120px" @input="emitUpdate" />
          <el-input v-model="cookie.value" size="small" placeholder="值（支持变量引用）" style="width: 180px" @input="emitUpdate" />
          <el-button type="danger" link size="small" @click="removeCookie(index)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
        <div class="cookie-row" style="margin-top: 6px">
          <el-input v-model="cookie.domain" size="small" placeholder="域名" style="width: 140px" @input="emitUpdate" />
          <el-input v-model="cookie.path" size="small" placeholder="路径" style="width: 100px" @input="emitUpdate" />
          <el-checkbox v-model="cookie.secure" size="small" @change="emitUpdate">Secure</el-checkbox>
          <el-checkbox v-model="cookie.http_only" size="small" @change="emitUpdate">HttpOnly</el-checkbox>
        </div>
      </div>
      <el-button type="primary" link size="small" @click="addCookie">添加Cookie</el-button>
    </div>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import { Delete } from '@element-plus/icons-vue'

const props = defineProps<{
  modelValue: Record<string, any>
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, any>]
}>()

const config = reactive({
  policy: 'standard',
  clear_each_iteration: false,
  custom_cookies: [] as any[],
  ...props.modelValue
})

watch(() => props.modelValue, (val) => {
  Object.assign(config, {
    policy: 'standard', clear_each_iteration: false, custom_cookies: [], ...val
  })
}, { deep: true })

function addCookie() {
  if (!config.custom_cookies) config.custom_cookies = []
  config.custom_cookies.push({ name: '', value: '', domain: '', path: '/', secure: false, http_only: false })
  emitUpdate()
}

function removeCookie(index: number) {
  config.custom_cookies.splice(index, 1)
  emitUpdate()
}

function emitUpdate() {
  emit('update:modelValue', { ...config })
}
</script>

<style scoped>
.cookie-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 12px;
}

.cookie-item {
  padding: 8px;
  background-color: #fafafa;
  border-radius: 4px;
  border: 1px solid #e5e4e7;
}

.cookie-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
