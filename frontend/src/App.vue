<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AppSidebar from './components/AppSidebar.vue'

const sidebarCollapsed = ref(false)
const mobileMenuOpen = ref(false)

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}
</script>

<template>
  <div class="flex h-screen overflow-hidden bg-dark-950">
    <!-- Mobile overlay -->
    <div
      v-if="mobileMenuOpen"
      class="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
      @click="mobileMenuOpen = false"
    />

    <!-- Sidebar -->
    <AppSidebar
      :collapsed="sidebarCollapsed"
      :mobile-open="mobileMenuOpen"
      @toggle="toggleSidebar"
      @close-mobile="mobileMenuOpen = false"
    />

    <!-- Main Content -->
    <main
      :class="[
        'flex-1 overflow-auto transition-all duration-300',
        sidebarCollapsed ? 'lg:ml-16' : 'lg:ml-64',
      ]"
    >
      <!-- Mobile header -->
      <div class="lg:hidden flex items-center gap-3 p-4 glass border-b border-white/5">
        <button
          class="p-2 rounded-lg hover:bg-white/10 transition-colors"
          @click="toggleMobileMenu"
        >
          <span class="block w-5 h-0.5 bg-white mb-1" />
          <span class="block w-5 h-0.5 bg-white mb-1" />
          <span class="block w-5 h-0.5 bg-white" />
        </button>
        <span class="font-semibold text-lg">Creative AI</span>
      </div>

      <router-view v-slot="{ Component, route }">
        <transition name="fade" mode="out-in">
          <component :is="Component" :key="route.path" />
        </transition>
      </router-view>
    </main>
  </div>
</template>