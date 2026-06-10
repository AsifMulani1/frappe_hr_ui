<script setup>
// Consistent loading / error / no-employee gate for data screens.
// Wrap a page's body in this so a failed fetch or an unlinked user is never
// shown as fabricated "healthy" empty data.
import { Button } from "frappe-ui"
import Icon from "./Icon.vue"

defineProps({
  resource: { type: Object, required: true },
  hasEmployee: { type: Boolean, default: true },
  loadingText: { type: String, default: "Loading…" },
})
</script>

<template>
  <div v-if="resource.loading && !resource.data" class="flex h-[55vh] items-center justify-center text-ink-gray-5">
    <div class="flex items-center gap-2 text-[13px]"><Icon name="dot" :size="18" class="animate-pulse" /> {{ loadingText }}</div>
  </div>

  <div v-else-if="resource.error" class="flex h-[55vh] flex-col items-center justify-center gap-2 text-center">
    <div class="flex h-10 w-10 items-center justify-center rounded-full bg-red-50 text-red-600"><Icon name="x" :size="20" /></div>
    <div class="text-[15px] font-medium text-ink-gray-8">Couldn't load this page</div>
    <div class="max-w-md text-[13px] text-ink-gray-5">{{ resource.error.messages?.[0] || resource.error.message || "Something went wrong. Please try again." }}</div>
    <Button class="mt-2" variant="subtle" theme="gray" label="Retry" @click="resource.reload()" />
  </div>

  <div v-else-if="!hasEmployee" class="flex h-[55vh] flex-col items-center justify-center gap-2 text-center">
    <Icon name="user" :size="26" class="text-ink-gray-4" />
    <div class="text-[15px] font-medium text-ink-gray-8">No employee record linked</div>
    <div class="max-w-md text-[13px] text-ink-gray-5">
      This user isn't linked to an Employee. Sign in as an employee (e.g. aarav.mehta@frappe.io) to use self-service.
    </div>
  </div>

  <slot v-else />
</template>
