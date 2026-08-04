import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'
import type { User, LoginRequest, RegisterRequest } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  // Initialize from localStorage
  function init() {
    const savedToken = localStorage.getItem('auth_token')
    const savedUser = localStorage.getItem('auth_user')
    if (savedToken) {
      token.value = savedToken
    }
    if (savedUser) {
      try {
        user.value = JSON.parse(savedUser)
      } catch {
        localStorage.removeItem('auth_user')
      }
    }
  }

  async function login(data: LoginRequest) {
    const response = await authApi.login(data)
    token.value = response.data.access_token
    user.value = response.data.user
    localStorage.setItem('auth_token', response.data.access_token)
    localStorage.setItem('auth_user', JSON.stringify({ username: response.data.user.username, role: response.data.user.role }))
  }

  async function register(data: RegisterRequest) {
    const response = await authApi.register(data)
    token.value = response.data.access_token
    user.value = response.data.user
    localStorage.setItem('auth_token', response.data.access_token)
    localStorage.setItem('auth_user', JSON.stringify({ username: response.data.user.username, role: response.data.user.role }))
  }

  async function fetchUser() {
    try {
      const response = await authApi.getMe()
      user.value = response.data
      localStorage.setItem('auth_user', JSON.stringify({ username: response.data.username, role: response.data.role }))
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_user')
  }

  // Initialize on store creation
  init()

  return {
    user,
    token,
    isAuthenticated,
    login,
    register,
    fetchUser,
    logout,
    init,
  }
})