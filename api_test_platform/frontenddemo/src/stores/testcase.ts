import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { testCaseApi } from '@/api/testcase'
import type { TestCase, TestCaseModule, ExecutionRecord } from '@/types'

export const useTestCaseStore = defineStore('testcase', () => {
  const testCases = ref<TestCase[]>([])
  const modules = ref<TestCaseModule[]>([])
  const currentTestCase = ref<TestCase | null>(null)
  const executionRecords = ref<ExecutionRecord[]>([])
  const loading = ref(false)
  const selectedModuleId = ref<number | null>(null)

  const filteredTestCases = computed(() => {
    if (selectedModuleId.value === null) {
      return testCases.value
    }
    return testCases.value.filter(tc => tc.module_id === selectedModuleId.value)
  })

  const fetchTestCases = async (params?: {
    team_id?: number
    module_id?: number
    status?: string
    keyword?: string
    priority?: string
  }) => {
    loading.value = true
    try {
      testCases.value = await testCaseApi.getTestCases(params)
    } finally {
      loading.value = false
    }
  }

  const fetchModules = async (teamId?: number) => {
    modules.value = await testCaseApi.getModules(teamId)
  }

  const createTestCase = async (data: Partial<TestCase>, teamId: number, userId: number) => {
    const created = await testCaseApi.createTestCase(data, teamId, userId)
    testCases.value.push(created)
    return created
  }

  const updateTestCase = async (id: number, data: Partial<TestCase>, userId: number) => {
    const updated = await testCaseApi.updateTestCase(id, data, userId)
    const index = testCases.value.findIndex(tc => tc.id === id)
    if (index !== -1) {
      testCases.value[index] = updated
    }
    return updated
  }

  const deleteTestCase = async (id: number) => {
    await testCaseApi.deleteTestCase(id)
    testCases.value = testCases.value.filter(tc => tc.id !== id)
  }

  const executeTestCase = async (id: number, data: {
    environment_id: number
    fail_strategy?: string
    save_record?: boolean
    timeout?: number
    step_interval?: number
  }) => {
    return await testCaseApi.executeTestCase(id, data)
  }

  const debugTestCase = async (id: number, data: {
    environment_id: number
    fail_strategy?: string
    save_record?: boolean
    timeout?: number
    step_interval?: number
  }) => {
    return await testCaseApi.debugTestCase(id, data)
  }

  const createModule = async (data: Partial<TestCaseModule>) => {
    const created = await testCaseApi.createModule(data)
    modules.value.push(created)
    return created
  }

  const deleteModule = async (id: number) => {
    await testCaseApi.deleteModule(id)
    modules.value = modules.value.filter(m => m.id !== id)
  }

  const fetchExecutionRecords = async (testCaseId: number, params?: {
    status?: string
    executor_id?: number
    page?: number
    page_size?: number
  }) => {
    const result = await testCaseApi.getExecutionRecords(testCaseId, params)
    executionRecords.value = result.items
    return result
  }

  return {
    testCases,
    modules,
    currentTestCase,
    executionRecords,
    loading,
    selectedModuleId,
    filteredTestCases,
    fetchTestCases,
    fetchModules,
    createTestCase,
    updateTestCase,
    deleteTestCase,
    executeTestCase,
    debugTestCase,
    createModule,
    deleteModule,
    fetchExecutionRecords,
  }
})