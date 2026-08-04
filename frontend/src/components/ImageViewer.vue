<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { X, Download, ZoomIn, ZoomOut, RotateCw, ChevronLeft, ChevronRight } from 'lucide-vue-next'

const props = defineProps<{
  images: string[]
  initialIndex?: number
}>()

const emit = defineEmits<{
  close: []
}>()

const currentIndex = ref(props.initialIndex || 0)
const scale = ref(1)
const rotation = ref(0)
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const position = ref({ x: 0, y: 0 })

const currentImage = ref(props.images[currentIndex.value] || '')

watch(
  () => currentIndex.value,
  (idx) => {
    currentImage.value = props.images[idx] || ''
    scale.value = 1
    rotation.value = 0
    position.value = { x: 0, y: 0 }
  }
)

function handleKeydown(e: KeyboardEvent) {
  switch (e.key) {
    case 'Escape':
      emit('close')
      break
    case 'ArrowLeft':
      if (currentIndex.value > 0) currentIndex.value--
      break
    case 'ArrowRight':
      if (currentIndex.value < props.images.length - 1) currentIndex.value++
      break
    case '+':
    case '=':
      scale.value = Math.min(scale.value + 0.25, 5)
      break
    case '-':
      scale.value = Math.max(scale.value - 0.25, 0.25)
      break
  }
}

function handleMouseDown(e: MouseEvent) {
  if (scale.value > 1) {
    isDragging.value = true
    dragStart.value = { x: e.clientX - position.value.x, y: e.clientY - position.value.y }
  }
}

function handleMouseMove(e: MouseEvent) {
  if (isDragging.value) {
    position.value = { x: e.clientX - dragStart.value.x, y: e.clientY - dragStart.value.y }
  }
}

function handleMouseUp() {
  isDragging.value = false
}

function zoomIn() {
  scale.value = Math.min(scale.value + 0.25, 5)
}

function zoomOut() {
  scale.value = Math.max(scale.value - 0.25, 0.25)
}

function rotate() {
  rotation.value = (rotation.value + 90) % 360
}

function resetView() {
  scale.value = 1
  rotation.value = 0
  position.value = { x: 0, y: 0 }
}

async function downloadImage() {
  if (!currentImage.value || (!currentImage.value.startsWith('https://') && !currentImage.value.startsWith('http://'))) return
  try {
    const response = await fetch(currentImage.value)
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `image-${Date.now()}.png`
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    window.open(currentImage.value, '_blank')
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
  document.body.style.overflow = 'hidden'
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = ''
})
</script>

<template>
  <div
    class="fixed inset-0 z-[100] flex items-center justify-center bg-black/90 backdrop-blur-xl animate-fade-in"
    @click.self="emit('close')"
  >
    <!-- Close button -->
    <button
      class="absolute top-4 right-4 p-2 rounded-xl bg-white/10 hover:bg-white/20 text-white transition-colors z-10"
      @click="emit('close')"
    >
      <X class="w-5 h-5" />
    </button>

    <!-- Toolbar -->
    <div class="absolute bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-2 glass rounded-2xl px-4 py-2 z-10">
      <button
        class="p-2 rounded-lg hover:bg-white/10 text-white transition-colors"
        @click="zoomOut"
        :disabled="scale <= 0.25"
      >
        <ZoomOut class="w-4 h-4" />
      </button>
      <span class="text-xs text-dark-300 min-w-[40px] text-center">
        {{ Math.round(scale * 100) }}%
      </span>
      <button
        class="p-2 rounded-lg hover:bg-white/10 text-white transition-colors"
        @click="zoomIn"
        :disabled="scale >= 5"
      >
        <ZoomIn class="w-4 h-4" />
      </button>
      <div class="w-px h-5 bg-white/10" />
      <button
        class="p-2 rounded-lg hover:bg-white/10 text-white transition-colors"
        @click="rotate"
      >
        <RotateCw class="w-4 h-4" />
      </button>
      <button
        class="p-2 rounded-lg hover:bg-white/10 text-white transition-colors"
        @click="resetView"
      >
        <span class="text-xs">1:1</span>
      </button>
      <div class="w-px h-5 bg-white/10" />
      <button
        class="p-2 rounded-lg hover:bg-white/10 text-white transition-colors"
        @click="downloadImage"
      >
        <Download class="w-4 h-4" />
      </button>
    </div>

    <!-- Navigation arrows -->
    <button
      v-if="currentIndex > 0"
      class="absolute left-4 top-1/2 -translate-y-1/2 p-2 rounded-xl bg-white/10 hover:bg-white/20 text-white transition-colors z-10"
      @click="currentIndex--"
    >
      <ChevronLeft class="w-6 h-6" />
    </button>
    <button
      v-if="currentIndex < images.length - 1"
      class="absolute right-4 top-1/2 -translate-y-1/2 p-2 rounded-xl bg-white/10 hover:bg-white/20 text-white transition-colors z-10"
      @click="currentIndex++"
    >
      <ChevronRight class="w-6 h-6" />
    </button>

    <!-- Counter -->
    <div class="absolute top-4 left-4 glass rounded-xl px-3 py-1.5 text-sm text-dark-300 z-10">
      {{ currentIndex + 1 }} / {{ images.length }}
    </div>

    <!-- Image -->
    <div
      class="w-full h-full flex items-center justify-center p-20 select-none"
      @mousedown="handleMouseDown"
      @mousemove="handleMouseMove"
      @mouseup="handleMouseUp"
      @mouseleave="handleMouseUp"
    >
      <img
        :src="currentImage"
        alt="Preview"
        :style="{
          transform: `translate(${position.x}px, ${position.y}px) scale(${scale}) rotate(${rotation}deg)`,
          cursor: scale > 1 ? (isDragging ? 'grabbing' : 'grab') : 'default',
          maxWidth: '90%',
          maxHeight: '90%',
          objectFit: 'contain',
        }"
        class="transition-transform duration-200 rounded-lg"
        draggable="false"
      />
    </div>
  </div>
</template>