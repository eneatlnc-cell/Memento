<script setup lang="ts">
import { ChevronDown } from 'lucide-vue-next'

export interface ModelOption {
  value: string
  label: string
  description?: string
}

export interface AspectRatioOption {
  value: string
  label: string
  width: number
  height: number
}

const props = withDefaults(
  defineProps<{
    models: ModelOption[]
    modelValue: string
    aspectRatios: AspectRatioOption[]
    aspectRatio: string
    showNegativePrompt?: boolean
    negativePrompt?: string
    advanced?: boolean
  }>(),
  {
    showNegativePrompt: false,
    negativePrompt: '',
    advanced: false,
  }
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'update:aspectRatio': [value: string]
  'update:negativePrompt': [value: string]
  'update:advanced': [value: boolean]
}>()
</script>

<template>
  <div class="space-y-4">
    <!-- Model Select -->
    <div>
      <label class="block text-xs font-medium text-dark-400 mb-2">模型</label>
      <div class="relative">
        <select
          :value="modelValue"
          @change="emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
          class="glass-input appearance-none cursor-pointer pr-10"
        >
          <option
            v-for="model in models"
            :key="model.value"
            :value="model.value"
            class="bg-dark-800"
          >
            {{ model.label }}
          </option>
        </select>
        <ChevronDown class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-400 pointer-events-none" />
      </div>
    </div>

    <!-- Aspect Ratio -->
    <div>
      <label class="block text-xs font-medium text-dark-400 mb-2">尺寸/比例</label>
      <div class="grid grid-cols-3 gap-2">
        <button
          v-for="ratio in aspectRatios"
          :key="ratio.value"
          :class="[
            'px-3 py-2 rounded-lg text-xs font-medium transition-all duration-200',
            aspectRatio === ratio.value
              ? 'bg-accent-500/20 border border-accent-500/40 text-accent-400'
              : 'border border-white/10 text-dark-400 hover:border-white/20 hover:text-dark-300',
          ]"
          @click="emit('update:aspectRatio', ratio.value)"
        >
          <div>{{ ratio.label }}</div>
          <div class="text-[10px] opacity-60">{{ ratio.width }}x{{ ratio.height }}</div>
        </button>
      </div>
    </div>

    <!-- Negative Prompt -->
    <div v-if="showNegativePrompt">
      <label class="block text-xs font-medium text-dark-400 mb-2">反向提示词</label>
      <textarea
        :value="negativePrompt"
        @input="emit('update:negativePrompt', ($event.target as HTMLTextAreaElement).value)"
        class="glass-input resize-none h-20"
        placeholder="不想要的元素..."
      />
    </div>

    <!-- Advanced Toggle -->
    <button
      class="flex items-center gap-2 text-xs text-dark-400 hover:text-dark-300 transition-colors"
      @click="emit('update:advanced', !advanced)"
    >
      <ChevronDown
        :class="[
          'w-3.5 h-3.5 transition-transform',
          advanced ? 'rotate-180' : '',
        ]"
      />
      高级选项
    </button>

    <div v-if="advanced" class="pl-5 space-y-3 animate-slide-down">
      <slot name="advanced" />
    </div>
  </div>
</template>