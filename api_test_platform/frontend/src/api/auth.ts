import client from './client'
import type {
  LoginRequest,
  RegisterRequest,
  ChangePasswordRequest,
  UpdateUserRequest,
  TokenResponse,
  UserResponse,
} from '@/types/auth'

export const authApi = {
  login: (data: LoginRequest) =>
    client.post<any, TokenResponse>('/auth/login', data),

  register: (data: RegisterRequest) =>
    client.post<any, TokenResponse>('/auth/register', data),

  refresh: (refreshToken: string) =>
    client.post<any, TokenResponse>('/auth/refresh', { refresh_token: refreshToken }),

  logout: () =>
    client.post<any, { message: string }>('/auth/logout'),

  getMe: () =>
    client.get<any, UserResponse>('/auth/me'),

  updateMe: (data: UpdateUserRequest) =>
    client.put<any, UserResponse>('/auth/me', data),

  changePassword: (data: ChangePasswordRequest) =>
    client.put<any, { message: string }>('/auth/password', data),
}
