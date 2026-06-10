<script setup>
// Generic create/edit drawer. Render a list of fields as FormControls bound to
// a single reactive `modelValue` object. Keeps every in-app form consistent.
import { Button, FormControl } from "frappe-ui"
import Drawer from "./Drawer.vue"
import DateField from "./DateField.vue"

const props = defineProps({
  open: Boolean,
  title: String,
  subtitle: String,
  width: { type: Number, default: 500 },
  // [{ key, label, type, options?, placeholder?, cols? }]
  fields: { type: Array, default: () => [] },
  modelValue: { type: Object, default: () => ({}) },
  loading: Boolean,
  submitLabel: { type: String, default: "Create" },
})
const emit = defineEmits(["update:modelValue", "submit", "close"])

function set(key, val) {
  emit("update:modelValue", { ...props.modelValue, [key]: val })
}
</script>

<template>
  <Drawer :open="open" :title="title" :subtitle="subtitle" :width="width" @close="emit('close')">
    <div class="grid grid-cols-2 gap-x-3 gap-y-4">
      <div v-for="f in fields" :key="f.key" :class="f.cols === 1 ? 'col-span-1' : 'col-span-2'">
        <DateField
          v-if="f.type === 'date'"
          :label="f.label"
          :placeholder="f.placeholder"
          :model-value="modelValue[f.key]"
          @update:model-value="set(f.key, $event)"
        />
        <FormControl
          v-else
          :type="f.type || 'text'"
          :label="f.label"
          :placeholder="f.placeholder"
          :options="f.options"
          :model-value="modelValue[f.key]"
          @update:model-value="set(f.key, $event)"
        />
      </div>
    </div>
    <template #footer>
      <Button variant="ghost" label="Cancel" @click="emit('close')" />
      <Button variant="solid" theme="blue" :label="submitLabel" :loading="loading" @click="emit('submit')" />
    </template>
  </Drawer>
</template>
