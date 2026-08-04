<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Sparkles, Mail, Lock, User, Loader2, Eye, EyeOff } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isLogin = ref(true)
const loading = ref(false)
const error = ref('')
const showPassword = ref(false)

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const formErrors = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

function validateForm(): boolean {
  let valid = true
  formErrors.username = ''
  formErrors.email = ''
  formErrors.password = ''
  formErrors.confirmPassword = ''

  if (!form.username.trim()) {
    formErrors.username = '请输入用户名'
    valid = false
  } else if (form.username.trim().length < 2) {
    formErrors.username = '用户名至少 2 个字符'
    valid = false
  }

  if (!isLogin.value && !form.email.trim()) {
    formErrors.email = '请输入邮箱'
    valid = false
  } else if (!isLogin.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    formErrors.email = '邮箱格式不正确'
    valid = false
  }

  if (!form.password) {
    formErrors.password = '请输入密码'
    valid = false
  } else if (form.password.length < 6) {
    formErrors.password = '密码至少 6 个字符'
    valid = false
  }

  if (!isLogin.value && form.password !== form.confirmPassword) {
    formErrors.confirmPassword = '两次密码不一致'
    valid = false
  }

  return valid
}

async function handleSubmit() {
  if (!validateForm()) return

  loading.value = true
  error.value = ''

  try {
    if (isLogin.value) {
      await authStore.login({
        username: form.username,
        password: form.password,
      })
    } else {
      await authStore.register({
        username: form.username,
        email: form.email,
        password: form.password,
      })
    }
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch (err: any) {
    const msg = err?.response?.data?.detail || err?.response?.data?.message || '操作失败，请重试'
    error.value = msg
  } finally {
    loading.value = false
  }
}

function toggleMode() {
  isLogin.value = !isLogin.value
  error.value = ''
  formErrors.username = ''
  formErrors.email = ''
  formErrors.password = ''
  formErrors.confirmPassword = ''
}
</script>

<template>
  <div class="min-h-full flex items-center justify-center p-6">
    <div class="w-full max-w-md animate-slide-up">
      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-accent-500 to-blue-500 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-accent-500/30">
          <Sparkles class="w-8 h-8 text-white" />
        </div>
        <h1 class="text-2xl font-bold text-white mb-1">
          {{ isLogin ? '欢迎回来' : '创建账号' }}
        </h1>
        <p class="text-sm text-dark-400">
          {{ isLogin ? '登录你的 Creative AI 账号' : '注册以开始使用 Creative AI' }}
        </p>
      </div>

      <!-- Form -->
      <div class="glass-card p-6 space-y-4">
        <!-- Error -->
        <div
          v-if="error"
          class="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-sm text-red-400 animate-fade-in"
        >
          {{ error }}
        </div>

        <!-- Username -->
        <div>
          <label class="block text-xs font-medium text-dark-400 mb-1.5">用户名</label>
          <div class="relative">
            <User class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500" />
            <input
              v-model="form.username"
              type="text"
              class="glass-input pl-10"
              placeholder="输入用户名"
              @keyup.enter="handleSubmit"
            />
          </div>
          <p v-if="formErrors.username" class="text-xs text-red-400 mt-1">{{ formErrors.username }}</p>
        </div>

        <!-- Email (register only) -->
        <div v-if="!isLogin">
          <label class="block text-xs font-medium text-dark-400 mb-1.5">邮箱</label>
          <div class="relative">
            <Mail class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500" />
            <input
              v-model="form.email"
              type="email"
              class="glass-input pl-10"
              placeholder="输入邮箱地址"
              @keyup.enter="handleSubmit"
            />
          </div>
          <p v-if="formErrors.email" class="text-xs text-red-400 mt-1">{{ formErrors.email }}</p>
        </div>

        <!-- Password -->
        <div>
          <label class="block text-xs font-medium text-dark-400 mb-1.5">密码</label>
          <div class="relative">
            <Lock class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500" />
            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              class="glass-input pl-10 pr-10"
              placeholder="输入密码"
              @keyup.enter="handleSubmit"
            />
            <button
              type="button"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-dark-500 hover:text-dark-300"
              @click="showPassword = !showPassword"
            >
              <EyeOff v-if="showPassword" class="w-4 h-4" />
              <Eye v-else class="w-4 h-4" />
            </button>
          </div>
          <p v-if="formErrors.password" class="text-xs text-red-400 mt-1">{{ formErrors.password }}</p>
        </div>

        <!-- Confirm Password (register only) -->
        <div v-if="!isLogin">
          <label class="block text-xs font-medium text-dark-400 mb-1.5">确认密码</label>
          <div class="relative">
            <Lock class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500" />
            <input
              v-model="form.confirmPassword"
              :type="showPassword ? 'text' : 'password'"
              class="glass-input pl-10"
              placeholder="再次输入密码"
              @keyup.enter="handleSubmit"
            />
          </div>
          <p v-if="formErrors.confirmPassword" class="text-xs text-red-400 mt-1">{{ formErrors.confirmPassword }}</p>
        </div>

        <!-- Submit -->
        <button
          class="glass-button-primary w-full py-3 text-base font-medium"
          :disabled="loading"
          @click="handleSubmit"
        >
          <Loader2 v-if="loading" class="w-4 h-4 animate-spin" />
          {{ isLogin ? '登录' : '注册' }}
        </button>

        <!-- Toggle -->
        <p class="text-center text-sm text-dark-400">
          {{ isLogin ? '还没有账号？' : '已有账号？' }}
          <button
            class="text-accent-400 hover:text-accent-300 font-medium transition-colors"
            @click="toggleMode"
          >
            {{ isLogin ? '立即注册' : '去登录' }}
          </button>
        </p>
      </div>
    </div>
  </div>
</template>