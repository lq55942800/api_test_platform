import { defineStore } from 'pinia'
import { authApi } from '@/api/auth'
import type {
  UserResponse,
  LoginRequest,
  RegisterRequest,
  UpdateUserRequest,
  ChangePasswordRequest,
} from '@/types/auth'
import router from '@/router'

const TOKEN_KEY = 'autotest_token'
const REFRESH_TOKEN_KEY = 'autotest_refresh_token'
const USER_KEY = 'autotest_user'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as UserResponse | null,
    token: null as string | null,
    refreshToken: null as string | null,
  }),

  getters: {
    isAuthenticated: (state): boolean => !!state.token && !!state.user,
  },

  actions: {
    async login(data: LoginRequest) {
      const response = await authApi.login(data)
      this._setAuthData(response)
      return response
    },

    async register(data: RegisterRequest) {
      const response = await authApi.register(data)
      this._setAuthData(response)
      return response
    },

    async logout() {
      try {
        await authApi.logout()
      } catch {
        // Ignore logout API errors
      }
      this._clearAuthData()
      router.push('/login')
    },

    async refreshAccessToken(): Promise<string | null> {
      if (!this.refreshToken) {
        this._clearAuthData()
        return null
      }

      try {
        const response = await authApi.refresh(this.refreshToken)
        this._setAuthData(response)
        return response.access_token
      } catch {
        this._clearAuthData()
        router.push('/login')
        return null
      }
    },

    async fetchUser() {
      try {
        const user = await authApi.getMe()
        this.user = user
        localStorage.setItem(USER_KEY, JSON.stringify(user))
      } catch {
        this._clearAuthData()
      }
    },

    async updateProfile(data: UpdateUserRequest) {
      const user = await authApi.updateMe(data)
      this.user = user
      localStorage.setItem(USER_KEY, JSON.stringify(user))
      return user
    },

    async changePassword(data: ChangePasswordRequest) {
      await authApi.changePassword(data)
    },

    async initAuth() {
      const token = localStorage.getItem(TOKEN_KEY)
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
      const userStr = localStorage.getItem(USER_KEY)

      if (token) {
        this.token = token
        this.refreshToken = refreshToken
        if (userStr) {
          try {
            this.user = JSON.parse(userStr)
          } catch {
            this.user = null
          }
        }
        await this.fetchUser()
      }
    },

    _setAuthData(data: { access_token: string; refresh_token: string; user: UserResponse }) {
      this.token = data.access_token
      this.refreshToken = data.refresh_token
      this.user = data.user

      localStorage.setItem(TOKEN_KEY, data.access_token)
      localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh_token)
      localStorage.setItem(USER_KEY, JSON.stringify(data.user))
    },

    _clearAuthData() {
      this.token = null
      this.refreshToken = null
      this.user = null

      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(REFRESH_TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
    },
  },
})
