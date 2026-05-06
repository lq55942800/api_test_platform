import client from './client'
import type { TestCase, TestCaseModule, ExecutionRecord } from '@/types'

interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface SSEStepEvent {
  type: 'started' | 'step' | 'completed' | 'error'
  execution_id?: number
  status?: string
  step_index?: number
  step_name?: string
  duration?: number
  error?: string
  message?: string
  total_steps?: number
  passed_steps?: number
  failed_steps?: number
  skipped_steps?: number
}

export function executeSSE(
  testCaseId: number,
  data: {
    environment_id: number
    fail_strategy?: string
    save_record?: boolean
    timeout?: number
    step_interval?: number
  },
  onEvent: (event: SSEStepEvent) => void,
  onError?: (error: any) => void,
  onComplete?: () => void,
): AbortController {
  const baseUrl = (client.defaults as any).baseURL || '/api/v1'
  const url = `${baseUrl}/test-cases/${testCaseId}/execute?user_id=1`
  const controller = new AbortController()
  fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
    signal: controller.signal,
  }).then(async (response) => {
    if (!response.ok) {
      if (onError) onError(new Error(`HTTP ${response.status}`))
      if (onComplete) onComplete()
      return
    }
    const reader = response.body?.getReader()
    if (!reader) {
      if (onError) onError(new Error('No readable stream'))
      if (onComplete) onComplete()
      return
    }
    const decoder = new TextDecoder()
    let buffer = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const parsed: SSEStepEvent = JSON.parse(line.slice(6))
            onEvent(parsed)
            if (parsed.type === 'completed' || parsed.type === 'error') {
              if (onComplete) onComplete()
              return
            }
          } catch {}
        }
      }
    }
    if (onComplete) onComplete()
  }).catch((e) => {
    if (e.name !== 'AbortError') {
      if (onError) onError(e)
    }
    if (onComplete) onComplete()
  })
  return controller
}

export const testCaseApi = {
  async list(params?: {
    team_id?: number
    module_id?: number
    status?: string
    keyword?: string
    priority?: string
    skip?: number
    limit?: number
  }): Promise<any> {
    return client.get('/test-cases', { params })
  },

  async get(id: number): Promise<TestCase> {
    return client.get(`/test-cases/${id}`)
  },

  async create(data: Partial<TestCase>): Promise<TestCase> {
    return client.post('/test-cases', data, { params: { team_id: 1, user_id: 1 } })
  },

  async update(id: number, data: Partial<TestCase>): Promise<TestCase> {
    return client.put(`/test-cases/${id}`, data, { params: { user_id: 1 } })
  },

  async delete(id: number): Promise<void> {
    return client.delete(`/test-cases/${id}`)
  },

  async execute(id: number, data: {
    environment_id: number
    fail_strategy?: string
    save_record?: boolean
    timeout?: number
    step_interval?: number
  }): Promise<any> {
    return client.post(`/test-cases/${id}/execute`, data)
  },

  async checkCopy(id: number, targetTeamId: number): Promise<any> {
    return client.get(`/test-cases/${id}/check-copy`, { params: { target_team_id: targetTeamId } })
  },

  async copyToTeam(id: number, targetTeamId: number): Promise<TestCase> {
    return client.post(`/test-cases/${id}/copy-to-team`, { target_team_id: targetTeamId })
  },
}

export const testCaseModuleApi = {
  async list(params?: { team_id?: number }): Promise<TestCaseModule[]> {
    return client.get('/test-case-modules', { params: { team_id: 1, ...params } })
  },

  async create(data: Partial<TestCaseModule>): Promise<TestCaseModule> {
    return client.post('/test-case-modules', data)
  },

  async update(id: number, data: Partial<TestCaseModule>): Promise<TestCaseModule> {
    return client.put(`/test-case-modules/${id}`, data)
  },

  async delete(id: number): Promise<void> {
    return client.delete(`/test-case-modules/${id}`)
  },
}

export const executionApi = {
  async list(testCaseId: number, params?: {
    status?: string
    executor_id?: number
    page?: number
    page_size?: number
  }): Promise<PaginatedResponse<ExecutionRecord>> {
    return client.get(`/test-cases/${testCaseId}/executions`, { params })
  },

  async get(executionId: number): Promise<ExecutionRecord> {
    return client.get(`/executions/${executionId}`)
  },

  async listStepExecutions(executionId: number): Promise<any[]> {
    return client.get(`/executions/${executionId}/steps`)
  },

  async retry(executionId: number): Promise<any> {
    return client.post(`/executions/${executionId}/retry`)
  },

  async retryStep(executionId: number, stepId: number): Promise<any> {
    return client.post(`/executions/${executionId}/steps/${stepId}/retry`)
  },

  async exportReport(executionId: number, format: string): Promise<Blob> {
    return client.get(`/executions/${executionId}/export`, { params: { format }, responseType: 'blob' })
  },
}
