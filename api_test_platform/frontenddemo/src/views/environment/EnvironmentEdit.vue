<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑环境' : '新建环境'"
    width="680px"
    :close-on-click-modal="false"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="环境名称" prop="name">
        <el-input v-model="form.name" placeholder="例如：测试环境" />
      </el-form-item>

      <el-form-item label="描述">
        <el-input v-model="form.description" type="textarea" rows="2" placeholder="环境描述" />
      </el-form-item>

      <el-form-item label="默认环境">
        <el-switch v-model="form.is_default" />
      </el-form-item>

      <el-divider>服务配置</el-divider>

      <div class="services-section">
        <div v-for="(service, sIndex) in form.services" :key="sIndex" class="service-item">
          <div class="service-header">
            <el-input v-model="service.name" placeholder="服务名称" style="width: 200px" />
            <el-select v-model="service.service_type" placeholder="服务类型" style="width: 140px">
              <el-option label="微服务" value="microservice" />
              <el-option label="模块" value="module" />
              <el-option label="第三方" value="third_party" />
            </el-select>
            <el-button type="danger" icon="Delete" plain circle @click="removeService(sIndex)" />
          </div>

          <div v-for="(server, srvIndex) in service.servers" :key="srvIndex" class="server-item">
            <el-input v-model="server.host" placeholder="服务器地址" style="flex: 1" />
            <el-input v-model="server.port" placeholder="端口" type="number" style="width: 100px" />
            <el-select v-model="server.protocol" style="width: 100px">
              <el-option label="http" value="http" />
              <el-option label="https" value="https" />
            </el-select>
            <el-input v-model="server.base_path" placeholder="base path" style="width: 120px" />
            <el-button type="danger" icon="Delete" plain circle @click="removeServer(sIndex, srvIndex)" />
          </div>

          <el-button size="small" plain @click="addServer(sIndex)">+ 添加服务器</el-button>
        </div>

        <el-button type="primary" plain @click="addService">+ 添加服务</el-button>
      </div>

      <el-divider>变量配置</el-divider>

      <KeyValueEditor v-model="form.variables" />

      <el-form-item label="是否激活">
        <el-switch v-model="form.is_active" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="handleSubmit">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useEnvironmentStore } from '@/stores/environment'
import type { Environment, EnvService, EnvServer, EnvVariable } from '@/types'
import KeyValueEditor from '@/components/forms/KeyValueEditor.vue'

const props = defineProps<{
  modelValue: boolean
  environment?: Environment | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

const store = useEnvironmentStore()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const isEdit = computed(() => !!props.environment?.id)

const formRef = ref()
const saving = ref(false)

const defaultService: EnvService = {
  name: '',
  service_type: 'microservice',
  servers: [],
}

const defaultServer: EnvServer = {
  name: '默认服务器',
  host: '',
  port: 80,
  protocol: 'http',
  base_path: '',
  is_default: true,
}

const defaultVariable: EnvVariable = {
  key: '',
  value: '',
  value_type: 'string',
}

const form = ref({
  name: '',
  description: '',
  is_default: false,
  is_active: true,
  services: [] as EnvService[],
  variables: [] as EnvVariable[],
})

const rules = {
  name: [{ required: true, message: '请输入环境名称', trigger: 'blur' }],
}

watch(() => props.environment, (env) => {
  if (env) {
    form.value = {
      name: env.name,
      description: env.description || '',
      is_default: env.is_default || false,
      is_active: env.is_active !== false,
      services: env.services ? [...env.services] : [],
      variables: env.variables ? [...env.variables] : [],
    }
  } else {
    form.value = {
      name: '',
      description: '',
      is_default: false,
      is_active: true,
      services: [],
      variables: [],
    }
  }
}, { immediate: true })

const addService = () => {
  form.value.services.push({ ...defaultService, servers: [{ ...defaultServer }] })
}

const removeService = (index: number) => {
  form.value.services.splice(index, 1)
}

const addServer = (serviceIndex: number) => {
  form.value.services[serviceIndex].servers?.push({ ...defaultServer })
}

const removeServer = (serviceIndex: number, serverIndex: number) => {
  form.value.services[serviceIndex].servers?.splice(serverIndex, 1)
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    saving.value = true

    if (isEdit.value) {
      await store.updateEnvironment(props.environment!.id!, form.value)
      ElMessage.success('更新成功')
    } else {
      await store.createEnvironment(form.value)
      ElMessage.success('创建成功')
    }

    emit('success')
  } catch (e) {
    // Validation failed or API error
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.services-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.service-item {
  padding: var(--spacing-md);
  background: var(--color-bg-hover);
  border-radius: var(--radius-lg);
}

.service-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.server-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--color-border-light);
}

.server-item:last-child {
  border-bottom: none;
}
</style>