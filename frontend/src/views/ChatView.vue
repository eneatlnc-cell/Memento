<script setup lang="ts">
import { ref, nextTick, onMounted, onUnmounted, watch } from 'vue'
import { chatApi } from '@/api'
import type { ChatMessage, SSEChatEvent, ChatHistory } from '@/types'
import {
  Send,
  Plus,
  Loader2,
  Bot,
  User,
  Trash2,
  Wrench,
  CheckCircle2,
  XCircle,
  Sparkles,
} from 'lucide-vue-next'

// State
const messages = ref<ChatMessage[]>([])
const inputText = ref('')
const isSending = ref(false)
const currentAbortController = ref<AbortController | null>(null)
const chatContainer = ref<HTMLDivElement>()
const chatHistories = ref<ChatHistory[]>([])
const currentHistoryId = ref<number | undefined>()
const activeToolCalls = ref<Map<string, { name: string; status: 'pending' | 'done' | 'error' }>>(new Map())
const sidebarOpen = ref(false)

// SSE streaming
const streamingContent = ref('')
const streamingMessageId = ref('')

function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

function handleSend() {
  const text = inputText.value.trim()
  if (!text || isSending.value) return

  // Add user message
  const userMsg: ChatMessage = {
    id: `user-${Date.now()}`,
    role: 'user',
    content: text,
    created_at: new Date().toISOString(),
  }
  messages.value.push(userMsg)
  inputText.value = ''
  scrollToBottom()

  // Start streaming
  isSending.value = true
  streamingContent.value = ''
  const assistantId = `assistant-${Date.now()}`
  streamingMessageId.value = assistantId

  const assistantMsg: ChatMessage = {
    id: assistantId,
    role: 'assistant',
    content: '',
    created_at: new Date().toISOString(),
  }
  messages.value.push(assistantMsg)
  scrollToBottom()

  const controller = chatApi.sendChatMessage(
    text,
    currentHistoryId.value,
    (event: SSEChatEvent) => {
      switch (event.type) {
        case 'content':
          streamingContent.value += event.content || ''
          // Update the assistant message in place
          const idx = messages.value.findIndex((m) => m.id === assistantId)
          if (idx >= 0) {
            messages.value[idx].content = streamingContent.value
          }
          scrollToBottom()
          break

        case 'tool_call':
          if (event.tool_call) {
            activeToolCalls.value.set(event.tool_call.id, {
              name: event.tool_call.name,
              status: 'pending',
            })
          }
          break

        case 'tool_result':
          if (event.tool_call) {
            activeToolCalls.value.set(event.tool_call.id, {
              name: event.tool_call.name,
              status: event.error ? 'error' : 'done',
            })
          }
          break

        case 'done':
          isSending.value = false
          streamingContent.value = ''
          streamingMessageId.value = ''
          currentAbortController.value = null
          break

        case 'error':
          const errIdx = messages.value.findIndex((m) => m.id === assistantId)
          if (errIdx >= 0) {
            messages.value[errIdx].content += '\n\n*[发生错误，请重试]*'
          }
          isSending.value = false
          streamingContent.value = ''
          streamingMessageId.value = ''
          currentAbortController.value = null
          break
      }
    },
    (error: Error) => {
      if (import.meta.env.DEV) console.error('Chat SSE error:', error)
      isSending.value = false
      streamingContent.value = ''
      streamingMessageId.value = ''
      currentAbortController.value = null
    }
  )

  currentAbortController.value = controller
}

function handleStop() {
  currentAbortController.value?.abort()
  isSending.value = false
  streamingContent.value = ''
  streamingMessageId.value = ''
  currentAbortController.value = null
}

function newChat() {
  messages.value = []
  currentHistoryId.value = undefined
  activeToolCalls.value.clear()
  isSending.value = false
  streamingContent.value = ''
  streamingMessageId.value = ''
  currentAbortController.value?.abort()
  currentAbortController.value = null
  sidebarOpen.value = false
}

function escapeHtml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

function formatMessage(content: string): string {
  // Escape HTML first, then apply Markdown-like formatting
  const escaped = escapeHtml(content)
  return escaped
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre class="bg-dark-800 rounded-lg p-3 my-2 overflow-x-auto text-sm"><code>$2</code></pre>')
    .replace(/`([^`]+)`/g, '<code class="bg-dark-800 px-1.5 py-0.5 rounded text-accent-400 text-sm">$1</code>')
    .replace(/\n/g, '<br/>')
}

function formatToolName(name: string): string {
  const names: Record<string, string> = {
    generate_image: '生成图片',
    generate_video: '生成视频',
    search: '搜索信息',
    browse: '浏览网页',
  }
  return names[name] || name
}

onMounted(() => {
  scrollToBottom()
})

onUnmounted(() => {
  currentAbortController.value?.abort()
})
</script>

<template>
  <div class="flex h-[calc(100vh-0px)]">
    <!-- Chat Area -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-white/5 glass">
        <div class="flex items-center gap-3">
          <button
            class="lg:hidden p-2 rounded-lg hover:bg-white/10"
            @click="sidebarOpen = !sidebarOpen"
          >
            <span class="block w-4 h-0.5 bg-white mb-1" />
            <span class="block w-4 h-0.5 bg-white" />
          </button>
          <Bot class="w-5 h-5 text-accent-400" />
          <h2 class="font-semibold text-white">AI 对话</h2>
        </div>
        <button
          class="glass-button text-sm"
          @click="newChat"
        >
          <Plus class="w-4 h-4" />
          新对话
        </button>
      </div>

      <!-- Messages -->
      <div
        ref="chatContainer"
        class="flex-1 overflow-y-auto px-4 py-6 space-y-6"
      >
        <div
          v-if="messages.length === 0"
          class="flex flex-col items-center justify-center h-full text-center"
        >
          <div class="w-20 h-20 rounded-2xl bg-gradient-to-br from-accent-500 to-blue-500 flex items-center justify-center mb-6 animate-float">
            <Sparkles class="w-10 h-10 text-white" />
          </div>
          <h3 class="text-xl font-semibold text-white mb-2">开始对话</h3>
          <p class="text-dark-400 max-w-md">
            输入你的问题或需求，AI 助手将帮助你完成各种任务
          </p>
        </div>

        <div
          v-for="msg in messages"
          :key="msg.id"
          :class="[
            'flex gap-3 animate-slide-up',
            msg.role === 'user' ? 'justify-end' : 'justify-start',
          ]"
        >
          <!-- Avatar -->
          <div
            v-if="msg.role === 'assistant'"
            class="w-8 h-8 rounded-lg bg-accent-500/20 flex items-center justify-center flex-shrink-0 mt-0.5"
          >
            <Bot class="w-4 h-4 text-accent-400" />
          </div>

          <div
            :class="[
              'max-w-[80%] rounded-2xl px-4 py-3',
              msg.role === 'user'
                ? 'bg-accent-500/20 border border-accent-500/30'
                : 'glass-card',
            ]"
          >
            <div
              v-if="msg.role === 'assistant'"
              class="text-sm leading-relaxed text-dark-200"
              v-html="formatMessage(msg.content)"
            />
            <p
              v-else
              class="text-sm leading-relaxed text-white"
            >
              {{ msg.content }}
            </p>

            <!-- Streaming cursor -->
            <span
              v-if="msg.id === streamingMessageId && isSending"
              class="inline-block w-2 h-4 bg-accent-400 ml-0.5 animate-pulse align-middle"
            />
          </div>

          <!-- User avatar -->
          <div
            v-if="msg.role === 'user'"
            class="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center flex-shrink-0 mt-0.5"
          >
            <User class="w-4 h-4 text-blue-400" />
          </div>
        </div>

        <!-- Tool calls indicator -->
        <div
          v-if="activeToolCalls.size > 0"
          class="flex items-center gap-2 px-4 py-3 glass-card w-fit mx-auto"
        >
          <Loader2 class="w-4 h-4 text-accent-400 animate-spin" />
          <div class="text-sm text-dark-300">
            <template v-for="[id, tc] in activeToolCalls" :key="id">
              <span class="flex items-center gap-1.5">
                <Wrench class="w-3.5 h-3.5 text-dark-400" />
                {{ formatToolName(tc.name) }}
                <CheckCircle2 v-if="tc.status === 'done'" class="w-3.5 h-3.5 text-green-400" />
                <XCircle v-else-if="tc.status === 'error'" class="w-3.5 h-3.5 text-red-400" />
                <Loader2 v-else class="w-3.5 h-3.5 text-accent-400 animate-spin" />
              </span>
            </template>
          </div>
        </div>

        <!-- Typing indicator -->
        <div
          v-if="isSending && !streamingContent"
          class="flex items-center gap-3 px-4"
        >
          <div class="w-8 h-8 rounded-lg bg-accent-500/20 flex items-center justify-center">
            <Bot class="w-4 h-4 text-accent-400" />
          </div>
          <div class="glass-card px-4 py-3">
            <div class="typing-dots">
              <span /><span /><span />
            </div>
          </div>
        </div>
      </div>

      <!-- Input -->
      <div class="p-4 border-t border-white/5 glass">
        <div class="flex items-end gap-3 max-w-4xl mx-auto">
          <textarea
            v-model="inputText"
            class="glass-input flex-1 resize-none min-h-[44px] max-h-[120px]"
            :placeholder="isSending ? 'AI 正在回复...' : '输入消息...'"
            rows="1"
            :disabled="isSending"
            @keydown.enter.exact.prevent="handleSend"
            @input="scrollToBottom"
          />
          <button
            v-if="!isSending"
            class="glass-button-primary p-3 rounded-xl"
            :disabled="!inputText.trim()"
            @click="handleSend"
          >
            <Send class="w-5 h-5" />
          </button>
          <button
            v-else
            class="glass-button-danger p-3 rounded-xl"
            @click="handleStop"
          >
            <span class="w-5 h-5 rounded bg-red-400" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>