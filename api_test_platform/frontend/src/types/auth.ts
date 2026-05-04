export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  full_name?: string
}

export interface ChangePasswordRequest {
  old_password: string
  new_password: string
}

export interface UpdateUserRequest {
  full_name?: string
  email?: string
}

export interface UserResponse {
  id: number
  username: string
  email: string
  full_name: string | null
  is_active: boolean
  is_superuser: boolean
  last_login_at: string | null
  created_at: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: UserResponse
}
