<script setup lang="ts">
import { computed } from 'vue'
import type { Generation } from '@/types'
import {
  Download,
  Trash2,
  Loader2,
  CheckCircle2,
  XCircle,
  Clock,
  Play,
} from 'lucide-vue-next'

const props = defineProps<{
  task: Generation
}>()

const emit = defineEmits<{
  download: [id: number]
  delete: [id: number]
}>()

const statusConfig = computed(() => {
  switch (props.task.status) {
    case 'pending':
      return { icon: Clock, color: 'text-yellow-400', bg: 'bg-yellow-400/10', label: '等待中' }
    case 'processing':
      return { icon: Loader2, color: 'text-blue-400', bg: 'bg-blue-400/10', label: '处理中' }
    case 'completed':
      return { icon: CheckCircle2, color: 'text-green-400', bg: 'bg-green-400/10', label: '已完成' }
    case 'failed':
      return { icon: XCircle, color: 'text-red-400', bg: 'bg-red-400/10', label: '失败' }
    default:
      return { icon: Clock, color: 'text-dark-400', bg: 'bg-dark-400/10', label: '未知' }
  }
})

const progressPercent = computed(() => {
  if (props.task.status === 'completed') return 100
  return props.task.progress || 0
})
</script>

<template>
  <div class="glass-card p-4 animate-fade-in">
    <!-- Thumbnail -->
    <div class="relative aspect-square rounded-lg overflow-hidden bg-dark-800 mb-3">
      <img
        v-if="task.thumbnail_url"
        :src="task.thumbnail_url"
        :alt="task.prompt"
        class="w-full h-full object-cover"
      />
      <div v-else class="w-full h-full flex items-center justify-center">
        <component
          :is="statusConfig.icon"
          :class="[statusConfig.color, 'w-8 h-8', task.status === 'processing' ? 'animate-spin' : '']"
        />
      </div>

      <!-- Status badge -->
      <div
        :class="[
          'absolute top-2 right-2 px-2 py-1 rounded-lg text-xs font-medium flex items-center gap-1',
          statusConfig.bg,
          statusConfig.color,
        ]"
      >
        <component
          :is="statusConfig.icon"
          :class="[task.status === 'processing' ? 'animate-spin' : '', 'w-3 h-3']"
        />
        {{ statusConfig.label }}
      </div>

      <!-- Video overlay -->
      <div
        v-if="task.type === 'video'"
        class="absolute inset-0 flex items-center justify-center bg-black/30"
      >
        <Play class="w-10 h-10 text-white" />
      </div>
    </div>

    <!-- Progress bar -->
    <div
      v-if="task.status === 'processing'"
      class="mb-3"
    >
      <div class="h-1.5 bg-dark-700 rounded-full overflow-hidden">
        <div
          class="h-full bg-gradient-to-r from-accent-500 to-blue-500 rounded-full transition-all duration-500"
          :style="{ width: `${progressPercent}%` }"
        />
      </div>
      <p class="text-xs text-dark-400 mt-1 text-right">{{ progressPercent }}%</p>
    </div>

    <!-- Error -->
    <p
      v-if="task.status === 'failed' && task.error_message"
      class="text-xs text-red-400 mb-3 line-clamp-2"
    >
      {{ task.error_message }}
    </p>

    <!-- Prompt -->
    <p class="text-xs text-dark-300 line-clamp-2 mb-3">
      {{ task.prompt }}
    </p>

    <!-- Actions -->
    <div class="flex items-center gap-2">
      <button
        v-if="task.status === 'completed' && task.result_url"
        class="flex-1 glass-button text-xs py-1.5"
        @click="emit('download', task.id)"
      >
        <Download class="w-3.5 h-3.5" />
        下载
      </button>
      <button
        class="p-1.5 rounded-lg hover:bg-red-500/10 text-dark-400 hover:text-red-400 transition-colors"
        @click="emit('delete', task.id)"
      >
        <Trash2 class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>