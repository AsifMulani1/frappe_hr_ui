<script setup>
import { computed } from "vue"
const props = defineProps({
  value: { type: Number, default: 0 },
  max: { type: Number, default: 100 },
  size: { type: Number, default: 116 },
  stroke: { type: Number, default: 9 },
})
const r = computed(() => (props.size - props.stroke) / 2)
const c = computed(() => 2 * Math.PI * r.value)
const pct = computed(() => Math.max(0, Math.min(1, props.value / (props.max || 1))))
</script>

<template>
  <svg :width="size" :height="size" :viewBox="`0 0 ${size} ${size}`" class="-rotate-90">
    <circle
      :cx="size / 2"
      :cy="size / 2"
      :r="r"
      fill="none"
      class="stroke-surface-gray-3"
      :stroke-width="stroke"
    />
    <circle
      :cx="size / 2"
      :cy="size / 2"
      :r="r"
      fill="none"
      class="stroke-blue-500 transition-[stroke-dashoffset] duration-700"
      :stroke-width="stroke"
      stroke-linecap="round"
      :stroke-dasharray="c"
      :stroke-dashoffset="c * (1 - pct)"
    />
  </svg>
</template>
