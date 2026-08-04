import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { providersApi, configApi } from '@/api'
import type { APIProvider, AppConfig } from '@/types'

export const useAppStore = defineStore('app', () => {
  const sidebarCollapsed = ref(false)
  const providers = ref<APIProvider[]>([])
  const config = ref<AppConfig | null>(null)
  const loading = ref(false)

  const currentProvider = computed(() =>
    providers.value.find((p) => p.is_default) || null
  )

  const imageProviders = computed(() =>
    providers.value.filter((p) => p.provider_type === 'image')
  )

  const videoProviders = computed(() =>
    providers.value.filter((p) => p.provider_type === 'video')
  )

  const chatProviders = computed(() =>
    providers.value.filter((p) => p.provider_type === 'chat')
  )

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  async function fetchProviders() {
    loading.value = true
    try {
      const response = await providersApi.getProviders()
      providers.value = response.data
    } catch (err) {
      if (import.meta.env.DEV) console.error('Failed to fetch providers:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchConfig() {
    try {
      const response = await configApi.getConfig()
      config.value = response.data
    } catch (err) {
      if (import.meta.env.DEV) console.error('Failed to fetch config:', err)
    }
  }

  async function setCurrentProvider(provider: APIProvider) {
    try {
      await providersApi.setDefaultProvider(provider.id)
      await fetchProviders()
    } catch (err) {
      if (import.meta.env.DEV) console.error('Failed to set default provider:', err)
    }
  }

  return {
    sidebarCollapsed,
    providers,
    config,
    loading,
    currentProvider,
    imageProviders,
    videoProviders,
    chatProviders,
    toggleSidebar,
    fetchProviders,
    fetchConfig,
    setCurrentProvider,
  }
})