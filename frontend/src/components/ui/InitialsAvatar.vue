<script setup>
import { computed } from "vue"
import { initials as toInitials } from "@/utils/formatters"

const props = defineProps({
  name: { type: String, default: "" },
  image: { type: String, default: "" },
  size: { type: Number, default: 32 },
  ring: { type: Boolean, default: false },
})

// Deterministic accent from the name, drawn from the prototype's palette.
const PALETTE = ["#0289F7", "#0B9E92", "#DB7706", "#8642C2", "#CF3A96", "#007BE0", "#278F5E", "#E86C13"]
const color = computed(() => {
  let h = 0
  for (const c of props.name || "?") h = (h * 31 + c.charCodeAt(0)) >>> 0
  return PALETTE[h % PALETTE.length]
})
const ini = computed(() => toInitials(props.name))
</script>

<template>
  <div
    class="flex shrink-0 items-center justify-center overflow-hidden rounded-full font-medium"
    :style="{
      width: size + 'px',
      height: size + 'px',
      fontSize: size * 0.4 + 'px',
      background: image ? undefined : `color-mix(in srgb, ${color} 14%, white)`,
      color: color,
      boxShadow: ring ? `0 0 0 2px var(--surface-base, #fff)` : undefined,
      letterSpacing: '.2px',
    }"
  >
    <img v-if="image" :src="image" :alt="name" class="h-full w-full object-cover" />
    <template v-else>{{ ini }}</template>
  </div>
</template>
