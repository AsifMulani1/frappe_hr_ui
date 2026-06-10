<script setup>
// In-app report viewer: runs a standard Frappe report server-side and shows the
// result in a table (with CSV export) — no Desk redirect.
import { watch, computed } from "vue"
import { Button, createResource } from "frappe-ui"
import Drawer from "./Drawer.vue"
import EmptyState from "./EmptyState.vue"
import { downloadCSV } from "@/utils/actions"

const props = defineProps({
  open: Boolean,
  report: String,
  title: String,
  filters: { type: Object, default: null },
})
const emit = defineEmits(["close"])

const data = createResource({ url: "frappe_hr_ui.api.get_report_data" })
watch(
  () => [props.open, props.report],
  ([open, report]) => {
    if (open && report) {
      data.fetch({ report_name: report, filters: props.filters ? JSON.stringify(props.filters) : undefined })
    }
  },
  { immediate: true }
)
const columns = computed(() => data.data?.columns || [])
const rows = computed(() => data.data?.rows || [])
</script>

<template>
  <Drawer :open="open" :title="title || report" subtitle="Report" :width="820" @close="emit('close')">
    <template #head>
      <div class="flex w-full items-center justify-between gap-3">
        <div>
          <div class="text-[15.5px] font-medium text-ink-gray-9">{{ title || report }}</div>
          <div class="mt-0.5 text-[12.5px] text-ink-gray-5">{{ rows.length }} rows</div>
        </div>
        <Button v-if="rows.length" variant="subtle" theme="gray" size="sm" label="Download CSV"
          @click="downloadCSV(report, columns, rows)" />
      </div>
    </template>

    <div v-if="data.loading" class="py-10 text-center text-[13px] text-ink-gray-5">Running report…</div>
    <EmptyState v-else-if="data.data?.error" icon="alert" title="Couldn't run report" :message="data.data.error" compact />
    <EmptyState v-else-if="!rows.length" icon="inbox" title="No data" message="This report returned no rows for the current period." compact />
    <div v-else class="overflow-x-auto">
      <table class="w-full border-collapse text-[12.5px]">
        <thead>
          <tr class="border-b border-outline-gray-2 text-left text-ink-gray-5">
            <th v-for="c in columns" :key="c.key" class="whitespace-nowrap px-2.5 py-2 font-medium">{{ c.label }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, i) in rows" :key="i" class="border-b border-outline-gray-1">
            <td v-for="c in columns" :key="c.key" class="whitespace-nowrap px-2.5 py-1.5 text-ink-gray-8">{{ row[c.key] }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </Drawer>
</template>
