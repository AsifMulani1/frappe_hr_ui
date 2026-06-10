<script setup>
import Sidebar from "./Sidebar.vue"
import Topbar from "./Topbar.vue"
import CommandPalette from "./CommandPalette.vue"
import { watch } from "vue"
import { useRoute } from "vue-router"
import { useUiStore } from "@/stores/ui"
const ui = useUiStore()
const route = useRoute()
// Close the off-canvas sidebar whenever the route changes (covers ⌘K, deep links).
watch(() => route.fullPath, () => ui.closeMobileNav())
</script>

<template>
  <div class="flex h-full overflow-hidden bg-surface-gray-1">
    <Sidebar />
    <!-- Backdrop for the off-canvas sidebar (mobile only) -->
    <div
      v-if="ui.mobileNavOpen"
      class="fixed inset-0 z-[65] bg-black/30 lg:hidden"
      @click="ui.closeMobileNav()"
    />
    <div class="flex min-w-0 flex-1 flex-col">
      <Topbar />
      <main class="flex-1 overflow-y-auto">
        <RouterView />
      </main>
    </div>
    <CommandPalette />
  </div>
</template>
