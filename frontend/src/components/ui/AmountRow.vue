<script setup>
defineProps({
  label: String,
  value: [String, Number],
  bold: Boolean,
  border: { type: Boolean, default: true },
  color: { type: String, default: "" }, // tailwind text class
})
</script>

<template>
  <div class="flex items-center justify-between py-[9px]" :class="border ? 'border-b border-outline-gray-1' : ''">
    <span class="text-[13.5px]" :class="bold ? 'font-medium text-ink-gray-9' : 'text-ink-gray-7'">{{ label }}</span>
    <span class="tnum text-[13.5px]" :class="[bold ? 'font-medium' : '', color || 'text-ink-gray-9']">{{ value }}</span>
  </div>
</template>
