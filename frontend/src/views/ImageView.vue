<script setup lang="ts">
import { ref, reactive } from 'vue'
import { imagesApi } from '@/api'
import { useAppStore } from '@/stores/app'
import type { Generation, ImageGenerationParams } from '@/types'
import ImageUploader from '@/components/ImageUploader.vue'
import ParamSelector from '@/components/ParamSelector.vue'
import ImageViewer from '@/components/ImageViewer.vue'
import type { ModelOption, AspectRatioOption } from '@/components/ParamSelector.vue'
import {
  Sparkles,
  Loader2,
  Image,
  Download,
  Trash2,
  Plus,
  ImageIcon,
  Wand2,
} from 'lucide-vue-next'

const appStore = useAppStore()

const activeTab = ref<'text-to-image' | 'image-to-image'>('text-to-image')
const prompt = ref('')
const negativePrompt = ref('')
const model = ref('default')
const aspectRatio = ref('1:1')
const advanced = ref(false)
const generating = ref(false)
const error = ref('')
const results = ref<Generation[]>([])
const imageFile = ref<string | File | null>(null)
const strength = ref(0.7)

const viewerVisible = ref(false)
const viewerImages = ref<string[]>([])
const viewerIndex = ref(0)

const models: ModelOption[] = [
  { value: 'default', label: '默认模型', description: '通用高质量图片生成' },
  { value: 'realistic', label: '写实模型', description: '超写实照片级别' },
  { value: 'anime', label: '动漫模型', description: '二次元动漫风格' },
  { value: 'artistic', label: '艺术模型', description: '艺术插画风格' },
]

const aspectRatios: AspectRatioOption[] = [
  { value: '1:1', label: '1:1', width: 1024, height: 1024 },
  { value: '3:4', label: '3:4', width: 768, height: 1024 },
  { value: '4:3', label: '4:3', width: 1024, height: 768 },
  { value: '9:16', label: '9:16', width: 576, height: 1024 },
  { value: '16:9', label: '16:9', width: 1024, height: 576 },
]

async function handleGenerate() {
  if (!prompt.value.trim()) {
    error.value = '请输入提示词'
    return
  }

  generating.value = true
  error.value = ''

  try {
    const ratio = aspectRatios.find((r) => r.value === aspectRatio.value)

    const params: ImageGenerationParams = {
      prompt: prompt.value.trim(),
      negative_prompt: negativePrompt.value || undefined,
      model: model.value,
      width: ratio?.width,
      height: ratio?.height,
      aspect_ratio: aspectRatio.value,
    }

    if (activeTab.value === 'image-to-image' && imageFile.value) {
      if (typeof imageFile.value === 'string') {
        params.image_url = imageFile.value
      }
      params.strength = strength.value
    }

    const response = await imagesApi.generateImage(params)
    results.value.unshift(response.data)

    prompt.value = ''
    negativePrompt.value = ''
    imageFile.value = null
  } catch (err: any) {
    error.value = err?.response?.data?.detail || '生成失败，请重试'
  } finally {
    generating.value = false
  }
}

function openViewer(images: string[], index: number) {
  viewerImages.value = images
  viewerIndex.value = index
  viewerVisible.value = true
}

function downloadImage(url: string) {
  if (!url || (!url.startsWith('https://') && !url.startsWith('http://'))) return
  const a = document.createElement('a')
  a.href = url
  a.download = `image-${Date.now()}.png`
  a.click()
}

function removeResult(index: number) {
  results.value.splice(index, 1)
}
</script>

<template>
  <div class="min-h-full p-6 lg:p-8 animate-fade-in">
    <div class="max-w-6xl mx-auto space-y-8">
      <!-- Header -->
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-purple-500/20 flex items-center justify-center">
          <ImageIcon class="w-5 h-5 text-purple-400" />
        </div>
        <div>
          <h1 class="text-2xl font-bold text-white">图片生成</h1>
          <p class="text-sm text-dark-400">输入提示词，AI 为你生成精美图片</p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Left: Controls -->
        <div class="space-y-6">
          <!-- Tab Switch -->
          <div class="flex glass rounded-xl p-1">
            <button
              :class="[
                'flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-all duration-200',
                activeTab === 'text-to-image'
                  ? 'bg-accent-500/20 text-accent-400'
                  : 'text-dark-400 hover:text-dark-300',
              ]"
              @click="activeTab = 'text-to-image'"
            >
              <Wand2 class="w-4 h-4 inline mr-1.5" />
              文生图
            </button>
            <button
              :class="[
                'flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-all duration-200',
                activeTab === 'image-to-image'
                  ? 'bg-accent-500/20 text-accent-400'
                  : 'text-dark-400 hover:text-dark-300',
              ]"
              @click="activeTab = 'image-to-image'"
            >
              <Image class="w-4 h-4 inline mr-1.5" />
              图生图
            </button>
          </div>

          <!-- Prompt -->
          <div>
            <label class="block text-sm font-medium text-dark-300 mb-2">提示词</label>
            <textarea
              v-model="prompt"
              class="glass-input resize-none h-32"
              placeholder="描述你想要生成的图片..."
              :maxlength="appStore.config?.max_prompt_length || 500"
            />
            <p class="text-xs text-dark-500 mt-1 text-right">
              {{ prompt.length }}/{{ appStore.config?.max_prompt_length || 500 }}
            </p>
          </div>

          <!-- Image Upload (image-to-image) -->
          <div v-if="activeTab === 'image-to-image'">
            <label class="block text-sm font-medium text-dark-300 mb-2">参考图片</label>
            <ImageUploader v-model="imageFile" />

            <div class="mt-4">
              <label class="block text-sm font-medium text-dark-300 mb-2">
                参考强度: {{ strength }}
              </label>
              <input
                v-model.number="strength"
                type="range"
                min="0"
                max="1"
                step="0.05"
                class="w-full accent-accent-500"
              />
              <div class="flex justify-between text-xs text-dark-500">
                <span>原图</span>
                <span>创意</span>
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

          <!-- Generate Button -->
          <button
            class="glass-button-primary w-full py-3 text-base font-medium"
            :disabled="generating || !prompt.trim()"
            @click="handleGenerate"
          >
            <Loader2 v-if="generating" class="w-5 h-5 animate-spin" />
            <Sparkles v-else class="w-5 h-5" />
            {{ generating ? '生成中...' : '生成图片' }}
          </button>

          <!-- Param Selector -->
          <div class="glass-card p-4">
            <ParamSelector
              v-model="model"
              v-model:aspect-ratio="aspectRatio"
              v-model:negative-prompt="negativePrompt"
              v-model:advanced="advanced"
              :models="models"
              :aspect-ratios="aspectRatios"
              :show-negative-prompt="true"
            >
              <template #advanced>
                <div class="space-y-3">
                  <div>
                    <label class="block text-xs text-dark-400 mb-1">数量</label>
                    <select class="glass-input text-sm">
                      <option value="1" class="bg-dark-800">1</option>
                      <option value="2" class="bg-dark-800">2</option>
                      <option value="4" class="bg-dark-800">4</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-xs text-dark-400 mb-1">随机种子</label>
                    <input type="number" class="glass-input text-sm" placeholder="留空为随机" />
                  </div>
                </div>
              </template>
            </ParamSelector>
          </div>
        </div>

        <!-- Right: Results -->
        <div>
          <h3 class="text-lg font-semibold text-white mb-4">生成结果</h3>
          <div
            v-if="results.length === 0"
            class="glass-card p-12 text-center"
          >
            <Image class="w-12 h-12 text-dark-500 mx-auto mb-4" />
            <p class="text-dark-400">还没有生成结果</p>
            <p class="text-sm text-dark-500 mt-1">输入提示词开始生成</p>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div
              v-for="(result, index) in results"
              :key="result.id"
              class="glass-card overflow-hidden animate-scale-in"
            >
              <div
                class="aspect-square bg-dark-800 cursor-pointer relative group"
                @click="result.result_url && openViewer([result.result_url], 0)"
              >
                <img
                  v-if="result.result_url"
                  :src="result.result_url"
                  :alt="result.prompt"
                  class="w-full h-full object-cover"
                />
                <div
                  v-else
                  class="w-full h-full flex items-center justify-center"
                >
                  <Loader2 class="w-8 h-8 text-accent-400 animate-spin" />
                </div>
                <div class="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100">
                  <span class="text-white text-sm font-medium">点击查看大图</span>
                </div>
              </div>
              <div class="p-3">
                <p class="text-xs text-dark-300 line-clamp-2 mb-2">{{ result.prompt }}</p>
                <div class="flex items-center gap-2">
                  <button
                    class="flex-1 glass-button text-xs py-1.5"
                    @click="result.result_url && downloadImage(result.result_url)"
                  >
                    <Download class="w-3.5 h-3.5" />
                    下载
                  </button>
                  <button
                    class="p-1.5 rounded-lg hover:bg-red-500/10 text-dark-400 hover:text-red-400 transition-colors"
                    @click="removeResult(index)"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Image Viewer -->
    <ImageViewer
      v-if="viewerVisible"
      :images="viewerImages"
      :initial-index="viewerIndex"
      @close="viewerVisible = false"
    />
  </div>
</template>