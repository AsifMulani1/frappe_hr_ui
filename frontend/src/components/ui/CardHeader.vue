<script setup>
import Icon from "./Icon.vue"
defineProps({
  title: String,
  sub: String,
  icon: String,
})
</script>

<template>
  <div class="mb-4 flex items-center justify-between gap-3">
    <div class="flex min-w-0 items-center gap-2.5">
      <div
        v-if="icon"
        class="flex h-[30px] w-[30px] shrink-0 items-center justify-center rounded-md bg-surface-gray-2 text-ink-gray-7"
      >
        <Icon :name="icon" :size="17" />
      </div>
      <div class="min-w-0">
        <div class="text-[15px] font-medium text-ink-gray-9">{{ title }}</div>
        <div v-if="sub" class="mt-px text-[12.5px] text-ink-gray-5">{{ sub }}</div>
      </div>
    </div>
    <slot name="action" />
  </div>
</template>
