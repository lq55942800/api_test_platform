import client from './client'
import type { Environment, Service, EnvironmentVariable } from '@/types/api'

interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

interface ListParams {
  page?: number
  page_size?: number
  keyword?: string
}

interface ServiceListParams extends ListParams {
  environment_id?: number
}

export const environmentApi = {
  async list(params?: ListParams): Promise<PaginatedResponse<Environment>> {
    return client.get('/environments', { params })
  },

  async get(id: number): Promise<Environment> {
    return client.get(`/environments/${id}`)
  },

  async create(data: Partial<Environment>): Promise<Environment> {
    return client.post('/environments', data)
  },

  async update(id: number, data: Partial<Environment>): Promise<Environment> {
    return client.put(`/environments/${id}`, data)
  },

  async delete(id: number): Promise<void> {
    return client.delete(`/environments/${id}`)
  },

  async copy(id: number): Promise<Environment> {
    return client.post(`/environments/${id}/copy`)
  },

  async setDefault(id: number): Promise<Environment> {
    return client.put(`/environments/${id}/default`)
  },

  async listAllServices(params?: ServiceListParams): Promise<PaginatedResponse<Service>> {
    return client.get('/environments/services/all', { params })
  },

  async listServices(envId: number, params?: ListParams): Promise<PaginatedResponse<Service>> {
    return client.get(`/environments/${envId}/services`, { params })
  },

  async getService(serviceId: number): Promise<Service> {
    return client.get(`/services/${serviceId}`)
  },

  async createService(envId: number, data: Partial<Service>): Promise<Service> {
    return client.post(`/environments/${envId}/services`, data)
  },

  async updateService(serviceId: number, data: Partial<Service>): Promise<Service> {
    return client.put(`/services/${serviceId}`, data)
  },

  async deleteService(serviceId: number): Promise<void> {
    return client.delete(`/services/${serviceId}`)
  },

  async copyService(serviceId: number): Promise<Service> {
    return client.post(`/services/${serviceId}/copy`)
  },

  async listVariables(envId: number): Promise<EnvironmentVariable[]> {
    return client.get(`/environments/${envId}/variables`)
  },

  async createVariable(envId: number, data: Partial<EnvironmentVariable>): Promise<EnvironmentVariable> {
    return client.post(`/environments/${envId}/variables`, data)
  },

  async updateVariable(variableId: number, data: Partial<EnvironmentVariable>): Promise<EnvironmentVariable> {
    return client.put(`/variables/${variableId}`, data)
  },

  async deleteVariable(variableId: number): Promise<void> {
    return client.delete(`/variables/${variableId}`)
  },
}

interface Server {
  id: number
  service_id: number
  host: string
  port: number
  protocol: string
  description: string
}

interface Database {
  id: number
  service_id: number
  name: string
  type: string
  host: string
  port: number
  username: string
  password: string
  database: string
  description: string
}

interface DatabaseCreate {
  service_id: number
  name: string
  type: string
  host: string
  port: number
  username: string
  password: string
  database: string
  description?: string
}

export const serverApi = {
  async create(serviceId: number, data: Partial<Server>): Promise<Server> {
    return client.post(`/services/${serviceId}/servers`, data)
  },

  async update(id: number, data: Partial<Server>): Promise<Server> {
    return client.put(`/servers/${id}`, data)
  },

  async delete(id: number): Promise<void> {
    return client.delete(`/servers/${id}`)
  },
}

export const databaseApi = {
  async create(serviceId: number, data: DatabaseCreate): Promise<Database> {
    return client.post(`/services/${serviceId}/databases`, data)
  },

  async update(id: number, data: DatabaseCreate): Promise<Database> {
    return client.put(`/databases/${id}`, data)
  },

  async delete(id: number): Promise<void> {
    return client.delete(`/databases/${id}`)
  },

  async testConnection(id: number): Promise<any> {
    return client.post(`/databases/${id}/test-connection`)
  },
}
