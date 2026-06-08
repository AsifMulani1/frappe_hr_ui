<script setup>
import Sidebar from "./Sidebar.vue"
import Topbar from "./Topbar.vue"
</script>

<template>
  <div class="flex h-full overflow-hidden bg-surface-gray-1">
    <Sidebar />
    <div class="flex min-w-0 flex-1 flex-col">
      <Topbar />
      <main class="flex-1 overflow-y-auto">
        <RouterView />
      </main>
    </div>
  </div>
</template>
