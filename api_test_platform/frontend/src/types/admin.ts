export interface TeamCreate {
  name: string
  description?: string
}

export interface TeamUpdate {
  name?: string
  description?: string
  is_active?: boolean
}

export interface TeamResponse {
  id: number
  name: string
  description: string | null
  is_active: boolean
  member_count: number
  api_count: number
  test_case_count: number
  created_at: string
  updated_at: string
}

export interface TeamMemberCreate {
  user_id: number
  role: string
}

export interface TeamMemberUpdate {
  role: string
}

export interface TeamMemberResponse {
  id: number
  team_id: number
  user_id: number
  username: string
  full_name: string | null
  role: string
  status: string
  joined_at: string
}

export interface AdminUserCreate {
  username: string
  email: string
  password: string
  full_name?: string
  is_superuser?: boolean
}

export interface AdminUserUpdate {
  email?: string
  full_name?: string
  is_active?: boolean
  is_superuser?: boolean
}

export interface AdminUserResponse {
  id: number
  username: string
  email: string
  full_name: string | null
  is_active: boolean
  is_superuser: boolean
  last_login_at: string | null
  created_at: string
  teams: Array<{ team_id: number; team_name: string; role: string }>
}

export interface AdminPasswordReset {
  new_password: string
}

export const MEMBER_ROLES = [
  { value: 'team_leader', label: '团队负责人' },
  { value: 'developer', label: '开发人员' },
  { value: 'tester', label: '测试人员' },
] as const
