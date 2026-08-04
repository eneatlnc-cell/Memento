<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  MessageSquare,
  Image,
  Video,
  Layout,
  ArrowRight,
  Sparkles,
  Zap,
  Shield,
  Code,
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

const features = [
  {
    icon: MessageSquare,
    title: 'AI 对话',
    description: '与智能助手进行自然语言对话，获取创意灵感、编写代码、撰写文案等',
    path: '/chat',
    color: 'from-blue-500 to-cyan-500',
    glow: 'rgba(59, 130, 246, 0.3)',
  },
  {
    icon: Image,
    title: '图片生成',
    description: '输入文字描述，AI 即刻生成精美图片，支持多种风格和尺寸',
    path: '/images',
    color: 'from-purple-500 to-pink-500',
    glow: 'rgba(139, 92, 246, 0.3)',
  },
  {
    icon: Video,
    title: '视频生成',
    description: '从文字或图片生成动态视频，支持关键帧控制和多种分辨率',
    path: '/videos',
    color: 'from-orange-500 to-red-500',
    glow: 'rgba(249, 115, 22, 0.3)',
  },
  {
    icon: Layout,
    title: '无限画布',
    description: '在无限画布上自由排列和组织你的创作，支持节点连接和批量操作',
    path: '/canvas',
    color: 'from-green-500 to-emerald-500',
    glow: 'rgba(34, 197, 94, 0.3)',
  },
]

const highlights = [
  { icon: Zap, title: '极速生成', desc: '毫秒级响应，秒级出图' },
  { icon: Shield, title: '安全可靠', desc: '数据加密存储，隐私保护' },
  { icon: Code, title: 'API 开放', desc: '灵活的 API 接入方式' },
]
</script>

<template>
  <div class="min-h-full p-6 lg:p-8 space-y-12 animate-fade-in">
    <!-- Hero -->
    <div class="text-center pt-8 lg:pt-16 pb-4">
      <div class="inline-flex items-center gap-2 glass-card px-4 py-2 rounded-full mb-6">
        <Sparkles class="w-4 h-4 text-accent-400" />
        <span class="text-sm text-dark-300">AI 驱动的创意平台</span>
      </div>

      <h1 class="text-4xl lg:text-6xl font-bold mb-4">
        <span class="bg-gradient-to-r from-accent-400 via-purple-400 to-blue-400 bg-clip-text text-transparent">
          Memento
        </span>
      </h1>
      <p class="text-lg text-dark-400 max-w-2xl mx-auto">
        一站式 AI 创作平台，集对话、图片生成、视频生成于一体，用你的 API 自由创作
      </p>
      <div class="flex items-center justify-center gap-4 mt-8">
        <button
          v-if="!authStore.isAuthenticated"
          class="glass-button-primary px-6 py-3 rounded-xl text-base font-medium"
          @click="router.push('/login')"
        >
          立即开始
          <ArrowRight class="w-4 h-4" />
        </button>
        <button
          v-else
          class="glass-button-primary px-6 py-3 rounded-xl text-base font-medium"
          @click="router.push('/chat')"
        >
          开始创作
          <ArrowRight class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Highlights -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
      <div
        v-for="item in highlights"
        :key="item.title"
        class="glass-card p-6 text-center animate-slide-up"
      >
        <div class="w-12 h-12 rounded-xl bg-accent-500/20 flex items-center justify-center mx-auto mb-4">
          <component :is="item.icon" class="w-6 h-6 text-accent-400" />
        </div>
        <h3 class="font-semibold text-white mb-1">{{ item.title }}</h3>
        <p class="text-sm text-dark-400">{{ item.desc }}</p>
      </div>
    </div>

    <!-- Features -->
    <div class="max-w-6xl mx-auto">
      <h2 class="text-2xl font-bold text-white text-center mb-8">探索功能</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div
          v-for="feature in features"
          :key="feature.path"
          class="glass-card p-6 group cursor-pointer"
          @click="router.push(feature.path)"
        >
          <div class="flex items-start gap-4">
            <div
              :class="[
                'w-14 h-14 rounded-2xl flex items-center justify-center flex-shrink-0',
                'bg-gradient-to-br',
                feature.color,
              ]"
              :style="{ boxShadow: `0 0 30px ${feature.glow}` }"
            >
              <component :is="feature.icon" class="w-7 h-7 text-white" />
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="text-lg font-semibold text-white mb-1">{{ feature.title }}</h3>
              <p class="text-sm text-dark-400 leading-relaxed">{{ feature.description }}</p>
            </div>
            <div class="flex-shrink-0 self-center opacity-0 group-hover:opacity-100 transition-opacity">
              <ArrowRight class="w-5 h-5 text-accent-400" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="text-center pb-8">
      <p class="text-sm text-dark-500">
        Memento &copy; {{ new Date().getFullYear() }}
      </p>
    </div>
  </div>
</template>