<script setup>
// Espresso date field: a labelled frappe-ui DatePicker. Drop-in replacement for
// the native <input type="date"> (FormControl type="date"), which falls back to
// the OS calendar. Value is YYYY-MM-DD, matching the backend and the old input.
import { DatePicker } from "frappe-ui"

defineProps({
  modelValue: { type: String, default: "" },
  label: String,
  placeholder: { type: String, default: "Select date" },
})
defineEmits(["update:modelValue"])
</script>

<template>
  <div>
    <label v-if="label" class="mb-1.5 block text-xs text-ink-gray-5">{{ label }}</label>
    <DatePicker
      class="w-full"
      :model-value="modelValue"
      :placeholder="placeholder"
      @update:model-value="$emit('update:modelValue', $event)"
    />
  </div>
</template>
