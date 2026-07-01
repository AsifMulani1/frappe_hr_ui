<script setup>
defineProps({
  pad: { type: Boolean, default: true },
  hover: { type: Boolean, default: false },
})
</script>

<template>
  <div
    class="rounded-[10px] border border-outline-gray-1 bg-surface-base shadow-sm transition-shadow"
    :class="[pad ? 'p-5' : '', hover ? 'hover:border-outline-gray-2 hover:shadow-md' : '']"
  >
    <slot />
  </div>
</template>
