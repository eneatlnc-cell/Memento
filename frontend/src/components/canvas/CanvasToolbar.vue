<script setup lang="ts">
import {
  ZoomIn,
  ZoomOut,
  Maximize,
  Plus,
  Trash2,
  Undo2,
  Redo2,
  Map,
} from 'lucide-vue-next'

const props = defineProps<{
  scale: number
  canUndo: boolean
  canRedo: boolean
}>()

const emit = defineEmits<{
  'update:scale': [value: number]
  'addNode': []
  'zoomIn': []
  'zoomOut': []
  'fitScreen': []
  'undo': []
  'redo': []
  'clear': []
  'toggleMinimap': []
}>()
</script>

<template>
  <div class="flex items-center gap-1 px-4 py-2 glass border-b border-white/5 z-10">
    <!-- Left group -->
    <div class="flex items-center gap-1">
      <button
        class="p-2 rounded-lg hover:bg-white/10 text-dark-400 hover:text-white transition-colors"
        title="添加节点"
        @click="emit('addNode')"
      >
        <Plus class="w-4 h-4" />
      </button>
      <div class="w-px h-5 bg-white/10 mx-1" />
      <button
        class="p-2 rounded-lg hover:bg-white/10 text-dark-400 hover:text-white transition-colors disabled:opacity-30"
        title="撤销"
        :disabled="!canUndo"
        @click="emit('undo')"
      >
        <Undo2 class="w-4 h-4" />
      </button>
      <button
        class="p-2 rounded-lg hover:bg-white/10 text-dark-400 hover:text-white transition-colors disabled:opacity-30"
        title="重做"
        :disabled="!canRedo"
        @click="emit('redo')"
      >
        <Redo2 class="w-4 h-4" />
      </button>
    </div>

    <!-- Center group -->
    <div class="flex-1 flex items-center justify-center gap-1">
      <button
        class="p-2 rounded-lg hover:bg-white/10 text-dark-400 hover:text-white transition-colors"
        title="缩小"
        @click="emit('zoomOut')"
      >
        <ZoomOut class="w-4 h-4" />
      </button>
      <span class="text-xs text-dark-400 min-w-[48px] text-center font-mono">
        {{ Math.round(scale * 100) }}%
      </span>
      <button
        class="p-2 rounded-lg hover:bg-white/10 text-dark-400 hover:text-white transition-colors"
        title="放大"
        @click="emit('zoomIn')"
      >
        <ZoomIn class="w-4 h-4" />
      </button>
      <button
        class="p-2 rounded-lg hover:bg-white/10 text-dark-400 hover:text-white transition-colors"
        title="适应屏幕"
        @click="emit('fitScreen')"
      >
        <Maximize class="w-4 h-4" />
      </button>
    </div>

    <!-- Right group -->
    <div class="flex items-center gap-1">
      <button
        class="p-2 rounded-lg hover:bg-white/10 text-dark-400 hover:text-white transition-colors"
        title="鹰眼图"
        @click="emit('toggleMinimap')"
      >
        <Map class="w-4 h-4" />
      </button>
      <div class="w-px h-5 bg-white/10 mx-1" />
      <button
        class="p-2 rounded-lg hover:bg-red-500/10 text-dark-400 hover:text-red-400 transition-colors"
        title="清空画布"
        @click="emit('clear')"
      >
        <Trash2 class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>