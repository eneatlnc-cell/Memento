<script setup lang="ts">
import { ref, reactive } from 'vue'
import { videosApi } from '@/api'
import { useAppStore } from '@/stores/app'
import type { Generation, VideoGenerationParams } from '@/types'
import ImageUploader from '@/components/ImageUploader.vue'
import TaskCard from '@/components/TaskCard.vue'
import {
  Video,
  Sparkles,
  Loader2,
  Play,
  Film,
  Image,
  Layers,
} from 'lucide-vue-next'

const appStore = useAppStore()

const activeTab = ref<'text-to-video' | 'image-to-video' | 'keyframe'>('text-to-video')
const prompt = ref('')
const negativePrompt = ref('')
const model = ref('default')
const resolution = ref('1080p')
const duration = ref(5)
const fps = ref(24)
const numFrames = ref(120)
const generating = ref(false)
const error = ref('')
const tasks = ref<Generation[]>([])
const imageFile = ref<string | File | null>(null)
const keyframeUrls = ref<string[]>([])

const models = [
  { value: 'default', label: '默认模型' },
  { value: 'smooth', label: '流畅模型' },
  { value: 'realistic', label: '写实模型' },
]

const resolutions = [
  { value: '720p', label: '720p (1280x720)' },
  { value: '1080p', label: '1080p (1920x1080)' },
  { value: '2k', label: '2K (2560x1440)' },
]

async function handleGenerate() {
  if (!prompt.value.trim()) {
    error.value = '请输入提示词'
    return
  }

  generating.value = true
  error.value = ''

  try {
    const params: VideoGenerationParams = {
      prompt: prompt.value.trim(),
      negative_prompt: negativePrompt.value || undefined,
      model: model.value,
      duration: duration.value,
      fps: fps.value,
      num_frames: numFrames.value,
    }

    if (activeTab.value === 'image-to-video' && imageFile.value) {
      if (typeof imageFile.value === 'string') {
        params.image_url = imageFile.value
      }
    }

    if (activeTab.value === 'keyframe' && keyframeUrls.value.length > 0) {
      params.keyframe_urls = keyframeUrls.value
    }

    const response = await videosApi.createVideo(params)
    tasks.value.unshift(response.data)

    prompt.value = ''
    negativePrompt.value = ''
    imageFile.value = null
    keyframeUrls.value = []
  } catch (err: any) {
    error.value = err?.response?.data?.detail || '生成失败，请重试'
  } finally {
    generating.value = false
  }
}

function handleDownload(taskId: number) {
  const task = tasks.value.find((t) => t.id === taskId)
  if (task?.result_url) {
    window.open(task.result_url, '_blank')
  }
}

function handleDelete(taskId: number) {
  tasks.value = tasks.value.filter((t) => t.id !== taskId)
}
</script>

<template>
  <div class="min-h-full p-6 lg:p-8 animate-fade-in">
    <div class="max-w-6xl mx-auto space-y-8">
      <!-- Header -->
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-orange-500/20 flex items-center justify-center">
          <Film class="w-5 h-5 text-orange-400" />
        </div>
        <div>
          <h1 class="text-2xl font-bold text-white">视频生成</h1>
          <p class="text-sm text-dark-400">从文字或图片生成高质量视频</p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Left: Controls -->
        <div class="space-y-6">
          <!-- Tab Switch -->
          <div class="flex glass rounded-xl p-1">
            <button
              v-for="tab in [
                { key: 'text-to-video', label: '文生视频', icon: Video },
                { key: 'image-to-video', label: '图生视频', icon: Image },
                { key: 'keyframe', label: '关键帧', icon: Layers },
              ]"
              :key="tab.key"
              :class="[
                'flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all duration-200',
                activeTab === tab.key
                  ? 'bg-accent-500/20 text-accent-400'
                  : 'text-dark-400 hover:text-dark-300',
              ]"
              @click="activeTab = tab.key as any"
            >
              <component :is="tab.icon" class="w-4 h-4 inline mr-1" />
              {{ tab.label }}
            </button>
          </div>

          <!-- Prompt -->
          <div>
            <label class="block text-sm font-medium text-dark-300 mb-2">提示词</label>
            <textarea
              v-model="prompt"
              class="glass-input resize-none h-28"
              placeholder="描述你想要生成的视频内容..."
              :maxlength="appStore.config?.max_prompt_length || 500"
            />
            <p class="text-xs text-dark-500 mt-1 text-right">
              {{ prompt.length }}/{{ appStore.config?.max_prompt_length || 500 }}
            </p>
          </div>

          <!-- Image Upload -->
          <div v-if="activeTab === 'image-to-video'">
            <label class="block text-sm font-medium text-dark-300 mb-2">参考图片</label>
            <ImageUploader v-model="imageFile" aspect-ratio="16:9" />
          </div>

          <!-- Keyframe URLs -->
          <div v-if="activeTab === 'keyframe'">
            <label class="block text-sm font-medium text-dark-300 mb-2">关键帧图片</label>
            <div class="space-y-2">
              <div
                v-for="(url, i) in keyframeUrls"
                :key="i"
                class="flex items-center gap-2"
              >
                <input
                  :value="url"
                  class="glass-input flex-1 text-sm"
                  placeholder="关键帧图片 URL"
                  @input="keyframeUrls[i] = ($event.target as HTMLInputElement).value"
                />
                <button
                  class="p-2 rounded-lg hover:bg-red-500/10 text-dark-400 hover:text-red-400"
                  @click="keyframeUrls.splice(i, 1)"
                >
                  <span class="text-xs">移除</span>
                </button>
              </div>
              <button
                class="glass-button text-xs"
                @click="keyframeUrls.push('')"
              >
                添加关键帧
              </button>
            </div>
          </div>

          <!-- Parameters -->
          <div class="glass-card p-4 space-y-4">
            <h4 class="text-sm font-medium text-dark-300">参数设置</h4>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs text-dark-400 mb-1">模型</label>
                <select v-model="model" class="glass-input text-sm">
                  <option
                    v-for="m in models"
                    :key="m.value"
                    :value="m.value"
                    class="bg-dark-800"
                  >
                    {{ m.label }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-xs text-dark-400 mb-1">分辨率</label>
                <select v-model="resolution" class="glass-input text-sm">
                  <option
                    v-for="r in resolutions"
                    :key="r.value"
                    :value="r.value"
                    class="bg-dark-800"
                  >
                    {{ r.label }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-xs text-dark-400 mb-1">时长 (秒)</label>
                <input
                  v-model.number="duration"
                  type="number"
                  min="1"
                  max="30"
                  class="glass-input text-sm"
                />
              </div>
              <div>
                <label class="block text-xs text-dark-400 mb-1">帧率 (FPS)</label>
                <select v-model.number="fps" class="glass-input text-sm">
                  <option :value="24" class="bg-dark-800">24</option>
                  <option :value="30" class="bg-dark-800">30</option>
                  <option :value="60" class="bg-dark-800">60</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Error -->
          <div
            v-if="error"
            class="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-sm text-red-400"
          >
            {{ error }}
          </div>

          <!-- Generate -->
          <button
            class="glass-button-primary w-full py-3 text-base font-medium"
            :disabled="generating || !prompt.trim()"
            @click="handleGenerate"
          >
            <Loader2 v-if="generating" class="w-5 h-5 animate-spin" />
            <Sparkles v-else class="w-5 h-5" />
            {{ generating ? '生成中...' : '生成视频' }}
          </button>
        </div>

        <!-- Right: Tasks -->
        <div>
          <h3 class="text-lg font-semibold text-white mb-4">任务队列</h3>
          <div
            v-if="tasks.length === 0"
            class="glass-card p-12 text-center"
          >
            <Video class="w-12 h-12 text-dark-500 mx-auto mb-4" />
            <p class="text-dark-400">暂无任务</p>
            <p class="text-sm text-dark-500 mt-1">输入提示词开始生成视频</p>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <TaskCard
              v-for="task in tasks"
              :key="task.id"
              :task="task"
              @download="handleDownload"
              @delete="handleDelete"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>