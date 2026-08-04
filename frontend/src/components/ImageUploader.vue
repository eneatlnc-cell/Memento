<script setup lang="ts">
import { ref, watch } from 'vue'
import { Upload, Link, X, Image } from 'lucide-vue-next'

const props = defineProps<{
  modelValue: string | File | null
  aspectRatio?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string | File | null]
}>()

const isDragging = ref(false)
const urlInput = ref('')
const showUrlInput = ref(false)
const previewUrl = ref<string | null>(null)
const fileInput = ref<HTMLInputElement>()

const acceptedFormats = '.png,.jpg,.jpeg,.webp,.gif'

function handleDragOver(e: DragEvent) {
  e.preventDefault()
  isDragging.value = true
}

function handleDragLeave() {
  isDragging.value = false
}

function handleDrop(e: DragEvent) {
  e.preventDefault()
  isDragging.value = false
  const files = e.dataTransfer?.files
  if (files && files.length > 0) {
    handleFile(files[0])
  }
}

function handleFileSelect(e: Event) {
  const target = e.target as HTMLInputElement
  const files = target.files
  if (files && files.length > 0) {
    handleFile(files[0])
  }
}

function handleFile(file: File) {
  if (!file.type.startsWith('image/')) return
  emit('update:modelValue', file)
  previewUrl.value = URL.createObjectURL(file)
}

function handleUrlSubmit() {
  const url = urlInput.value.trim()
  if (!url) return
  emit('update:modelValue', url)
  previewUrl.value = url
  showUrlInput.value = false
  urlInput.value = ''
}

function clearImage() {
  emit('update:modelValue', null)
  previewUrl.value = null
}

function triggerFileInput() {
  fileInput.value?.click()
}

watch(
  () => props.modelValue,
  (val) => {
    if (!val) {
      previewUrl.value = null
    } else if (typeof val === 'string') {
      previewUrl.value = val
    }
  }
)
</script>

<template>
  <div class="space-y-3">
    <div
      v-if="!previewUrl"
      :class="[
        'relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 cursor-pointer',
        isDragging
          ? 'border-accent-500 bg-accent-500/10'
          : 'border-white/10 hover:border-white/20 hover:bg-white/5',
      ]"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @drop="handleDrop"
      @click="triggerFileInput"
    >
      <input
        ref="fileInput"
        type="file"
        :accept="acceptedFormats"
        class="hidden"
        @change="handleFileSelect"
      />
      <Upload class="w-10 h-10 text-dark-400 mx-auto mb-3" />
      <p class="text-sm text-dark-300 mb-1">
        拖拽图片到此处，或点击上传
      </p>
      <p class="text-xs text-dark-500">
        支持 PNG、JPG、WEBP、GIF
      </p>

      <div class="mt-4">
        <button
          class="glass-button text-xs py-1.5"
          @click.stop="showUrlInput = !showUrlInput"
        >
          <Link class="w-3.5 h-3.5" />
          使用 URL 输入
        </button>
      </div>
    </div>

    <!-- URL Input -->
    <div v-if="showUrlInput && !previewUrl" class="flex gap-2">
      <input
        v-model="urlInput"
        type="text"
        placeholder="输入图片 URL..."
        class="glass-input flex-1 text-sm"
        @keyup.enter="handleUrlSubmit"
      />
      <button class="glass-button text-sm" @click="handleUrlSubmit">确定</button>
      <button
        class="p-2 rounded-lg hover:bg-white/10 text-dark-400"
        @click="showUrlInput = false"
      >
        <X class="w-4 h-4" />
      </button>
    </div>

    <!-- Preview -->
    <div v-if="previewUrl" class="relative">
      <div :class="aspectRatio === '16:9' ? 'aspect-video' : aspectRatio === '9:16' ? 'aspect-[9/16]' : 'aspect-square'">
        <img
          :src="previewUrl"
          alt="Preview"
          class="w-full h-full object-cover rounded-xl"
        />
      </div>
      <button
        class="absolute top-2 right-2 p-1.5 rounded-lg bg-black/60 hover:bg-black/80 text-white transition-colors"
        @click="clearImage"
      >
        <X class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>