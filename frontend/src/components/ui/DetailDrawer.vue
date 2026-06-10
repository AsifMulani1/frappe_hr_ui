<script setup>
// Read-only in-app detail viewer for a Frappe document (replaces opening Desk).
import { watch } from "vue"
import { createResource } from "frappe-ui"
import Drawer from "./Drawer.vue"
import StatusBadge from "./StatusBadge.vue"

const props = defineProps({
  open: Boolean,
  doctype: String,
  name: String,
  title: String,
})
const emit = defineEmits(["close"])

const detail = createResource({ url: "frappe_hr_ui.api.get_doc_detail" })
watch(
  () => [props.open, props.doctype, props.name],
  ([open, dt, nm]) => {
    if (open && dt && nm) detail.fetch({ doctype: dt, name: nm })
  },
  { immediate: true }
)
</script>

<template>
  <Drawer :open="open" :title="title || name" :subtitle="doctype" :width="460" @close="emit('close')">
    <div v-if="detail.loading" class="py-10 text-center text-[13px] text-ink-gray-5">Loading…</div>
    <div v-else-if="detail.data" class="flex flex-col">
      <div class="mb-3 flex items-center gap-2">
        <span class="text-[15px] font-medium text-ink-gray-9">{{ detail.data.title || detail.data.name }}</span>
        <StatusBadge v-if="detail.data.status" tone="neutral" size="sm" :label="String(detail.data.status)" />
      </div>
      <div
        v-for="(f, i) in detail.data.fields"
        :key="i"
        class="flex items-start justify-between gap-4 border-b border-outline-gray-1 py-2.5 last:border-b-0"
      >
        <span class="text-[12.5px] text-ink-gray-5">{{ f.label }}</span>
        <span class="text-right text-[13px] font-medium text-ink-gray-9">{{ f.value }}</span>
      </div>
    </div>
    <div v-else class="py-10 text-center text-[13px] text-ink-gray-5">Couldn't load details.</div>
  </Drawer>
</template>
