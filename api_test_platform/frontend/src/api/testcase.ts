import client from './client'
import type { TestCase, TestCaseModule, ExecutionRecord } from '@/types'

export const testCaseApi = {
  getTestCases: (params?: {
    team_id?: number
    module_id?: number
    status?: string
    keyword?: string
    priority?: string
    skip?: number
    limit?: number
  }) => {
    return client.get<TestCase[]>('/test-cases', { params })
  },

  getTestCase: (id: number) => {
    return client.get<TestCase>(`/test-cases/${id}`)
  },

  createTestCase: (data: Partial<TestCase>, teamId: number, userId: number) => {
    return client.post<TestCase>(`/test-cases?team_id=${teamId}&user_id=${userId}`, data)
  },

  updateTestCase: (id: number, data: Partial<TestCase>, userId: number) => {
    return client.put<TestCase>(`/test-cases/${id}?user_id=${userId}`, data)
  },

  deleteTestCase: (id: number) => {
    return client.delete(`/test-cases/${id}`)
  },

  executeTestCase: (id: number, data: {
    environment_id: number
    fail_strategy?: string
    save_record?: boolean
    timeout?: number
    step_interval?: number
  }) => {
    return client.post<any>(`/test-cases/${id}/execute`, data)
  },

  debugTestCase: (id: number, data: {
    environment_id: number
    fail_strategy?: string
    save_record?: boolean
    timeout?: number
    step_interval?: number
  }) => {
    return client.post<any>(`/test-cases/${id}/debug`, data)
  },

  getModules: (teamId?: number) => {
    const params = teamId ? { team_id: teamId } : {}
    return client.get<TestCaseModule[]>('/test-case-modules', { params })
  },

  createModule: (data: Partial<TestCaseModule>) => {
    return client.post<TestCaseModule>('/test-case-modules', data)
  },

  updateModule: (id: number, data: Partial<TestCaseModule>) => {
    return client.put<TestCaseModule>(`/test-case-modules/${id}`, data)
  },

  deleteModule: (id: number) => {
    return client.delete(`/test-case-modules/${id}`)
  },

  getExecutionRecords: (testCaseId: number, params?: {
    status?: string
    executor_id?: number
    page?: number
    page_size?: number
  }) => {
    return client.get<{ items: ExecutionRecord[]; total: number }>(
      `/execution-records/${testCaseId}`,
      { params }
    )
  },

  getExecutionDetail: (executionId: number) => {
    return client.get<ExecutionRecord>(`/execution-records/detail/${executionId}`)
  },
}