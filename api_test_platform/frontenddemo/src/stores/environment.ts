import { defineStore } from 'pinia'
import { ref } from 'vue'
import { environmentApi } from '@/api/environment'
import type { Environment } from '@/types'

export const useEnvironmentStore = defineStore('environment', () => {
  const environments = ref<Environment[]>([])
  const currentEnvironment = ref<Environment | null>(null)
  const loading = ref(false)

  const fetchEnvironments = async (teamId?: number) => {
    loading.value = true
    try {
      environments.value = await environmentApi.getEnvironments(teamId)
    } finally {
      loading.value = false
    }
  }

  const createEnvironment = async (data: Partial<Environment>) => {
    const created = await environmentApi.createEnvironment(data)
    environments.value.push(created)
    return created
  }

  const updateEnvironment = async (id: number, data: Partial<Environment>) => {
    const updated = await environmentApi.updateEnvironment(id, data)
    const index = environments.value.findIndex(e => e.id === id)
    if (index !== -1) {
      environments.value[index] = updated
    }
    return updated
  }

  const deleteEnvironment = async (id: number) => {
    await environmentApi.deleteEnvironment(id)
    environments.value = environments.value.filter(e => e.id !== id)
  }

  return {
    environments,
    currentEnvironment,
    loading,
    fetchEnvironments,
    createEnvironment,
    updateEnvironment,
    deleteEnvironment,
  }
})