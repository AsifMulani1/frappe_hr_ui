<script setup>
// A Link-field picker with inline "+ New" creation. Pairs with DocForm: the
// "+ New" button emits `create` with the target doctype and an onCreated
// callback; DocForm opens a nested create drawer and calls back with the new
// record's name, which we append to the options and select. This is what lets
// users create a master in-context instead of detouring to the Settings hub.
import { ref, watch } from "vue"
import { Select, Button } from "frappe-ui"
import Icon from "./Icon.vue"

const props = defineProps({
  doctype: { type: String, required: true },
  modelValue: { type: [String, Number], default: undefined },
  options: { type: Array, default: () => [] },
  label: String,
  disabled: Boolean,
  size: { type: String, default: "md" },
  compact: Boolean, // child-table cell: no label
  placeholder: { type: String, default: "" },
})
const emit = defineEmits(["update:modelValue", "create"])

const localOpts = ref([...props.options])
watch(() => props.options, (o) => { localOpts.value = [...(o || [])] })

function addAndSelect(name) {
  if (name && !localOpts.value.some((o) => o.value === name)) {
    localOpts.value.unshift({ label: name, value: name })
  }
  emit("update:modelValue", name)
}
function requestCreate() {
  if (props.doctype && !props.disabled) emit("create", { doctype: props.doctype, onCreated: addAndSelect })
}
</script>

<template>
  <div>
    <label v-if="label && !compact" class="mb-1.5 block text-xs text-ink-gray-5">{{ label }}</label>
    <div class="flex items-center gap-1.5">
      <Select
        class="flex-1"
        :size="size"
        :model-value="modelValue"
        :options="localOpts"
        :disabled="disabled"
        :placeholder="placeholder"
        @update:model-value="emit('update:modelValue', $event)"
      />
      <Button
        variant="ghost"
        :disabled="disabled"
        :label="`New ${doctype}`"
        :tooltip="`New ${doctype}`"
        class="shrink-0"
        @click="requestCreate"
      >
        <template #icon><Icon name="plus" :size="15" /></template>
      </Button>
    </div>
  </div>
</template>
