import client from './client'
import type { Environment } from '@/types'

export const environmentApi = {
  getEnvironments: (teamId?: number) => {
    const params = teamId ? { team_id: teamId } : {}
    return client.get<Environment[]>('/environments', { params })
  },

  getEnvironment: (id: number) => {
    return client.get<Environment>(`/environments/${id}`)
  },

  createEnvironment: (data: Partial<Environment>) => {
    return client.post<Environment>('/environments', data)
  },

  updateEnvironment: (id: number, data: Partial<Environment>) => {
    return client.put<Environment>(`/environments/${id}`, data)
  },

  deleteEnvironment: (id: number) => {
    return client.delete(`/environments/${id}`)
  },
}