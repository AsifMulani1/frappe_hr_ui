<script setup>
import { Button } from "frappe-ui"
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
    <Button
      v-if="back"
      class="mb-2"
      variant="ghost"
      :label="back"
      @click="emit('back')"
    >
      <template #prefix><Icon name="chevLeft" :size="14" /></template>
    </Button>
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
