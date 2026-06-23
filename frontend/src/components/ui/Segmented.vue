<script setup>
import { computed } from "vue"
import { TabButtons } from "frappe-ui"

// options: [{id,label}] or [string]; v-model
const props = defineProps({
  options: { type: Array, default: () => [] },
  modelValue: String,
  size: { type: String, default: "md" },
})
const emit = defineEmits(["update:modelValue"])

const buttons = computed(() =>
  props.options.map((o) =>
    typeof o === "object" ? { label: o.label, value: o.id } : { label: o, value: o }
  )
)
</script>

<template>
  <TabButtons
    :buttons="buttons"
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
  />
</template>
