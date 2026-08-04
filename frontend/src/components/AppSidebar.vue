<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  Home,
  MessageSquare,
  Image,
  Video,
  Layout,
  History,
  Settings,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  LogIn,
  User,
  LogOut,
} from 'lucide-vue-next'

const props = defineProps<{
  collapsed: boolean
  mobileOpen: boolean
}>()

const emit = defineEmits<{
  toggle: []
  closeMobile: []
}>()

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const navItems = [
  { path: '/', name: '首页', icon: Home },
  { path: '/chat', name: 'AI 对话', icon: MessageSquare, auth: true },
  { path: '/images', name: '图片生成', icon: Image, auth: true },
  { path: '/videos', name: '视频生成', icon: Video, auth: true },
  { path: '/canvas', name: '无限画布', icon: Layout, auth: true },
  { path: '/history', name: '历史记录', icon: History, auth: true },
  { path: '/settings', name: '设置', icon: Settings, auth: true },
]

const visibleItems = computed(() =>
  navItems.filter((item) => !item.auth || authStore.isAuthenticated)
)

function isActive(path: string): boolean {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

function navigate(path: string) {
  router.push(path)
  emit('closeMobile')
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
  emit('closeMobile')
}
</script>

<template>
  <aside
    :class="[
      'fixed top-0 left-0 h-full z-50 flex flex-col transition-all duration-300',
      'glass border-r border-white/5',
      collapsed ? 'w-16' : 'w-64',
      mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
    ]"
  >
    <!-- Logo -->
    <div class="flex items-center h-16 px-4 border-b border-white/5">
      <div class="flex items-center gap-3 flex-1 min-w-0">
        <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-500 to-blue-500 flex items-center justify-center flex-shrink-0">
          <Sparkles class="w-5 h-5 text-white" />
        </div>
        <transition name="fade">
          <span
            v-if="!collapsed"
            class="font-bold text-lg bg-gradient-to-r from-accent-400 to-blue-400 bg-clip-text text-transparent whitespace-nowrap"
          >
            Memento
          </span>
        </transition>
      </div>
      <button
        class="hidden lg:flex p-1.5 rounded-lg hover:bg-white/10 transition-colors"
        @click="emit('toggle')"
      >
        <ChevronLeft v-if="!collapsed" class="w-4 h-4 text-dark-400" />
        <ChevronRight v-else class="w-4 h-4 text-dark-400" />
      </button>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 overflow-y-auto py-4 px-2">
      <div class="space-y-1">
        <button
          v-for="item in visibleItems"
          :key="item.path"
          @click="navigate(item.path)"
          :class="[
            'w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group',
            isActive(item.path)
              ? 'bg-accent-500/20 text-accent-400 border border-accent-500/30'
              : 'text-dark-300 hover:bg-white/5 hover:text-white',
          ]"
          :title="collapsed ? item.name : ''"
        >
          <component :is="item.icon" class="w-5 h-5 flex-shrink-0" />
          <transition name="fade">
            <span v-if="!collapsed" class="text-sm font-medium whitespace-nowrap">
              {{ item.name }}
            </span>
          </transition>
          <div
            v-if="isActive(item.path) && !collapsed"
            class="ml-auto w-1.5 h-1.5 rounded-full bg-accent-400"
          />
        </button>
      </div>
    </nav>

    <!-- User Section -->
    <div class="p-3 border-t border-white/5">
      <template v-if="authStore.isAuthenticated && authStore.user">
        <div
          :class="[
            'flex items-center gap-3 p-2 rounded-xl transition-colors',
            collapsed ? 'justify-center' : '',
          ]"
        >
          <div class="w-8 h-8 rounded-full bg-accent-500/30 flex items-center justify-center flex-shrink-0">
            <User class="w-4 h-4 text-accent-400" />
          </div>
          <transition name="fade">
            <div v-if="!collapsed" class="flex-1 min-w-0">
              <p class="text-sm font-medium text-white truncate">
                {{ authStore.user.username }}
              </p>
              <p class="text-xs text-dark-400">
                {{ authStore.user.role === 'admin' ? '管理员' : '用户' }}
              </p>
            </div>
          </transition>
          <button
            v-if="!collapsed"
            class="p-1.5 rounded-lg hover:bg-white/10 transition-colors"
            @click="handleLogout"
            title="退出登录"
          >
            <LogOut class="w-4 h-4 text-dark-400" />
          </button>
        </div>
      </template>
      <template v-else>
        <button
          @click="navigate('/login')"
          :class="[
            'w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200',
            'text-dark-300 hover:bg-white/5 hover:text-white',
            collapsed ? 'justify-center' : '',
          ]"
        >
          <LogIn class="w-5 h-5 flex-shrink-0" />
          <transition name="fade">
            <span v-if="!collapsed" class="text-sm font-medium">登录</span>
          </transition>
        </button>
      </template>
    </div>
  </aside>
</template>