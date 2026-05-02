import client from './client'
import type { ApiDefinition } from '@/types/api'

const TEAM_ID = 1

interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

interface ApiListParams {
  page?: number
  page_size?: number
  module_id?: number
  keyword?: string
  method?: string
  status?: string
}

interface DebugParams {
  method: string
  url: string
  headers?: Record<string, string>
  body?: string
  pre_request_actions?: any[]
  post_request_actions?: any[]
}

interface Module {
  id: number
  name: string
  parent_id: number | null
  project_id: number
  sort_order: number
  children?: Module[]
}

interface Tag {
  id: number
  name: string
  project_id: number
}

export const apiApi = {
  async list(params?: ApiListParams): Promise<PaginatedResponse<ApiDefinition>> {
    return client.get(`/teams/${TEAM_ID}/apis`, { params })
  },

  async get(id: number): Promise<ApiDefinition> {
    return client.get(`/apis/${id}`)
  },

  async create(data: Partial<ApiDefinition>): Promise<ApiDefinition> {
    return client.post(`/teams/${TEAM_ID}/apis`, data)
  },

  async update(id: number, data: Partial<ApiDefinition>): Promise<ApiDefinition> {
    return client.put(`/apis/${id}`, data)
  },

  async delete(id: number): Promise<void> {
    return client.delete(`/apis/${id}`)
  },

  async copy(id: number): Promise<ApiDefinition> {
    return client.post(`/apis/${id}/copy`)
  },

  async updateStatus(id: number, status: string): Promise<ApiDefinition> {
    return client.put(`/apis/${id}/status`, { status })
  },

  async batchDelete(api_ids: number[]): Promise<void> {
    return client.post('/apis/batch-delete', { api_ids })
  },

  async batchMove(api_ids: number[], target_module_id: number): Promise<void> {
    return client.post('/apis/batch-move', { api_ids, target_module_id })
  },

  async batchUpdateStatus(api_ids: number[], status: string): Promise<void> {
    return client.post('/apis/batch-status', { api_ids, status })
  },

  async debug(apiId: number, data: DebugParams): Promise<any> {
    return client.post(`/apis/${apiId}/debug`, data)
  },

  async listDebugHistories(apiId: number, params?: { page: number; page_size: number }): Promise<PaginatedResponse<any>> {
    return client.get(`/apis/${apiId}/debug-histories`, { params })
  },

  async listVersions(apiId: number, params?: { page: number; page_size: number }): Promise<PaginatedResponse<any>> {
    return client.get(`/apis/${apiId}/versions`, { params })
  },

  async compareVersions(apiId: number, v1: number, v2: number): Promise<any> {
    return client.get(`/apis/${apiId}/versions/compare`, { params: { v1, v2 } })
  },

  async rollbackVersion(apiId: number, versionNumber: number): Promise<ApiDefinition> {
    return client.post(`/apis/${apiId}/versions/${versionNumber}/rollback`)
  },
}

export const moduleApi = {
  async list(): Promise<Module[]> {
    return client.get(`/teams/${TEAM_ID}/api-modules`)
  },

  async create(data: Partial<Module>): Promise<Module> {
    return client.post(`/teams/${TEAM_ID}/api-modules`, data)
  },

  async update(id: number, data: Partial<Module>): Promise<Module> {
    return client.put(`/api-modules/${id}`, data)
  },

  async delete(id: number): Promise<void> {
    return client.delete(`/api-modules/${id}`)
  },
}

export const tagApi = {
  async list(): Promise<Tag[]> {
    return client.get(`/teams/${TEAM_ID}/api-tags`)
  },

  async create(data: Partial<Tag>): Promise<Tag> {
    return client.post(`/teams/${TEAM_ID}/api-tags`, data)
  },

  async delete(id: number): Promise<void> {
    return client.delete(`/api-tags/${id}`)
  },
}

export const recentApi = {
  async list(): Promise<any[]> {
    return client.get('/apis/recent')
  },
}

export const importApi = {
  async preview(data: { file_type: string; file_content: string; module_id?: number }): Promise<any> {
    return client.post(`/teams/${TEAM_ID}/apis/import/preview`, data)
  },

  async execute(data: { file_type: string; file_content: string; module_id?: number; overwrite?: boolean }): Promise<any> {
    return client.post(`/teams/${TEAM_ID}/apis/import`, data)
  },
}
