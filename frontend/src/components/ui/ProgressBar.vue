<script setup>
import { computed } from "vue"
const props = defineProps({
  value: { type: Number, default: 0 },
  max: { type: Number, default: 100 },
  color: { type: String, default: "bg-blue-500" },
  height: { type: Number, default: 6 },
})
const pct = computed(() => Math.max(0, Math.min(100, (props.value / (props.max || 1)) * 100)))
</script>

<template>
  <div
    class="w-full overflow-hidden rounded-full bg-surface-gray-3"
    :style="{ height: height + 'px' }"
  >
    <div
      class="h-full rounded-full transition-[width] duration-500"
      :class="color"
      :style="{ width: pct + '%' }"
    />
  </div>
</template>
