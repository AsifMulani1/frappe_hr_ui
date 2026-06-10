<script setup>
import { ref, computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import Toolbar from "@/components/ui/Toolbar.vue"
import FilterChip from "@/components/ui/FilterChip.vue"
import DataTable from "@/components/ui/DataTable.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import Icon from "@/components/ui/Icon.vue"
import ReportDrawer from "@/components/ui/ReportDrawer.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"

const r = createResource({ url: "frappe_hr_ui.api.get_challan", auto: true })
const rows = computed(() => r.data?.rows || [])
const reportOpen = ref(false)
const columns = [
  { key: "ref", label: "Reference" },
  { key: "type", label: "Type" },
  { key: "period", label: "Period" },
  { key: "amt", label: "Amount", align: "right" },
  { key: "due", label: "Due" },
  { key: "st", label: "Status" },
]
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Challan & returns" subtitle="All statutory challans and filing references in one place">
      <template #actions><Button variant="solid" theme="blue" label="Generate challan" @click="reportOpen = true"><template #prefix><Icon name="plus" :size="15" /></template></Button></template>
    </PageHeader>
    <AsyncShell :resource="r" loading-text="Loading challans…">
    <Card class="!p-4">
      <Toolbar search="Search challans…"><FilterChip label="Type" /><FilterChip label="Status" active /></Toolbar>
      <DataTable :columns="columns" :rows="rows" row-key="ref" :loading="r.loading" empty-title="No challans generated">
        <template #cell-ref="{ row }"><span class="tnum font-medium">{{ row.ref }}</span></template>
        <template #cell-period="{ row }"><span class="text-ink-gray-7">{{ row.period }}</span></template>
        <template #cell-amt="{ row }"><span class="tnum font-medium">{{ row.amt }}</span></template>
        <template #cell-due="{ row }"><span class="tnum">{{ row.due }}</span></template>
        <template #cell-st="{ row }"><StatusBadge :tone="row.tone" size="sm" dot :label="row.st" /></template>
      </DataTable>
    </Card>
    </AsyncShell>

    <ReportDrawer :open="reportOpen" report="Salary Register" title="Statutory deductions" @close="reportOpen = false" />
  </div>
</template>
