<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import type { APIProvider, ProviderFormData, ProviderType } from '@/types'
import { Loader2, Server } from 'lucide-vue-next'

const props = defineProps<{
  initialData?: APIProvider
}>()

const emit = defineEmits<{
  submit: [data: ProviderFormData]
  cancel: []
}>()

const loading = ref(false)
const error = ref('')

const form = reactive<ProviderFormData>({
  name: '',
  provider_type: 'image',
  base_url: '',
  api_key: '',
  is_default: false,
})

const formErrors = reactive({
  name: '',
  base_url: '',
  api_key: '',
})

// Initialize from existing data
watch(
  () => props.initialData,
  (data) => {
    if (data) {
      form.name = data.name
      form.provider_type = data.provider_type
      form.base_url = data.base_url
      form.api_key = data.api_key
      form.is_default = data.is_default
    }
  },
  { immediate: true }
)

function validate(): boolean {
  let valid = true
  formErrors.name = ''
  formErrors.base_url = ''
  formErrors.api_key = ''

  if (!form.name.trim()) {
    formErrors.name = '请输入名称'
    valid = false
  }

  if (!form.base_url.trim()) {
    formErrors.base_url = '请输入 Base URL'
    valid = false
  } else {
    try {
      new URL(form.base_url)
    } catch {
      formErrors.base_url = 'URL 格式不正确'
      valid = false
    }
  }

  if (!form.api_key.trim()) {
    formErrors.api_key = '请输入 API Key'
    valid = false
  }

  return valid
}

async function handleSubmit() {
  if (!validate()) return

  loading.value = true
  error.value = ''

  try {
    await emit('submit', { ...form })
  } catch (err: any) {
    error.value = err?.response?.data?.detail || '保存失败'
  } finally {
    loading.value = false
  }
}

const providerTypes: { value: ProviderType; label: string }[] = [
  { value: 'image', label: '图片生成' },
  { value: 'video', label: '视频生成' },
  { value: 'chat', label: 'AI 对话' },
]
</script>

<template>
  <div class="glass-card p-5 space-y-4">
    <!-- Error -->
    <div
      v-if="error"
      class="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-sm text-red-400"
    >
      {{ error }}
    </div>

    <!-- Name -->
    <div>
      <label class="block text-xs font-medium text-dark-400 mb-1.5">名称</label>
      <input
        v-model="form.name"
        class="glass-input"
        placeholder="例如：OpenAI、Stable Diffusion"
      />
      <p v-if="formErrors.name" class="text-xs text-red-400 mt-1">{{ formErrors.name }}</p>
    </div>

    <!-- Provider Type -->
    <div>
      <label class="block text-xs font-medium text-dark-400 mb-1.5">类型</label>
      <div class="grid grid-cols-3 gap-2">
        <button
          v-for="pt in providerTypes"
          :key="pt.value"
          :class="[
            'py-2 px-3 rounded-lg text-xs font-medium transition-all duration-200',
            form.provider_type === pt.value
              ? 'bg-accent-500/20 border border-accent-500/40 text-accent-400'
              : 'border border-white/10 text-dark-400 hover:border-white/20',
          ]"
          @click="form.provider_type = pt.value"
        >
          {{ pt.label }}
        </button>
      </div>
    </div>

    <!-- Base URL -->
    <div>
      <label class="block text-xs font-medium text-dark-400 mb-1.5">Base URL</label>
      <input
        v-model="form.base_url"
        class="glass-input"
        placeholder="https://api.example.com/v1"
      />
      <p v-if="formErrors.base_url" class="text-xs text-red-400 mt-1">{{ formErrors.base_url }}</p>
    </div>

    <!-- API Key -->
    <div>
      <label class="block text-xs font-medium text-dark-400 mb-1.5">API Key</label>
      <input
        v-model="form.api_key"
        type="password"
        class="glass-input"
        placeholder="sk-..."
      />
      <p v-if="formErrors.api_key" class="text-xs text-red-400 mt-1">{{ formErrors.api_key }}</p>
    </div>

    <!-- Set as default -->
    <label class="flex items-center gap-3 cursor-pointer">
      <input
        v-model="form.is_default"
        type="checkbox"
        class="w-4 h-4 rounded accent-accent-500"
      />
      <span class="text-sm text-dark-300">设为默认 Provider</span>
    </label>

    <!-- Actions -->
    <div class="flex items-center gap-3 pt-2">
      <button
        class="glass-button-primary flex-1 py-2.5"
        :disabled="loading"
        @click="handleSubmit"
      >
        <Loader2 v-if="loading" class="w-4 h-4 animate-spin" />
        {{ initialData ? '保存修改' : '添加 Provider' }}
      </button>
      <button class="glass-button flex-1 py-2.5" @click="emit('cancel')">
        取消
      </button>
    </div>
  </div>
</template>