<script setup>
import MetricCard from "./MetricCard.vue"
defineProps({
  items: { type: Array, default: () => [] },
  cols: { type: Number, default: 0 },
})
</script>

<template>
  <div
    class="mb-5 grid gap-5"
    :style="{ gridTemplateColumns: `repeat(${cols || items.length}, minmax(0, 1fr))` }"
  >
    <MetricCard v-for="(m, i) in items" :key="i" v-bind="m" />
  </div>
</template>
