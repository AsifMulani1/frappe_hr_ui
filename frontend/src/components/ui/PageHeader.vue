<script setup>
import Icon from "./Icon.vue"
defineProps({
  title: String,
  subtitle: String,
  back: String,
})
const emit = defineEmits(["back"])
</script>

<template>
  <div class="mb-[18px]">
    <button
      v-if="back"
      class="mb-2 inline-flex items-center gap-1.5 border-0 bg-transparent p-0 text-[12.5px] text-ink-gray-5 hover:text-ink-gray-7"
      @click="emit('back')"
    >
      <Icon name="chevLeft" :size="14" /> {{ back }}
    </button>
    <div class="flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 class="text-[21px] font-medium tracking-tight text-ink-gray-9">{{ title }}</h1>
        <div v-if="subtitle" class="mt-[3px] text-[13.5px] text-ink-gray-5">{{ subtitle }}</div>
      </div>
      <div v-if="$slots.actions" class="flex items-center gap-2"><slot name="actions" /></div>
    </div>
    <slot name="meta" />
  </div>
</template>
