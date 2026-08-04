<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { historyApi } from '@/api'
import type { Generation, HistoryFilter, PaginatedResponse } from '@/types'
import ImageViewer from '@/components/ImageViewer.vue'
import {
  Search,
  Filter,
  Grid3x3,
  List,
  Trash2,
  CheckSquare,
  Square,
  ChevronLeft,
  ChevronRight,
  Loader2,
  Image,
  Video,
  HistoryIcon,
  X,
} from 'lucide-vue-next'

// State
const items = ref<Generation[]>([])
const loading = ref(false)
const selectedIds = ref<Set<number>>(new Set())
const selectAll = ref(false)
const viewerVisible = ref(false)
const viewerImages = ref<string[]>([])
const viewerIndex = ref(0)

const filter = reactive<HistoryFilter>({
  type: undefined,
  start_date: '',
  end_date: '',
  search: '',
  page: 1,
  page_size: 20,
})

const pagination = reactive({
  total: 0,
  total_pages: 0,
  page: 1,
})

const showFilters = ref(false)

async function fetchHistory() {
  loading.value = true
  try {
    const response = await historyApi.getHistory({ ...filter })
    items.value = response.data.data
    pagination.total = response.data.total
    pagination.total_pages = response.data.total_pages
    pagination.page = response.data.page
  } catch (err) {
    console.error('Failed to fetch history:', err)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  filter.page = 1
  fetchHistory()
}

function handlePageChange(page: number) {
  filter.page = page
  fetchHistory()
}

function toggleSelect(id: number) {
  const newSet = new Set(selectedIds.value)
  if (newSet.has(id)) {
    newSet.delete(id)
  } else {
    newSet.add(id)
  }
  selectedIds.value = newSet
}

function toggleSelectAll() {
  if (selectAll.value) {
    selectedIds.value = new Set()
    selectAll.value = false
  } else {
    selectedIds.value = new Set(items.value.map((i) => i.id))
    selectAll.value = true
  }
}

async function handleBatchDelete() {
  if (selectedIds.value.size === 0) return
  if (!confirm(`确定删除 ${selectedIds.value.size} 条记录？`)) return

  try {
    await historyApi.batchDeleteHistory(Array.from(selectedIds.value))
    selectedIds.value = new Set()
    selectAll.value = false
    fetchHistory()
  } catch (err) {
    console.error('Failed to delete:', err)
  }
}

async function handleDelete(id: number) {
  if (!confirm('确定删除这条记录？')) return
  try {
    await historyApi.deleteHistory(id)
    fetchHistory()
  } catch (err) {
    console.error('Failed to delete:', err)
  }
}

function openViewer(urls: string[], index: number) {
  viewerImages.value = urls
  viewerIndex.value = index
  viewerVisible.value = true
}

function clearFilters() {
  filter.type = undefined
  filter.start_date = ''
  filter.end_date = ''
  filter.search = ''
  filter.page = 1
  fetchHistory()
}

onMounted(() => {
  fetchHistory()
})

watch(
  () => filter.type,
  () => {
    filter.page = 1
    fetchHistory()
  }
)
</script>

<template>
  <div class="min-h-full p-6 lg:p-8 animate-fade-in">
    <div class="max-w-6xl mx-auto space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center">
            <HistoryIcon class="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h1 class="text-2xl font-bold text-white">历史记录</h1>
            <p class="text-sm text-dark-400">共 {{ pagination.total }} 条</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <button
            class="glass-button text-sm"
            @click="showFilters = !showFilters"
          >
            <Filter class="w-4 h-4" />
            筛选
          </button>
          <button
            v-if="selectedIds.size > 0"
            class="glass-button-danger text-sm"
            @click="handleBatchDelete"
          >
            <Trash2 class="w-4 h-4" />
            删除 ({{ selectedIds.size }})
          </button>
        </div>
      </div>

      <!-- Filters -->
      <div v-if="showFilters" class="glass-card p-4 space-y-4 animate-slide-down">
        <div class="flex items-center gap-4 flex-wrap">
          <!-- Search -->
          <div class="flex-1 min-w-[200px]">
            <div class="relative">
              <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500" />
              <input
                v-model="filter.search"
                class="glass-input pl-10 text-sm"
                placeholder="搜索提示词..."
                @keyup.enter="handleSearch"
              />
            </div>
          </div>

          <!-- Type filter -->
          <div class="flex glass rounded-lg p-0.5">
            <button
              :class="[
                'px-3 py-1.5 rounded-md text-xs font-medium transition-colors',
                !filter.type ? 'bg-accent-500/20 text-accent-400' : 'text-dark-400 hover:text-dark-300',
              ]"
              @click="filter.type = undefined"
            >
              全部
            </button>
            <button
              :class="[
                'px-3 py-1.5 rounded-md text-xs font-medium transition-colors',
                filter.type === 'image' ? 'bg-accent-500/20 text-accent-400' : 'text-dark-400 hover:text-dark-300',
              ]"
              @click="filter.type = 'image'"
            >
              <Image class="w-3.5 h-3.5 inline mr-1" />
              图片
            </button>
            <button
              :class="[
                'px-3 py-1.5 rounded-md text-xs font-medium transition-colors',
                filter.type === 'video' ? 'bg-accent-500/20 text-accent-400' : 'text-dark-400 hover:text-dark-300',
              ]"
              @click="filter.type = 'video'"
            >
              <Video class="w-3.5 h-3.5 inline mr-1" />
              视频
            </button>
          </div>

          <!-- Date -->
          <div class="flex items-center gap-2">
            <input
              v-model="filter.start_date"
              type="date"
              class="glass-input text-sm w-36"
            />
            <span class="text-dark-500">-</span>
            <input
              v-model="filter.end_date"
              type="date"
              class="glass-input text-sm w-36"
            />
          </div>

          <button
            class="glass-button text-sm"
            @click="handleSearch"
          >
            搜索
          </button>
          <button
            class="text-sm text-dark-400 hover:text-dark-300"
            @click="clearFilters"
          >
            <X class="w-4 h-4 inline" />
            清除
          </button>
        </div>
      </div>

      <!-- Select all -->
      <div v-if="items.length > 0" class="flex items-center gap-3">
        <button
          class="flex items-center gap-2 text-sm text-dark-400 hover:text-dark-300"
          @click="toggleSelectAll"
        >
          <component :is="selectAll ? CheckSquare : Square" class="w-4 h-4" />
          全选
        </button>
      </div>

      <!-- Grid -->
      <div v-if="loading" class="flex items-center justify-center py-20">
        <Loader2 class="w-8 h-8 text-accent-400 animate-spin" />
      </div>

      <div
        v-else-if="items.length === 0"
        class="glass-card p-12 text-center"
      >
        <HistoryIcon class="w-12 h-12 text-dark-500 mx-auto mb-4" />
        <p class="text-dark-400">暂无历史记录</p>
      </div>

      <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        <div
          v-for="item in items"
          :key="item.id"
          :class="[
            'glass-card overflow-hidden cursor-pointer transition-all duration-200 group',
            selectedIds.has(item.id) ? 'ring-2 ring-accent-500' : 'hover:ring-1 hover:ring-white/20',
          ]"
          @click="item.result_url && openViewer([item.result_url], 0)"
        >
          <div class="aspect-square bg-dark-800 relative">
            <img
              v-if="item.thumbnail_url || item.result_url"
              :src="item.thumbnail_url || item.result_url"
              :alt="item.prompt"
              class="w-full h-full object-cover"
            />
            <div v-else class="w-full h-full flex items-center justify-center">
              <Video class="w-8 h-8 text-dark-500" />
            </div>

            <!-- Select checkbox -->
            <button
              class="absolute top-2 left-2 p-1 rounded-lg bg-black/50 group-hover:opacity-100 transition-opacity"
              :class="selectedIds.has(item.id) ? 'opacity-100' : 'opacity-0'"
              @click.stop="toggleSelect(item.id)"
            >
              <component :is="selectedIds.has(item.id) ? CheckSquare : Square" class="w-4 h-4 text-white" />
            </button>

            <!-- Type badge -->
            <div class="absolute top-2 right-2 px-2 py-0.5 rounded-lg bg-black/60 text-xs text-white flex items-center gap-1">
              <Image v-if="item.type === 'image'" class="w-3 h-3" />
              <Video v-else class="w-3 h-3" />
              {{ item.type === 'image' ? '图片' : '视频' }}
            </div>
          </div>
          <div class="p-3">
            <p class="text-xs text-dark-300 line-clamp-2 mb-2">{{ item.prompt }}</p>
            <div class="flex items-center justify-between">
              <span class="text-[10px] text-dark-500">
                {{ new Date(item.created_at).toLocaleDateString() }}
              </span>
              <button
                class="p-1 rounded hover:bg-red-500/10 text-dark-500 hover:text-red-400 transition-colors"
                @click.stop="handleDelete(item.id)"
              >
                <Trash2 class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="pagination.total_pages > 1" class="flex items-center justify-center gap-2">
        <button
          class="glass-button p-2"
          :disabled="pagination.page <= 1"
          @click="handlePageChange(pagination.page - 1)"
        >
          <ChevronLeft class="w-4 h-4" />
        </button>
        <span
          v-for="p in pagination.total_pages"
          :key="p"
          :class="[
            'w-8 h-8 rounded-lg flex items-center justify-center text-sm cursor-pointer transition-colors',
            p === pagination.page
              ? 'bg-accent-500/20 text-accent-400'
              : 'text-dark-400 hover:bg-white/5',
          ]"
          @click="handlePageChange(p)"
        >
          {{ p }}
        </span>
        <button
          class="glass-button p-2"
          :disabled="pagination.page >= pagination.total_pages"
          @click="handlePageChange(pagination.page + 1)"
        >
          <ChevronRight class="w-4 h-4" />
        </button>
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