import client from './client'
import type { ApiDefinition, ApiModule } from '@/types'

export const apiManagementApi = {
  getApis: (params?: {
    team_id?: number
    module_id?: number
    status?: string
    keyword?: string
    skip?: number
    limit?: number
  }) => {
    return client.get<ApiDefinition[]>('/api-management/apis', { params })
  },

  getApi: (id: number) => {
    return client.get<ApiDefinition>(`/api-management/apis/${id}`)
  },

  createApi: (data: Partial<ApiDefinition>) => {
    return client.post<ApiDefinition>('/api-management/apis', data)
  },

  updateApi: (id: number, data: Partial<ApiDefinition>) => {
    return client.put<ApiDefinition>(`/api-management/apis/${id}`, data)
  },

  deleteApi: (id: number) => {
    return client.delete(`/api-management/apis/${id}`)
  },

  getModules: (teamId?: number) => {
    const params = teamId ? { team_id: teamId } : {}
    return client.get<ApiModule[]>('/api-management/modules', { params })
  },

  createModule: (data: Partial<ApiModule>) => {
    return client.post<ApiModule>('/api-management/modules', data)
  },

  updateModule: (id: number, data: Partial<ApiModule>) => {
    return client.put<ApiModule>(`/api-management/modules/${id}`, data)
  },

  deleteModule: (id: number) => {
    return client.delete(`/api-management/modules/${id}`)
  },

  debugApi: (id: number, data: {
    environment_id: number
    param_overrides?: Record<string, any>
    header_overrides?: Record<string, any>
    body_overrides?: any
  }) => {
    return client.post<any>(`/api-management/apis/${id}/debug`, data)
  },
}