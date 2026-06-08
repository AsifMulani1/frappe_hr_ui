<script setup>
// options: [{id,label}] or [string]; v-model
defineProps({ options: { type: Array, default: () => [] }, modelValue: String, size: { type: String, default: "md" } })
const emit = defineEmits(["update:modelValue"])
const id = (o) => (typeof o === "object" ? o.id : o)
const label = (o) => (typeof o === "object" ? o.label : o)
</script>

<template>
  <div class="inline-flex gap-0.5 rounded-md bg-surface-gray-2 p-[3px]">
    <button
      v-for="o in options"
      :key="id(o)"
      class="rounded-[6px] font-medium transition-colors"
      :class="[
        size === 'sm' ? 'px-2.5 py-1 text-[12.5px]' : 'px-[13px] py-[5px] text-[12.5px]',
        modelValue === id(o) ? 'bg-surface-white text-ink-gray-9 shadow-sm' : 'text-ink-gray-5 hover:text-ink-gray-7',
      ]"
      @click="emit('update:modelValue', id(o))"
    >
      {{ label(o) }}
    </button>
  </div>
</template>
