<template>
  <div class="database-config">
    <el-form label-width="80px" label-position="left" size="small">
      <el-form-item label="环境选择">
        <el-select
          v-model="config.environment_id"
          placeholder="选择环境"
          size="small"
          style="width: 100%"
          @change="onEnvironmentChange"
        >
          <el-option
            v-for="env in environments"
            :key="env.id"
            :label="env.name"
            :value="env.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="服务选择">
        <el-select
          v-model="config.service_id"
          placeholder="选择服务"
          size="small"
          style="width: 100%"
          @change="onServiceChange"
        >
          <el-option
            v-for="svc in currentServices"
            :key="svc.id"
            :label="svc.name"
            :value="svc.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="查询类型">
        <el-select v-model="config.query_type" size="small" @change="emitUpdate">
          <el-option label="SELECT" value="select" />
          <el-option label="INSERT" value="insert" />
          <el-option label="UPDATE" value="update" />
          <el-option label="DELETE" value="delete" />
        </el-select>
      </el-form-item>

      <el-form-item label="SQL语句">
        <el-input
          v-model="config.sql"
          type="textarea"
          :rows="4"
          placeholder="SELECT * FROM table WHERE id = ${id}"
          @input="emitUpdate"
          class="sql-textarea"
        />
      </el-form-item>

      <el-form-item v-if="config.query_type === 'select'" label="变量映射">
        <el-table :data="config.variable_mapping" size="small" border style="width: 100%">
          <el-table-column label="列名" min-width="100">
            <template #default="{ row }">
              <el-input v-model="row.column" placeholder="列名" size="small" @input="emitUpdate" />
            </template>
          </el-table-column>
          <el-table-column label="变量名" min-width="100">
            <template #default="{ row }">
              <el-input v-model="row.variable" placeholder="变量名" size="small" @input="emitUpdate" />
            </template>
          </el-table-column>
          <el-table-column label="作用域" width="100">
            <template #default="{ row }">
              <el-select v-model="row.scope" size="small" @change="emitUpdate">
                <el-option v-for="s in VARIABLE_SCOPES" :key="s.value" :label="s.label" :value="s.value" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="" width="50" align="center">
            <template #default="{ $index }">
              <el-button type="danger" link size="small" @click="removeMapping($index)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-button size="small" plain style="margin-top: 4px; width: 100%" @click="addMapping">
          <el-icon><Plus /></el-icon>添加映射
        </el-button>
      </el-form-item>

      <el-form-item label="错误处理">
        <el-select v-model="config.on_error" size="small" style="width: 120px" @change="emitUpdate">
          <el-option label="终止执行" value="abort" />
          <el-option label="跳过继续" value="skip" />
        </el-select>
      </el-form-item>

      <el-form-item label="超时(ms)">
        <el-input-number v-model="config.timeout" :min="1000" :max="120000" :step="1000" size="small" style="width: 140px" @change="emitUpdate" />
      </el-form-item>

      <div v-if="dbInfo" class="db-info">
        <el-tag size="small" type="info">{{ dbInfo.db_type }}</el-tag>
        <span class="db-host">{{ dbInfo.host }}:{{ dbInfo.port }}/{{ dbInfo.database }}</span>
      </div>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch, ref, computed, onMounted } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
import { VARIABLE_SCOPES } from '@/types/api'
import axios from 'axios'

const props = defineProps<{
  modelValue: Record<string, any>
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, any>]
}>()

const config = reactive({
  environment_id: undefined as number | undefined,
  service_id: undefined as number | undefined,
  query_type: 'select',
  sql: '',
  variable_mapping: [] as Array<{ column: string; variable: string; scope: string }>,
  on_error: 'abort',
  timeout: 30000,
  ...props.modelValue
})

const environments = ref<Array<any>>([])
const servicesMap = ref<Record<number, Array<any>>>({})

const currentServices = computed(() => {
  if (!config.environment_id) return []
  return servicesMap.value[config.environment_id] || []
})

const dbInfo = computed(() => {
  if (!config.service_id) return null
  for (const envId in servicesMap.value) {
    const svc = servicesMap.value[envId]?.find((s: any) => s.id === config.service_id)
    if (svc && svc.databases && svc.databases.length > 0) {
      return svc.databases[0]
    }
  }
  return null
})

watch(() => props.modelValue, (val) => {
  Object.assign(config, {
    environment_id: undefined, service_id: undefined,
    query_type: 'select', sql: '', variable_mapping: [],
    on_error: 'abort', timeout: 30000,
    ...val
  })
}, { deep: true })

onMounted(async () => {
  try {
    const resp = await axios.get('/api/v1/environments', { params: { page_size: 100 } })
    const data = resp.data
    environments.value = data.items || data || []
    for (const env of environments.value) {
      if (env.services && env.services.length > 0) {
        servicesMap.value[env.id] = env.services
      }
    }
  } catch (e) {
    console.error('Failed to load environments', e)
  }
})

function onEnvironmentChange() {
  config.service_id = undefined
  emitUpdate()
}

function onServiceChange() {
  emitUpdate()
}

function addMapping() {
  config.variable_mapping.push({ column: '', variable: '', scope: 'temp' })
  emitUpdate()
}

function removeMapping(index: number) {
  config.variable_mapping.splice(index, 1)
  emitUpdate()
}

function emitUpdate() {
  emit('update:modelValue', { ...config })
}
</script>

<style scoped>
.database-config { width: 100%; }
.db-info { display: flex; align-items: center; gap: 8px; margin-top: 8px; padding: 8px; background: #f5f7fa; border-radius: 4px; }
.db-host { color: #606266; font-size: 12px; }
.sql-textarea :deep(.el-textarea__inner) { font-family: ui-monospace, Consolas, monospace; font-size: 13px; }
</style>
