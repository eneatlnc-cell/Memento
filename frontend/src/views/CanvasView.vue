<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import CanvasNode from '@/components/canvas/CanvasNode.vue'
import CanvasToolbar from '@/components/canvas/CanvasToolbar.vue'
import {
  Plus,
  ZoomIn,
  ZoomOut,
  Maximize,
  Trash2,
  Undo2,
  Redo2,
} from 'lucide-vue-next'

// Node types
interface CanvasNodeData {
  id: string
  x: number
  y: number
  width: number
  height: number
  imageUrl: string
  prompt: string
  selected: boolean
}

interface Connection {
  id: string
  from: string
  to: string
}

// State
const canvasRef = ref<HTMLDivElement>()
const nodes = ref<CanvasNodeData[]>([])
const connections = ref<Connection[]>([])
const scale = ref(1)
const offset = reactive({ x: 0, y: 0 })
const isPanning = ref(false)
const panStart = ref({ x: 0, y: 0 })
const offsetStart = ref({ x: 0, y: 0 })
const isSpacePressed = ref(false)
const drawingConnection = ref<{ from: string; toX: number; toY: number } | null>(null)
const connectionStart = ref<string | null>(null)
const history = ref<{ nodes: CanvasNodeData[]; connections: Connection[] }[]>([])
const historyIndex = ref(-1)
const showMinimap = ref(true)

let nodeIdCounter = 0

const canUndo = computed(() => historyIndex.value > 0)
const canRedo = computed(() => historyIndex.value < history.value.length - 1)

function saveState() {
  // Remove future states
  history.value = history.value.slice(0, historyIndex.value + 1)
  history.value.push({
    nodes: JSON.parse(JSON.stringify(nodes.value)),
    connections: JSON.parse(JSON.stringify(connections.value)),
  })
  historyIndex.value = history.value.length - 1
}

function undo() {
  if (!canUndo.value) return
  historyIndex.value--
  const state = history.value[historyIndex.value]
  nodes.value = JSON.parse(JSON.stringify(state.nodes))
  connections.value = JSON.parse(JSON.stringify(state.connections))
}

function redo() {
  if (!canRedo.value) return
  historyIndex.value++
  const state = history.value[historyIndex.value]
  nodes.value = JSON.parse(JSON.stringify(state.nodes))
  connections.value = JSON.parse(JSON.stringify(state.connections))
}

function addNode(imageUrl?: string, prompt?: string) {
  const id = `node-${++nodeIdCounter}`
  const centerX = (canvasRef.value?.clientWidth || 800) / 2 - offset.x
  const centerY = (canvasRef.value?.clientHeight || 600) / 2 - offset.y

  nodes.value.push({
    id,
    x: centerX / scale.value - 100 + Math.random() * 50,
    y: centerY / scale.value - 100 + Math.random() * 50,
    width: 200,
    height: 200,
    imageUrl: imageUrl || '',
    prompt: prompt || '',
    selected: false,
  })

  // Deselect all others
  nodes.value.forEach((n) => {
    if (n.id !== id) n.selected = false
  })

  saveState()
}

function addImageNode(imageUrl: string, prompt: string) {
  addNode(imageUrl, prompt)
}

function selectNode(nodeId: string, multi: boolean = false) {
  if (!multi) {
    nodes.value.forEach((n) => {
      n.selected = n.id === nodeId
    })
  } else {
    const node = nodes.value.find((n) => n.id === nodeId)
    if (node) node.selected = !node.selected
  }
}

function clearSelection() {
  nodes.value.forEach((n) => (n.selected = false))
}

function deleteSelected() {
  const selectedIds = nodes.value.filter((n) => n.selected).map((n) => n.id)
  nodes.value = nodes.value.filter((n) => !selectedIds.includes(n.id))
  connections.value = connections.value.filter(
    (c) => !selectedIds.includes(c.from) && !selectedIds.includes(c.to)
  )
  saveState()
}

function clearCanvas() {
  if (confirm('确定要清空画布吗？')) {
    nodes.value = []
    connections.value = []
    saveState()
  }
}

function updateNodePosition(nodeId: string, x: number, y: number) {
  const node = nodes.value.find((n) => n.id === nodeId)
  if (node) {
    node.x = x
    node.y = y
  }
}

function updateNodePositionEnd(nodeId: string) {
  saveState()
}

// Canvas interaction
function handleCanvasMouseDown(e: MouseEvent) {
  if (e.target === canvasRef.value || (e.target as HTMLElement).classList.contains('canvas-bg')) {
    clearSelection()
    if (isSpacePressed.value || e.button === 1) {
      isPanning.value = true
      panStart.value = { x: e.clientX, y: e.clientY }
      offsetStart.value = { x: offset.x, y: offset.y }
    }
  }
}

function handleCanvasMouseMove(e: MouseEvent) {
  if (isPanning.value) {
    const dx = e.clientX - panStart.value.x
    const dy = e.clientY - panStart.value.y
    offset.x = offsetStart.value.x + dx
    offset.y = offsetStart.value.y + dy
  }

  if (drawingConnection.value) {
    drawingConnection.value.toX = (e.clientX - canvasRef.value!.getBoundingClientRect().left - offset.x) / scale.value
    drawingConnection.value.toY = (e.clientY - canvasRef.value!.getBoundingClientRect().top - offset.y) / scale.value
  }
}

function handleCanvasMouseUp() {
  isPanning.value = false
  if (drawingConnection.value) {
    // Check if we're over a node
    const mx = drawingConnection.value.toX
    const my = drawingConnection.value.toY
    const targetNode = nodes.value.find(
      (n) =>
        n.id !== drawingConnection.value!.from &&
        mx >= n.x &&
        mx <= n.x + n.width &&
        my >= n.y &&
        my <= n.y + n.height
    )
    if (targetNode) {
      connections.value.push({
        id: `conn-${Date.now()}`,
        from: drawingConnection.value.from,
        to: targetNode.id,
      })
      saveState()
    }
    drawingConnection.value = null
    connectionStart.value = null
  }
}

function handleWheel(e: WheelEvent) {
  e.preventDefault()
  const delta = e.deltaY > 0 ? -0.1 : 0.1
  const newScale = Math.max(0.1, Math.min(5, scale.value + delta))
  scale.value = newScale
}

function zoomIn() {
  scale.value = Math.min(5, scale.value + 0.2)
}

function zoomOut() {
  scale.value = Math.max(0.1, scale.value - 0.2)
}

function fitToScreen() {
  scale.value = 1
  offset.x = 0
  offset.y = 0
}

function handleNodeDragStart(nodeId: string) {
  // handled by CanvasNode component
}

function handleConnectStart(nodeId: string) {
  connectionStart.value = nodeId
  const node = nodes.value.find((n) => n.id === nodeId)
  if (node) {
    drawingConnection.value = {
      from: nodeId,
      toX: node.x + node.width / 2,
      toY: node.y + node.height / 2,
    }
  }
}

// Keyboard
function handleKeyDown(e: KeyboardEvent) {
  if (e.key === ' ' || e.code === 'Space') {
    e.preventDefault()
    isSpacePressed.value = true
  }
  if (e.key === 'Delete' || e.key === 'Backspace') {
    deleteSelected()
  }
  if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
    e.preventDefault()
    if (e.shiftKey) {
      redo()
    } else {
      undo()
    }
  }
}

function handleKeyUp(e: KeyboardEvent) {
  if (e.key === ' ' || e.code === 'Space') {
    isSpacePressed.value = false
    isPanning.value = false
  }
}

// Minimap
const minimapScale = computed(() => {
  const w = canvasRef.value?.clientWidth || 800
  const h = canvasRef.value?.clientHeight || 600
  return Math.min(150 / w, 150 / h)
})

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
  window.addEventListener('keyup', handleKeyUp)
  saveState()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
  window.removeEventListener('keyup', handleKeyUp)
})

defineExpose({
  addImageNode,
})
</script>

<template>
  <div class="h-[calc(100vh-0px)] flex flex-col overflow-hidden">
    <!-- Toolbar -->
    <CanvasToolbar
      v-model:scale="scale"
      :can-undo="canUndo"
      :can-redo="canRedo"
      @add-node="addNode()"
      @zoom-in="zoomIn"
      @zoom-out="zoomOut"
      @fit-screen="fitToScreen"
      @undo="undo"
      @redo="redo"
      @clear="clearCanvas"
      @toggle-minimap="showMinimap = !showMinimap"
    />

    <!-- Canvas -->
    <div
      ref="canvasRef"
      class="canvas-bg flex-1 relative overflow-hidden"
      :style="{
        background: 'radial-gradient(circle, rgba(255,255,255,0.03) 1px, transparent 1px)',
        backgroundSize: `${20 * scale}px ${20 * scale}px`,
        cursor: isPanning ? 'grabbing' : isSpacePressed ? 'grab' : 'default',
      }"
      @mousedown="handleCanvasMouseDown"
      @mousemove="handleCanvasMouseMove"
      @mouseup="handleCanvasMouseUp"
      @mouseleave="handleCanvasMouseUp"
      @wheel.prevent="handleWheel"
    >
      <!-- Transform layer -->
      <div
        class="absolute inset-0 origin-top-left"
        :style="{
          transform: `translate(${offset.x}px, ${offset.y}px) scale(${scale})`,
        }"
      >
        <!-- Connections -->
        <svg class="absolute inset-0 pointer-events-none" style="width: 10000px; height: 10000px; top: -5000px; left: -5000px;">
          <line
            v-for="conn in connections"
            :key="conn.id"
            :x1="(nodes.find(n => n.id === conn.from)?.x || 0) + (nodes.find(n => n.id === conn.from)?.width || 0) / 2"
            :y1="(nodes.find(n => n.id === conn.from)?.y || 0) + (nodes.find(n => n.id === conn.from)?.height || 0) / 2"
            :x2="(nodes.find(n => n.id === conn.to)?.x || 0) + (nodes.find(n => n.id === conn.to)?.width || 0) / 2"
            :y2="(nodes.find(n => n.id === conn.to)?.y || 0) + (nodes.find(n => n.id === conn.to)?.height || 0) / 2"
            stroke="rgba(139, 92, 246, 0.5)"
            stroke-width="2"
            stroke-dasharray="6,3"
          />

          <!-- Drawing connection -->
          <line
            v-if="drawingConnection"
            :x1="(nodes.find(n => n.id === drawingConnection!.from)?.x || 0) + (nodes.find(n => n.id === drawingConnection!.from)?.width || 0) / 2"
            :y1="(nodes.find(n => n.id === drawingConnection!.from)?.y || 0) + (nodes.find(n => n.id === drawingConnection!.from)?.height || 0) / 2"
            :x2="drawingConnection!.toX"
            :y2="drawingConnection!.toY"
            stroke="rgba(139, 92, 246, 0.8)"
            stroke-width="2"
            stroke-dasharray="6,3"
          />
        </svg>

        <!-- Nodes -->
        <CanvasNode
          v-for="node in nodes"
          :key="node.id"
          :node="node"
          :scale="scale"
          @update-position="(x, y) => updateNodePosition(node.id, x, y)"
          @update-position-end="updateNodePositionEnd(node.id)"
          @select="selectNode(node.id, $event)"
          @connect="handleConnectStart(node.id)"
          @delete="deleteSelected()"
        />
      </div>

      <!-- Empty state -->
      <div
        v-if="nodes.length === 0"
        class="absolute inset-0 flex items-center justify-center pointer-events-none"
      >
        <div class="text-center">
          <p class="text-dark-400 text-lg mb-2">空白画布</p>
          <p class="text-dark-500 text-sm">
            点击工具栏 "添加节点" 或按空格键拖拽画布
          </p>
        </div>
      </div>

      <!-- Scale indicator -->
      <div class="absolute bottom-4 left-4 glass rounded-xl px-3 py-1.5 text-xs text-dark-400">
        {{ Math.round(scale * 100) }}%
      </div>
    </div>

    <!-- Minimap -->
    <div
      v-if="showMinimap && nodes.length > 0"
      class="absolute bottom-4 right-4 w-40 h-28 glass rounded-xl overflow-hidden border border-white/10"
    >
      <div class="absolute inset-0" :style="{ transform: `scale(${minimapScale})`, transformOrigin: 'top left' }">
        <div
          v-for="node in nodes"
          :key="node.id"
          class="absolute rounded bg-accent-500/30"
          :style="{
            left: `${node.x}px`,
            top: `${node.y}px`,
            width: `${node.width}px`,
            height: `${node.height}px`,
          }"
        />
      </div>
      <!-- Viewport indicator -->
      <div
        class="absolute border border-accent-400/60 rounded"
        :style="{
          left: `${-offset.x * minimapScale / scale}px`,
          top: `${-offset.y * minimapScale / scale}px`,
          width: `${(canvasRef?.clientWidth || 800) * minimapScale / scale}px`,
          height: `${(canvasRef?.clientHeight || 600) * minimapScale / scale}px`,
        }"
      />
    </div>
  </div>
</template>

<style scoped>
.canvas-bg {
  background-color: #0a0f1a;
}
</style>