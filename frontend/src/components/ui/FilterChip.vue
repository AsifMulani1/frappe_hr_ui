<script setup>
import Icon from "./Icon.vue"
defineProps({ label: String, value: [String, Number], active: Boolean })
</script>

<template>
  <button
    class="inline-flex h-[34px] items-center gap-1.5 whitespace-nowrap rounded-md border px-[11px] text-[13px] font-medium"
    :class="active ? 'border-blue-200 bg-blue-50 text-blue-700' : 'border-outline-gray-2 bg-surface-white text-ink-gray-7 hover:bg-surface-gray-1'"
  >
    {{ label }}<span v-if="value != null" :class="active ? 'text-blue-700' : 'text-ink-gray-9'">{{ value }}</span>
    <Icon name="chevDown" :size="14" class="opacity-60" />
  </button>
</template>
