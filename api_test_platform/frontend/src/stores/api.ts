import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiApi, moduleApi, tagApi, recentApi } from '@/api/api'
import type {
  ApiDefinition,
  ApiDefinitionCreate,
  ApiDefinitionUpdate,
  ApiModule,
  ApiModuleCreate,
  ApiModuleUpdate,
  ApiTag,
  ApiTagCreate,
  ApiVersion,
  VersionDiff,
  DebugHistory,
  DebugRequest,
  DebugResult,
  PaginatedResponse
} from '@/types/api'

export const useApiStore = defineStore('api', () => {
  const apis = ref<ApiDefinition[]>([])
  const currentApi = ref<ApiDefinition | null>(null)
  const loading = ref(false)
  const total = ref(0)

  const filters = ref<{
    keyword?: string
    method?: string
    status?: string
    module_id?: number
    tag_id?: number
    owner_id?: number
  }>({})

  const pagination = ref({
    page: 1,
    page_size: 20
  })

  async function fetchApis(params?: {
    page?: number
    page_size?: number
    keyword?: string
    method?: string
    status?: string
    module_id?: number
    tag_id?: number
    owner_id?: number
  }) {
    loading.value = true
    try {
      const response: PaginatedResponse<ApiDefinition> = await apiApi.list({
        page: pagination.value.page,
        page_size: pagination.value.page_size,
        ...filters.value,
        ...params
      })
      apis.value = response.items
      total.value = response.total
    } finally {
      loading.value = false
    }
  }

  async function fetchApi(id: number) {
    loading.value = true
    try {
      currentApi.value = await apiApi.get(id)
      return currentApi.value
    } finally {
      loading.value = false
    }
  }

  async function createApi(data: ApiDefinitionCreate) {
    const api = await apiApi.create(data)
    return api
  }

  async function updateApi(id: number, data: ApiDefinitionUpdate) {
    const api = await apiApi.update(id, data)
    if (currentApi.value?.id === id) {
      currentApi.value = api
    }
    const index = apis.value.findIndex(a => a.id === id)
    if (index !== -1) {
      apis.value[index] = api
    }
    return api
  }

  async function deleteApi(id: number) {
    await apiApi.delete(id)
    apis.value = apis.value.filter(a => a.id !== id)
    if (currentApi.value?.id === id) {
      currentApi.value = null
    }
  }

  async function copyApi(id: number) {
    const api = await apiApi.copy(id)
    return api
  }

  async function updateApiStatus(id: number, status: string) {
    await apiApi.updateStatus(id, status)
    const index = apis.value.findIndex(a => a.id === id)
    if (index !== -1) {
      apis.value[index].status = status
    }
    if (currentApi.value?.id === id) {
      currentApi.value.status = status
    }
  }

  async function batchDeleteApis(api_ids: number[]) {
    return await apiApi.batchDelete(api_ids)
  }

  async function batchMoveApis(api_ids: number[], target_module_id: number) {
    return await apiApi.batchMove(api_ids, target_module_id)
  }

  async function batchUpdateStatus(api_ids: number[], status: string) {
    return await apiApi.batchUpdateStatus(api_ids, status)
  }

  function setFilters(newFilters: Partial<typeof filters.value>) {
    filters.value = { ...filters.value, ...newFilters }
  }

  function resetFilters() {
    filters.value = {}
  }

  function setPagination(page: number, pageSize: number) {
    pagination.value.page = page
    pagination.value.page_size = pageSize
  }

  function clearCurrentApi() {
    currentApi.value = null
  }

  return {
    apis,
    currentApi,
    loading,
    total,
    filters,
    pagination,
    fetchApis,
    fetchApi,
    createApi,
    updateApi,
    deleteApi,
    copyApi,
    updateApiStatus,
    batchDeleteApis,
    batchMoveApis,
    batchUpdateStatus,
    setFilters,
    resetFilters,
    setPagination,
    clearCurrentApi
  }
})

export const useModuleStore = defineStore('apiModule', () => {
  const modules = ref<ApiModule[]>([])
  const loading = ref(false)

  async function fetchModules() {
    loading.value = true
    try {
      modules.value = await moduleApi.list()
    } finally {
      loading.value = false
    }
  }

  async function createModule(data: ApiModuleCreate) {
    const module = await moduleApi.create(data)
    modules.value.push(module)
    return module
  }

  async function updateModule(id: number, data: ApiModuleUpdate) {
    const module = await moduleApi.update(id, data)
    const index = modules.value.findIndex(m => m.id === id)
    if (index !== -1) {
      modules.value[index] = module
    }
    return module
  }

  async function deleteModule(id: number) {
    await moduleApi.delete(id)
    modules.value = modules.value.filter(m => m.id !== id)
  }

  return {
    modules,
    loading,
    fetchModules,
    createModule,
    updateModule,
    deleteModule
  }
})

export const useTagStore = defineStore('apiTag', () => {
  const tags = ref<ApiTag[]>([])
  const loading = ref(false)

  async function fetchTags() {
    loading.value = true
    try {
      tags.value = await tagApi.list()
    } finally {
      loading.value = false
    }
  }

  async function createTag(data: ApiTagCreate) {
    const tag = await tagApi.create(data)
    tags.value.push(tag)
    return tag
  }

  async function deleteTag(id: number) {
    await tagApi.delete(id)
    tags.value = tags.value.filter(t => t.id !== id)
  }

  return {
    tags,
    loading,
    fetchTags,
    createTag,
    deleteTag
  }
})

export const useDebugStore = defineStore('apiDebug', () => {
  const debugVisible = ref(false)
  const debugApiId = ref<number | null>(null)
  const debugResult = ref<DebugResult | null>(null)
  const debugLoading = ref(false)
  const debugHistories = ref<DebugHistory[]>([])
  const environmentId = ref<number | null>(null)

  function openDebug(apiId: number) {
    debugApiId.value = apiId
    debugVisible.value = true
    debugResult.value = null
  }

  function closeDebug() {
    debugVisible.value = false
    debugApiId.value = null
    debugResult.value = null
  }

  async function executeDebug(apiId: number, data: DebugRequest) {
    debugLoading.value = true
    try {
      const result = await apiApi.debug(apiId, data)
      debugResult.value = result
      return result
    } finally {
      debugLoading.value = false
    }
  }

  async function fetchDebugHistories(apiId: number) {
    const response = await apiApi.listDebugHistories(apiId, { page: 1, page_size: 10 })
    debugHistories.value = response.items
  }

  return {
    debugVisible,
    debugApiId,
    debugResult,
    debugLoading,
    debugHistories,
    environmentId,
    openDebug,
    closeDebug,
    executeDebug,
    fetchDebugHistories
  }
})

export const useVersionStore = defineStore('apiVersion', () => {
  const versions = ref<ApiVersion[]>([])
  const versionDiff = ref<VersionDiff | null>(null)
  const loading = ref(false)

  async function fetchVersions(apiId: number) {
    loading.value = true
    try {
      const response = await apiApi.listVersions(apiId, { page: 1, page_size: 20 })
      versions.value = response.items
    } finally {
      loading.value = false
    }
  }

  async function compareVersions(apiId: number, v1: number, v2: number) {
    loading.value = true
    try {
      versionDiff.value = await apiApi.compareVersions(apiId, v1, v2)
    } finally {
      loading.value = false
    }
  }

  async function rollbackVersion(apiId: number, versionNumber: number) {
    const api = await apiApi.rollbackVersion(apiId, versionNumber)
    return api
  }

  function clearVersions() {
    versions.value = []
    versionDiff.value = null
  }

  return {
    versions,
    versionDiff,
    loading,
    fetchVersions,
    compareVersions,
    rollbackVersion,
    clearVersions
  }
})

export const useRecentStore = defineStore('apiRecent', () => {
  const recentVisits = ref<ApiDefinition[]>([])

  async function fetchRecentVisits() {
    recentVisits.value = await recentApi.list()
  }

  return {
    recentVisits,
    fetchRecentVisits
  }
})
