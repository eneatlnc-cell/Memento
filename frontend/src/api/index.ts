import axios, { AxiosError, type AxiosInstance, type AxiosRequestConfig } from 'axios'
import type {
  ApiResponse,
  PaginatedResponse,
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  ChangePasswordRequest,
  User,
  APIProvider,
  ProviderFormData,
  Generation,
  ImageGenerationParams,
  VideoGenerationParams,
  ChatHistory,
  ChatMessage,
  AppConfig,
  HistoryFilter,
  SSEChatEvent,
} from '@/types'

const api: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor: add JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor: handle 401
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_user')
      const currentPath = window.location.pathname
      if (currentPath !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// ===== Auth API =====
export const authApi = {
  register(data: RegisterRequest): Promise<ApiResponse<AuthResponse>> {
    return api.post('/auth/register', data).then((r) => r.data)
  },
  login(data: LoginRequest): Promise<ApiResponse<AuthResponse>> {
    return api.post('/auth/login', data).then((r) => r.data)
  },
  getMe(): Promise<ApiResponse<User>> {
    return api.get('/auth/me').then((r) => r.data)
  },
  changePassword(data: ChangePasswordRequest): Promise<ApiResponse<null>> {
    return api.put('/auth/change-password', data).then((r) => r.data)
  },
}

// ===== Images API =====
export const imagesApi = {
  generateImage(params: ImageGenerationParams): Promise<ApiResponse<Generation>> {
    return api.post('/images/generate', params).then((r) => r.data)
  },
}

// ===== Videos API =====
export const videosApi = {
  createVideo(params: VideoGenerationParams): Promise<ApiResponse<Generation>> {
    return api.post('/videos/generate', params).then((r) => r.data)
  },
  getVideoStatus(videoId: number): Promise<ApiResponse<Generation>> {
    return api.get(`/videos/${videoId}/status`).then((r) => r.data)
  },
  deleteVideo(videoId: number): Promise<ApiResponse<null>> {
    return api.delete(`/videos/${videoId}`).then((r) => r.data)
  },
}

// ===== Chat API =====
export const chatApi = {
  sendChatMessage(
    message: string,
    historyId?: number,
    onEvent?: (event: SSEChatEvent) => void,
    onError?: (error: Error) => void
  ): AbortController {
    const controller = new AbortController()
    const token = localStorage.getItem('auth_token')

    const params = new URLSearchParams()
    params.append('message', message)
    if (historyId) params.append('history_id', String(historyId))

    fetch(`/api/chat/send?${params.toString()}`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: 'text/event-stream',
      },
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }
        const reader = response.body?.getReader()
        if (!reader) throw new Error('No response body')

        const decoder = new TextDecoder()
        let buffer = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6).trim()
              if (data === '[DONE]') {
                onEvent?.({ type: 'done' })
                return
              }
              try {
                const event: SSEChatEvent = JSON.parse(data)
                onEvent?.(event)
              } catch {
                // Ignore parse errors for incomplete chunks
              }
            }
          }
        }
      })
      .catch((err) => {
        if (err.name !== 'AbortError') {
          onError?.(err)
        }
      })

    return controller
  },
}

// ===== History API =====
export const historyApi = {
  getHistory(filter: HistoryFilter): Promise<ApiResponse<PaginatedResponse<Generation>>> {
    return api.get('/history', { params: filter }).then((r) => r.data)
  },
  deleteHistory(id: number): Promise<ApiResponse<null>> {
    return api.delete(`/history/${id}`).then((r) => r.data)
  },
  batchDeleteHistory(ids: number[]): Promise<ApiResponse<null>> {
    return api.post('/history/batch-delete', { ids }).then((r) => r.data)
  },
}

// ===== Providers API =====
export const providersApi = {
  getProviders(): Promise<ApiResponse<APIProvider[]>> {
    return api.get('/providers').then((r) => r.data)
  },
  addProvider(data: ProviderFormData): Promise<ApiResponse<APIProvider>> {
    return api.post('/providers', data).then((r) => r.data)
  },
  updateProvider(id: number, data: Partial<ProviderFormData>): Promise<ApiResponse<APIProvider>> {
    return api.put(`/providers/${id}`, data).then((r) => r.data)
  },
  deleteProvider(id: number): Promise<ApiResponse<null>> {
    return api.delete(`/providers/${id}`).then((r) => r.data)
  },
  setDefaultProvider(id: number): Promise<ApiResponse<APIProvider>> {
    return api.put(`/providers/${id}/default`).then((r) => r.data)
  },
}

// ===== Config API =====
export const configApi = {
  getConfig(): Promise<ApiResponse<AppConfig>> {
    return api.get('/config').then((r) => r.data)
  },
}

export default api