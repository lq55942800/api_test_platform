<template>
  <el-drawer
    v-model="visible"
    :title="isEdit ? '编辑接口' : '新建接口'"
    size="600px"
    :close-on-click-modal="false"
  >
    <div class="api-edit-form">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="接口名称" prop="name">
          <el-input v-model="form.name" placeholder="例如：获取用户列表" />
        </el-form-item>

        <el-form-item label="请求方法" prop="method">
          <el-select v-model="form.method" style="width: 120px">
            <el-option label="GET" value="GET" />
            <el-option label="POST" value="POST" />
            <el-option label="PUT" value="PUT" />
            <el-option label="DELETE" value="DELETE" />
            <el-option label="PATCH" value="PATCH" />
          </el-select>
        </el-form-item>

        <el-form-item label="路径" prop="path">
          <el-input v-model="form.path" placeholder="/api/users" />
        </el-form-item>

        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" rows="2" />
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="form.status">
            <el-option label="草稿" value="draft" />
            <el-option label="启用" value="enabled" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </el-form-item>

        <el-divider content-position="left">请求参数</el-divider>

        <el-tabs>
          <el-tab-pane label="Query参数">
            <KeyValueEditor v-model="queryParams" />
          </el-tab-pane>
          <el-tab-pane label="Header参数">
            <KeyValueEditor v-model="headerParams" />
          </el-tab-pane>
          <el-tab-pane label="Path参数">
            <KeyValueEditor v-model="pathParams" />
          </el-tab-pane>
        </el-tabs>

        <el-divider content-position="left">请求体</el-divider>

        <el-form-item label="Body类型">
          <el-select v-model="form.body_type">
            <el-option label="无" value="none" />
            <el-option label="JSON" value="json" />
            <el-option label="Form Data" value="form-data" />
            <el-option label="Raw" value="raw" />
          </el-select>
        </el-form-item>

        <el-form-item v-if="form.body_type !== 'none'" label="Body定义">
          <JsonEditor v-model="form.body_definition" />
        </el-form-item>

        <el-divider content-position="left">断言配置</el-divider>

        <el-form-item label="断言">
          <el-input
            v-model="form.assertions"
            type="textarea"
            rows="4"
            placeholder="JSON格式的断言配置"
          />
        </el-form-item>

        <el-divider content-position="left">超时配置</el-divider>

        <div class="timeout-config">
          <el-form-item label="连接超时">
            <el-input-number v-model="form.connect_timeout" :min="0" :step="1000" />
            <span class="timeout-unit">ms</span>
          </el-form-item>
          <el-form-item label="读取超时">
            <el-input-number v-model="form.read_timeout" :min="0" :step="1000" />
            <span class="timeout-unit">ms</span>
          </el-form-item>
        </div>
      </el-form>

      <div class="drawer-footer">
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSubmit">保存</el-button>
      </div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useApiStore } from '@/stores/api'
import type { ApiDefinition, HttpMethod } from '@/types'
import KeyValueEditor from '@/components/forms/KeyValueEditor.vue'
import JsonEditor from '@/components/forms/JsonEditor.vue'

interface KeyValueItem {
  key: string
  value: string
  description?: string
}

const props = defineProps<{
  modelValue: boolean
  api?: ApiDefinition | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

const store = useApiStore()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const isEdit = computed(() => !!props.api?.id)

const formRef = ref()
const saving = ref(false)

const form = ref({
  name: '',
  method: 'GET' as HttpMethod,
  path: '',
  description: '',
  status: 'draft' as const,
  body_type: 'none',
  body_definition: '',
  assertions: '',
  connect_timeout: 5000,
  read_timeout: 30000,
  write_timeout: 10000,
  pool_timeout: 5000,
})

const queryParams = ref<KeyValueItem[]>([])
const headerParams = ref<KeyValueItem[]>([])
const pathParams = ref<KeyValueItem[]>([])

const rules = {
  name: [{ required: true, message: '请输入接口名称', trigger: 'blur' }],
  method: [{ required: true, message: '请选择请求方法', trigger: 'change' }],
  path: [{ required: true, message: '请输入路径', trigger: 'blur' }],
}

watch(() => props.api, (api) => {
  if (api) {
    form.value = {
      name: api.name,
      method: api.method,
      path: api.path,
      description: api.description || '',
      status: api.status,
      body_type: (api.body_type as any) || 'none',
      body_definition: api.body_definition || '',
      assertions: api.assertions || '',
      connect_timeout: api.connect_timeout || 5000,
      read_timeout: api.read_timeout || 30000,
      write_timeout: api.write_timeout || 10000,
      pool_timeout: api.pool_timeout || 5000,
    }
    // Parse params from JSON strings
    if (api.query_params) {
      try {
        queryParams.value = JSON.parse(api.query_params)
      } catch { queryParams.value = [] }
    }
    if (api.header_params) {
      try {
        headerParams.value = JSON.parse(api.header_params)
      } catch { headerParams.value = [] }
    }
    if (api.path_params) {
      try {
        pathParams.value = JSON.parse(api.path_params)
      } catch { pathParams.value = [] }
    }
  } else {
    form.value = {
      name: '',
      method: 'GET',
      path: '',
      description: '',
      status: 'draft',
      body_type: 'none',
      body_definition: '',
      assertions: '',
      connect_timeout: 5000,
      read_timeout: 30000,
      write_timeout: 10000,
      pool_timeout: 5000,
    }
    queryParams.value = []
    headerParams.value = []
    pathParams.value = []
  }
}, { immediate: true })

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    saving.value = true

    const apiData = {
      ...form.value,
      query_params: JSON.stringify(queryParams.value),
      header_params: JSON.stringify(headerParams.value),
      path_params: JSON.stringify(pathParams.value),
    }

    if (isEdit.value) {
      await store.updateApi(props.api!.id!, apiData)
      ElMessage.success('更新成功')
    } else {
      await store.createApi(apiData)
      ElMessage.success('创建成功')
    }

    emit('success')
  } catch (e) {
    // Validation failed
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.api-edit-form {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.api-edit-form .el-form {
  flex: 1;
  overflow-y: auto;
  padding-right: var(--spacing-md);
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border);
  margin-top: var(--spacing-lg);
}

.timeout-config {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

.timeout-config .el-form-item {
  display: flex;
  align-items: center;
}

.timeout-unit {
  margin-left: var(--spacing-sm);
  color: var(--color-text-muted);
}
</style>