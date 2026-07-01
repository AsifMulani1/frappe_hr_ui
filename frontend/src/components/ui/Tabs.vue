<script setup>
import { Button } from "frappe-ui"
// tabs: [{ id, label, count? }], v-model:active
defineProps({
  tabs: { type: Array, default: () => [] },
  active: String,
})
const emit = defineEmits(["update:active"])
</script>

<template>
  <div class="flex gap-[18px] border-b border-outline-gray-1">
    <Button
      v-for="t in tabs"
      :key="t.id"
      :variant="active === t.id ? 'subtle' : 'ghost'"
      theme="gray"
      :label="t.label"
      @click="emit('update:active', t.id)"
    >
      <template v-if="t.count != null" #suffix>
        <span
          class="rounded-full px-1.5 text-2xs font-medium"
          :class="active === t.id ? 'bg-surface-gray-3 text-ink-gray-8' : 'bg-surface-gray-2 text-ink-gray-5'"
          >{{ t.count }}</span
        >
      </template>
    </Button>
  </div>
</template>
