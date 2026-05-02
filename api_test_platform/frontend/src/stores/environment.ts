import { defineStore } from 'pinia'
import { ref } from 'vue'
import { environmentApi } from '@/api/environment'
import type {
  Environment,
  EnvironmentCreate,
  EnvironmentUpdate,
  Service,
  ServiceCreate,
  ServiceUpdate,
  EnvVariable,
  EnvVariableCreate,
  EnvVariableUpdate,
  PaginatedResponse
} from '@/types/environment'

/**
 * 环境管理Store
 */
export const useEnvironmentStore = defineStore('environment', () => {
  // 状态
  const environments = ref<Environment[]>([])
  const currentEnvironment = ref<Environment | null>(null)
  const services = ref<Service[]>([])
  const variables = ref<EnvVariable[]>([])
  const loading = ref(false)
  const total = ref(0)
  const serviceTotal = ref(0)

  /**
   * 获取环境列表
   */
  async function fetchEnvironments(params?: {
    page?: number
    page_size?: number
    search?: string
    is_default?: boolean
  }) {
    loading.value = true
    try {
      const response: PaginatedResponse<Environment> = await environmentApi.list({
        page: 1,
        page_size: 100,
        ...params
      })
      environments.value = response.items
      total.value = response.total
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取环境详情
   */
  async function fetchEnvironment(id: number) {
    loading.value = true
    try {
      currentEnvironment.value = await environmentApi.get(id)
      variables.value = currentEnvironment.value.variables || []
      return currentEnvironment.value
    } finally {
      loading.value = false
    }
  }

  /**
   * 创建环境
   */
  async function createEnvironment(data: EnvironmentCreate) {
    const env = await environmentApi.create(data)
    environments.value.push(env)
    return env
  }

  /**
   * 更新环境
   */
  async function updateEnvironment(id: number, data: EnvironmentUpdate) {
    const env = await environmentApi.update(id, data)
    const index = environments.value.findIndex(e => e.id === id)
    if (index !== -1) {
      environments.value[index] = env
    }
    if (currentEnvironment.value?.id === id) {
      currentEnvironment.value = env
    }
    return env
  }

  /**
   * 删除环境
   */
  async function deleteEnvironment(id: number) {
    await environmentApi.delete(id)
    environments.value = environments.value.filter(e => e.id !== id)
    if (currentEnvironment.value?.id === id) {
      currentEnvironment.value = null
      services.value = []
      variables.value = []
    }
  }

  /**
   * 复制环境
   */
  async function copyEnvironment(id: number) {
    const env = await environmentApi.copy(id)
    environments.value.push(env)
    return env
  }

  /**
   * 设置默认环境
   */
  async function setDefaultEnvironment(id: number) {
    const env = await environmentApi.setDefault(id)
    environments.value.forEach(e => {
      e.is_default = e.id === id
    })
    if (currentEnvironment.value) {
      currentEnvironment.value.is_default = currentEnvironment.value.id === id
    }
    return env
  }

  /**
   * 获取服务列表
   */
  async function fetchServices(envId: number, params?: {
    page?: number
    page_size?: number
    search?: string
  }) {
    loading.value = true
    try {
      const response: PaginatedResponse<Service> = await environmentApi.listServices(envId, {
        page: 1,
        page_size: 10,
        ...params
      })
      services.value = response.items
      serviceTotal.value = response.total
    } finally {
      loading.value = false
    }
  }

  /**
   * 创建服务
   */
  async function createService(envId: number, data: ServiceCreate) {
    const service = await environmentApi.createService(envId, data)
    return service
  }

  /**
   * 更新服务
   */
  async function updateService(serviceId: number, data: ServiceUpdate) {
    const service = await environmentApi.updateService(serviceId, data)
    const index = services.value.findIndex(s => s.id === serviceId)
    if (index !== -1) {
      services.value[index] = service
    }
    return service
  }

  /**
   * 删除服务
   */
  async function deleteService(serviceId: number) {
    await environmentApi.deleteService(serviceId)
  }

  /**
   * 复制服务
   */
  async function copyService(serviceId: number) {
    const service = await environmentApi.copyService(serviceId)
    return service
  }

  /**
   * 获取环境变量列表
   */
  async function fetchVariables(envId: number) {
    loading.value = true
    try {
      variables.value = await environmentApi.listVariables(envId)
    } finally {
      loading.value = false
    }
  }

  /**
   * 创建环境变量
   */
  async function createVariable(envId: number, data: EnvVariableCreate) {
    const variable = await environmentApi.createVariable(envId, data)
    variables.value.push(variable)
    return variable
  }

  /**
   * 更新环境变量
   */
  async function updateVariable(variableId: number, data: EnvVariableUpdate) {
    const variable = await environmentApi.updateVariable(variableId, data)
    const index = variables.value.findIndex(v => v.id === variableId)
    if (index !== -1) {
      variables.value[index] = variable
    }
    return variable
  }

  /**
   * 删除环境变量
   */
  async function deleteVariable(variableId: number) {
    await environmentApi.deleteVariable(variableId)
    variables.value = variables.value.filter(v => v.id !== variableId)
  }

  /**
   * 清空当前环境
   */
  function clearCurrentEnvironment() {
    currentEnvironment.value = null
    services.value = []
    variables.value = []
  }

  return {
    // 状态
    environments,
    currentEnvironment,
    services,
    variables,
    loading,
    total,
    serviceTotal,
    
    // Actions
    fetchEnvironments,
    fetchEnvironment,
    createEnvironment,
    updateEnvironment,
    deleteEnvironment,
    copyEnvironment,
    setDefaultEnvironment,
    fetchServices,
    createService,
    updateService,
    deleteService,
    copyService,
    fetchVariables,
    createVariable,
    updateVariable,
    deleteVariable,
    clearCurrentEnvironment
  }
})
