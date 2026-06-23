<script setup>
import { computed } from "vue"
import { Badge } from "frappe-ui"

const props = defineProps({
  label: [String, Number],
  tone: { type: String, default: "neutral" }, // neutral|info|accent|success|warning|danger
  dot: Boolean,
  size: { type: String, default: "md" }, // sm|md
})

// Map this app's semantic tones onto frappe-ui Badge themes.
const THEME = {
  neutral: "gray",
  info: "blue",
  accent: "blue",
  success: "green",
  warning: "orange",
  danger: "red",
}
const DOT = {
  neutral: "bg-ink-gray-5", info: "bg-blue-500", accent: "bg-blue-500",
  success: "bg-green-500", warning: "bg-orange-500", danger: "bg-red-500",
}
const theme = computed(() => THEME[props.tone] || "gray")
</script>

<template>
  <Badge :theme="theme" variant="subtle" :size="size === 'sm' ? 'sm' : 'md'" :label="label">
    <template v-if="dot" #prefix>
      <span class="h-1.5 w-1.5 rounded-full" :class="DOT[tone] || DOT.neutral" />
    </template>
    <slot>{{ label }}</slot>
  </Badge>
</template>
