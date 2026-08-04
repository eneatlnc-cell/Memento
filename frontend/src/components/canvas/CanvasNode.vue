<script setup lang="ts">
import { ref, computed } from 'vue'
import { Trash2, GripHorizontal, Link, Image } from 'lucide-vue-next'

interface NodeData {
  id: string
  x: number
  y: number
  width: number
  height: number
  imageUrl: string
  prompt: string
  selected: boolean
}

const props = defineProps<{
  node: NodeData
  scale: number
}>()

const emit = defineEmits<{
  'update-position': [x: number, y: number]
  'update-position-end': []
  'select': [multi: boolean]
  'connect': []
  'delete': []
}>()

const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const nodeStart = ref({ x: 0, y: 0 })
const contextMenuVisible = ref(false)
const contextMenuPos = ref({ x: 0, y: 0 })

function handleMouseDown(e: MouseEvent) {
  if ((e.target as HTMLElement).closest('.node-action')) return

  emit('select', e.shiftKey || e.metaKey)

  isDragging.value = true
  dragStart.value = { x: e.clientX, y: e.clientY }
  nodeStart.value = { x: props.node.x, y: props.node.y }

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging.value) return
    const dx = (e.clientX - dragStart.value.x) / props.scale
    const dy = (e.clientY - dragStart.value.y) / props.scale
    emit('update-position', nodeStart.value.x + dx, nodeStart.value.y + dy)
  }

  const handleMouseUp = () => {
    isDragging.value = false
    emit('update-position-end')
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }

  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

function handleContextMenu(e: MouseEvent) {
  e.preventDefault()
  contextMenuVisible.value = true
  contextMenuPos.value = { x: e.clientX, y: e.clientY }

  const closeMenu = () => {
    contextMenuVisible.value = false
    document.removeEventListener('click', closeMenu)
  }
  setTimeout(() => document.addEventListener('click', closeMenu), 0)
}

function handleConnect(e: MouseEvent) {
  e.stopPropagation()
  emit('connect')
  contextMenuVisible.value = false
}
</script>

<template>
  <div
    :class="[
      'absolute rounded-xl overflow-hidden transition-shadow duration-200',
      node.selected
        ? 'ring-2 ring-accent-500 shadow-lg shadow-accent-500/20'
        : 'ring-1 ring-white/10 hover:ring-white/20',
    ]"
    :style="{
      left: `${node.x}px`,
      top: `${node.y}px`,
      width: `${node.width}px`,
      height: `${node.height}px`,
      cursor: isDragging ? 'grabbing' : 'grab',
    }"
    @mousedown="handleMouseDown"
    @contextmenu="handleContextMenu"
  >
    <!-- Image -->
    <div class="w-full h-full bg-dark-800 relative">
      <img
        v-if="node.imageUrl"
        :src="node.imageUrl"
        :alt="node.prompt"
        class="w-full h-full object-cover"
        draggable="false"
      />
      <div v-else class="w-full h-full flex items-center justify-center">
        <Image class="w-8 h-8 text-dark-600" />
      </div>

      <!-- Actions overlay -->
      <div
        :class="[
          'absolute top-2 right-2 flex items-center gap-1 transition-opacity',
          node.selected ? 'opacity-100' : 'opacity-0 group-hover:opacity-100',
        ]"
      >
        <button
          class="node-action p-1.5 rounded-lg bg-black/60 hover:bg-black/80 text-white transition-colors"
          @click.stop="handleConnect($event)"
          title="连线"
        >
          <Link class="w-3.5 h-3.5" />
        </button>
        <button
          class="node-action p-1.5 rounded-lg bg-black/60 hover:bg-red-500/80 text-white transition-colors"
          @click.stop="emit('delete')"
          title="删除"
        >
          <Trash2 class="w-3.5 h-3.5" />
        </button>
      </div>

      <!-- Prompt tooltip -->
      <div
        v-if="node.prompt"
        class="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-black/80 to-transparent"
      >
        <p class="text-[10px] text-white/80 line-clamp-1">{{ node.prompt }}</p>
      </div>
    </div>

    <!-- Connection anchor -->
    <div
      class="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 w-3 h-3 rounded-full bg-accent-500 border-2 border-dark-900 cursor-crosshair opacity-0 hover:opacity-100 transition-opacity"
      @mousedown.stop="handleConnect($event)"
    />
  </div>

  <!-- Context Menu -->
  <Teleport to="body">
    <div
      v-if="contextMenuVisible"
      class="fixed z-[200] glass-modal rounded-xl py-1 min-w-[160px] animate-scale-in"
      :style="{ left: `${contextMenuPos.x}px`, top: `${contextMenuPos.y}px` }"
    >
      <button
        class="w-full flex items-center gap-2 px-4 py-2 text-sm text-dark-300 hover:bg-white/5 hover:text-white transition-colors"
        @click="handleConnect"
      >
        <Link class="w-4 h-4" />
        连接节点
      </button>
      <button
        class="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-400 hover:bg-red-500/10 transition-colors"
        @click="emit('delete')"
      >
        <Trash2 class="w-4 h-4" />
        删除节点
      </button>
    </div>
  </Teleport>
</template>