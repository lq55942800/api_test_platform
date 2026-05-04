import client from './client'
import type {
  TeamCreate,
  TeamUpdate,
  TeamResponse,
  TeamMemberCreate,
  TeamMemberUpdate,
  TeamMemberResponse,
  AdminUserCreate,
  AdminUserUpdate,
  AdminUserResponse,
  AdminPasswordReset,
} from '@/types/admin'

export const teamApi = {
  list: (params?: { is_active?: boolean }) =>
    client.get<any, TeamResponse[]>('/admin/teams', { params }),
  get: (id: number) =>
    client.get<any, TeamResponse>(`/admin/teams/${id}`),
  create: (data: TeamCreate) =>
    client.post<any, TeamResponse>('/admin/teams', data),
  update: (id: number, data: TeamUpdate) =>
    client.put<any, TeamResponse>(`/admin/teams/${id}`, data),
  delete: (id: number) =>
    client.delete(`/admin/teams/${id}`),
  listMembers: (teamId: number) =>
    client.get<any, TeamMemberResponse[]>(`/admin/teams/${teamId}/members`),
  addMember: (teamId: number, data: TeamMemberCreate) =>
    client.post<any, TeamMemberResponse>(`/admin/teams/${teamId}/members`, data),
  updateMember: (teamId: number, memberId: number, data: TeamMemberUpdate) =>
    client.put<any, TeamMemberResponse>(`/admin/teams/${teamId}/members/${memberId}`, data),
  removeMember: (teamId: number, memberId: number) =>
    client.delete(`/admin/teams/${teamId}/members/${memberId}`),
}

export const userApi = {
  list: (params?: { is_active?: boolean; search?: string }) =>
    client.get<any, AdminUserResponse[]>('/admin/users', { params }),
  get: (id: number) =>
    client.get<any, AdminUserResponse>(`/admin/users/${id}`),
  create: (data: AdminUserCreate) =>
    client.post<any, AdminUserResponse>('/admin/users', data),
  update: (id: number, data: AdminUserUpdate) =>
    client.put<any, AdminUserResponse>(`/admin/users/${id}`, data),
  delete: (id: number) =>
    client.delete(`/admin/users/${id}`),
  resetPassword: (id: number, data: AdminPasswordReset) =>
    client.put<any, { message: string }>(`/admin/users/${id}/reset-password`, data),
}
