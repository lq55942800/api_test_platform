import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiManagementApi } from '@/api/api'
import type { ApiDefinition, ApiModule } from '@/types'

export const useApiStore = defineStore('api', () => {
  const apis = ref<ApiDefinition[]>([])
  const modules = ref<ApiModule[]>([])
  const currentApi = ref<ApiDefinition | null>(null)
  const loading = ref(false)
  const selectedModuleId = ref<number | null>(null)

  const filteredApis = computed(() => {
    if (selectedModuleId.value === null) {
      return apis.value
    }
    return apis.value.filter(api => api.module_id === selectedModuleId.value)
  })

  const fetchApis = async (params?: {
    team_id?: number
    module_id?: number
    status?: string
    keyword?: string
  }) => {
    loading.value = true
    try {
      apis.value = await apiManagementApi.getApis(params)
    } finally {
      loading.value = false
    }
  }

  const fetchModules = async (teamId?: number) => {
    modules.value = await apiManagementApi.getModules(teamId)
  }

  const createApi = async (data: Partial<ApiDefinition>) => {
    const created = await apiManagementApi.createApi(data)
    apis.value.push(created)
    return created
  }

  const updateApi = async (id: number, data: Partial<ApiDefinition>) => {
    const updated = await apiManagementApi.updateApi(id, data)
    const index = apis.value.findIndex(a => a.id === id)
    if (index !== -1) {
      apis.value[index] = updated
    }
    return updated
  }

  const deleteApi = async (id: number) => {
    await apiManagementApi.deleteApi(id)
    apis.value = apis.value.filter(a => a.id !== id)
  }

  const debugApi = async (id: number, data: {
    environment_id: number
    param_overrides?: Record<string, any>
    header_overrides?: Record<string, any>
    body_overrides?: any
  }) => {
    return await apiManagementApi.debugApi(id, data)
  }

  const createModule = async (data: Partial<ApiModule>) => {
    const created = await apiManagementApi.createModule(data)
    modules.value.push(created)
    return created
  }

  const deleteModule = async (id: number) => {
    await apiManagementApi.deleteModule(id)
    modules.value = modules.value.filter(m => m.id !== id)
  }

  return {
    apis,
    modules,
    currentApi,
    loading,
    selectedModuleId,
    filteredApis,
    fetchApis,
    fetchModules,
    createApi,
    updateApi,
    deleteApi,
    debugApi,
    createModule,
    deleteModule,
  }
})