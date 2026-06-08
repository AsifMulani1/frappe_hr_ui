<script setup>
// tabs: [{ id, label, count? }], v-model:active
defineProps({
  tabs: { type: Array, default: () => [] },
  active: String,
})
const emit = defineEmits(["update:active"])
</script>

<template>
  <div class="flex gap-[18px] border-b border-outline-gray-1">
    <button
      v-for="t in tabs"
      :key="t.id"
      class="-mb-px inline-flex items-center gap-[7px] border-b-[1.5px] px-px py-[9px] text-[13px] transition-colors"
      :class="
        active === t.id
          ? 'border-ink-gray-9 font-medium text-ink-gray-9'
          : 'border-transparent text-ink-gray-5 hover:text-ink-gray-7'
      "
      @click="emit('update:active', t.id)"
    >
      {{ t.label }}
      <span
        v-if="t.count != null"
        class="rounded-full px-1.5 text-[11px] font-medium"
        :class="active === t.id ? 'bg-surface-gray-3 text-ink-gray-8' : 'bg-surface-gray-2 text-ink-gray-5'"
        >{{ t.count }}</span
      >
    </button>
  </div>
</template>
