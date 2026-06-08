<script setup>
defineProps({
  label: String,
  value: [String, Number],
  full: Boolean,
})
</script>

<template>
  <div :class="full ? 'col-span-full' : ''">
    <div class="mb-[3px] text-[12px] text-ink-gray-5">{{ label }}</div>
    <div class="text-[13.5px] font-medium text-ink-gray-9">{{ value || "—" }}</div>
  </div>
</template>
