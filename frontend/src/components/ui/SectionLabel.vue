<script setup>
defineProps({ label: String })
</script>

<template>
  <div class="my-0.5 mb-3 flex items-center justify-between">
    <h3 class="text-[13px] font-medium tracking-[.01em] text-ink-gray-5">
      <slot>{{ label }}</slot>
    </h3>
    <slot name="action" />
  </div>
</template>
