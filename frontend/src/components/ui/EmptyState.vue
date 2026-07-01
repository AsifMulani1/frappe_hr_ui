<script setup>
import Icon from "./Icon.vue"
defineProps({
  icon: { type: String, default: "inbox" },
  title: String,
  message: String,
  compact: Boolean,
})
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-2 text-center" :class="compact ? 'py-8' : 'py-16'">
    <div class="flex h-12 w-12 items-center justify-center rounded-[10px] bg-surface-gray-2 text-ink-gray-4">
      <Icon :name="icon" :size="22" />
    </div>
    <div class="text-base font-medium text-ink-gray-7">{{ title }}</div>
    <div v-if="message" class="max-w-sm text-sm text-ink-gray-5">{{ message }}</div>
    <slot />
  </div>
</template>
