<script setup>
import { computed } from "vue"
const props = defineProps({
  label: [String, Number],
  tone: { type: String, default: "neutral" }, // neutral|info|accent|success|warning|danger
  dot: Boolean,
  size: { type: String, default: "md" }, // sm|md
})
const TONES = {
  neutral: "bg-surface-gray-2 text-ink-gray-7 border-outline-gray-2",
  info: "bg-blue-50 text-blue-700 border-blue-100",
  accent: "bg-blue-50 text-blue-700 border-blue-100",
  success: "bg-green-50 text-green-700 border-green-100",
  warning: "bg-orange-50 text-orange-700 border-orange-100",
  danger: "bg-red-50 text-red-700 border-red-100",
}
const DOT = {
  neutral: "bg-ink-gray-5", info: "bg-blue-500", accent: "bg-blue-500",
  success: "bg-green-500", warning: "bg-orange-500", danger: "bg-red-500",
}
const cls = computed(() => TONES[props.tone] || TONES.neutral)
</script>

<template>
  <span
    class="inline-flex items-center gap-1.5 whitespace-nowrap rounded-full border font-medium leading-5"
    :class="[cls, size === 'sm' ? 'px-[7px] text-[11.5px]' : 'px-[9px] text-[12.5px]']"
  >
    <span v-if="dot" class="h-1.5 w-1.5 rounded-full" :class="DOT[tone] || DOT.neutral" />
    <slot>{{ label }}</slot>
  </span>
</template>
