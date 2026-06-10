<script setup>
import Icon from "./Icon.vue"
defineProps({ search: { type: [String, Boolean], default: "Search…" }, modelValue: String })
const emit = defineEmits(["update:modelValue"])
</script>

<template>
  <div class="mb-3.5 flex flex-wrap items-center gap-2.5">
    <div
      v-if="search !== false"
      class="flex h-[34px] min-w-[220px] flex-[0_1_280px] items-center gap-2 rounded-md border border-outline-gray-2 bg-surface-white px-2.5 text-ink-gray-5"
    >
      <Icon name="search" :size="15" />
      <input
        :value="modelValue"
        :placeholder="search"
        class="w-full border-0 bg-transparent text-[13.5px] text-ink-gray-9 outline-none ring-0 focus:outline-none focus:ring-0 focus:shadow-none"
        @input="emit('update:modelValue', $event.target.value)"
      />
    </div>
    <slot />
    <div class="flex-1" />
    <slot name="right" />
  </div>
</template>
