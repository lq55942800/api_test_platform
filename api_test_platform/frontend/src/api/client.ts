import axios from 'axios'
import type { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios'

const client: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

let isRefreshing = false
let failedQueue: Array<{
  resolve: (token: string) => void
  reject: (error: any) => void
}> = []

function processQueue(error: any, token: string | null = null) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error)
    } else {
      resolve(token!)
    }
  })
  failedQueue = []
}

client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('autotest_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

client.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data
  },
  async (error) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (originalRequest.url?.includes('/auth/refresh') || originalRequest.url?.includes('/auth/login')) {
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({
            resolve: (token: string) => {
              originalRequest.headers.Authorization = `Bearer ${token}`
              resolve(client(originalRequest))
            },
            reject,
          })
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const refreshToken = localStorage.getItem('autotest_refresh_token')
        if (!refreshToken) {
          throw new Error('No refresh token')
        }

        const response = await axios.post('/api/v1/auth/refresh', {
          refresh_token: refreshToken,
        })

        const { access_token, refresh_token: new_refresh_token } = response.data
        localStorage.setItem('autotest_token', access_token)
        localStorage.setItem('autotest_refresh_token', new_refresh_token)

        processQueue(null, access_token)

        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return client(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        localStorage.removeItem('autotest_token')
        localStorage.removeItem('autotest_refresh_token')
        localStorage.removeItem('autotest_user')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export default client
