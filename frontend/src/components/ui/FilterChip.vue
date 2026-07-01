<script setup>
import { Button } from "frappe-ui"
import Icon from "./Icon.vue"
defineProps({ label: String, value: [String, Number], active: Boolean })
</script>

<template>
  <Button
    class="whitespace-nowrap"
    :variant="active ? 'subtle' : 'outline'"
    theme="gray"
  >
    {{ label }}<span v-if="value != null" :class="active ? 'text-blue-700' : 'text-ink-gray-9'">{{ value }}</span>
    <template #suffix><Icon name="chevDown" :size="14" class="opacity-60" /></template>
  </Button>
</template>
