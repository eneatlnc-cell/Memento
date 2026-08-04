<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { providersApi } from '@/api'
import type { APIProvider, ProviderFormData } from '@/types'
import ProviderForm from '@/components/settings/ProviderForm.vue'
import {
  Settings,
  Server,
  Plus,
  Trash2,
  Edit3,
  Star,
  StarOff,
  CheckCircle2,
  Eye,
  EyeOff,
  Loader2,
  X,
} from 'lucide-vue-next'

const appStore = useAppStore()

const showForm = ref(false)
const editingProvider = ref<APIProvider | null>(null)
const showApiKeys = ref<Set<number>>(new Set())
const loading = ref(false)

async function fetchData() {
  await Promise.all([appStore.fetchProviders(), appStore.fetchConfig()])
}

function handleAdd() {
  editingProvider.value = null
  showForm.value = true
}

function handleEdit(provider: APIProvider) {
  editingProvider.value = provider
  showForm.value = true
}

async function handleFormSubmit(data: ProviderFormData) {
  try {
    if (editingProvider.value) {
      await providersApi.updateProvider(editingProvider.value.id, data)
    } else {
      await providersApi.addProvider(data)
    }
    showForm.value = false
    editingProvider.value = null
    await appStore.fetchProviders()
  } catch (err) {
    if (import.meta.env.DEV) console.error('Failed to save provider:', err)
    throw err
  }
}

async function handleDelete(provider: APIProvider) {
  if (!confirm(`确定删除 Provider "${provider.name}"？`)) return
  try {
    await providersApi.deleteProvider(provider.id)
    await appStore.fetchProviders()
  } catch (err) {
    if (import.meta.env.DEV) console.error('Failed to delete provider:', err)
  }
}

async function handleSetDefault(provider: APIProvider) {
  try {
    await appStore.setCurrentProvider(provider)
  } catch (err) {
    if (import.meta.env.DEV) console.error('Failed to set default:', err)
  }
}

function toggleApiKey(id: number) {
  const newSet = new Set(showApiKeys.value)
  if (newSet.has(id)) {
    newSet.delete(id)
  } else {
    newSet.add(id)
  }
  showApiKeys.value = newSet
}

function maskApiKey(key: string): string {
  if (!key) return '未设置'
  if (key.length <= 8) return '****'
  return key.slice(0, 4) + '****' + key.slice(-4)
}

const typeLabels: Record<string, string> = {
  image: '图片',
  video: '视频',
  chat: '对话',
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="min-h-full p-6 lg:p-8 animate-fade-in">
    <div class="max-w-4xl mx-auto space-y-8">
      <!-- Header -->
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-green-500/20 flex items-center justify-center">
          <Settings class="w-5 h-5 text-green-400" />
        </div>
        <div>
          <h1 class="text-2xl font-bold text-white">设置</h1>
          <p class="text-sm text-dark-400">管理 API Provider 和全局配置</p>
        </div>
      </div>

      <!-- Providers -->
      <div class="glass-card p-6 space-y-6">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <Server class="w-5 h-5 text-accent-400" />
            <h2 class="text-lg font-semibold text-white">API Providers</h2>
          </div>
          <button class="glass-button text-sm" @click="handleAdd">
            <Plus class="w-4 h-4" />
            添加 Provider
          </button>
        </div>

        <!-- Provider Form -->
        <div v-if="showForm" class="animate-slide-down">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-sm font-medium text-dark-300">
              {{ editingProvider ? '编辑 Provider' : '添加 Provider' }}
            </h3>
            <button
              class="p-1.5 rounded-lg hover:bg-white/10 text-dark-400"
              @click="showForm = false"
            >
              <X class="w-4 h-4" />
            </button>
          </div>
          <ProviderForm
            :initial-data="editingProvider || undefined"
            @submit="handleFormSubmit"
            @cancel="showForm = false"
          />
        </div>

        <!-- Provider List -->
        <div v-if="appStore.providers.length === 0 && !appStore.loading" class="text-center py-8">
          <Server class="w-12 h-12 text-dark-500 mx-auto mb-4" />
          <p class="text-dark-400 mb-2">暂无 Provider</p>
          <p class="text-sm text-dark-500">添加一个 API Provider 开始使用</p>
        </div>

        <div v-if="appStore.loading" class="flex items-center justify-center py-8">
          <Loader2 class="w-6 h-6 text-accent-400 animate-spin" />
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="provider in appStore.providers"
            :key="provider.id"
            :class="[
              'flex items-center gap-4 p-4 rounded-xl transition-all duration-200',
              provider.is_default
                ? 'bg-accent-500/10 border border-accent-500/30'
                : 'bg-white/[0.02] border border-white/5 hover:border-white/10',
            ]"
          >
            <!-- Info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <span class="font-medium text-white text-sm">{{ provider.name }}</span>
                <span
                  v-if="provider.is_default"
                  class="px-2 py-0.5 rounded-md bg-accent-500/20 text-accent-400 text-[10px] font-medium flex items-center gap-1"
                >
                  <Star class="w-3 h-3" />
                  默认
                </span>
                <span class="px-2 py-0.5 rounded-md bg-white/5 text-dark-400 text-[10px] font-medium">
                  {{ typeLabels[provider.provider_type] || provider.provider_type }}
                </span>
              </div>
              <div class="flex items-center gap-4 text-xs text-dark-400">
                <span class="truncate">{{ provider.base_url }}</span>
                <span class="flex items-center gap-1">
                  API Key:
                  <code class="text-dark-300 font-mono">
                    {{ maskApiKey(provider.api_key || '') }}
                  </code>
                </span>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex items-center gap-2">
              <button
                v-if="!provider.is_default"
                class="p-2 rounded-lg hover:bg-accent-500/10 text-dark-400 hover:text-accent-400 transition-colors"
                title="设为默认"
                @click="handleSetDefault(provider)"
              >
                <StarOff class="w-4 h-4" />
              </button>
              <button
                class="p-2 rounded-lg hover:bg-white/10 text-dark-400 hover:text-white transition-colors"
                @click="handleEdit(provider)"
              >
                <Edit3 class="w-4 h-4" />
              </button>
              <button
                class="p-2 rounded-lg hover:bg-red-500/10 text-dark-400 hover:text-red-400 transition-colors"
                @click="handleDelete(provider)"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>