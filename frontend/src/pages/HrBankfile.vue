<script setup>
import { computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import StatTiles from "@/components/ui/StatTiles.vue"
import Card from "@/components/ui/Card.vue"
import DataTable from "@/components/ui/DataTable.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import Icon from "@/components/ui/Icon.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"
import { formatINR, formatINRShort } from "@/utils/formatters"
import { downloadCSV } from "@/utils/actions"

const r = createResource({ url: "frappe_hr_ui.api.get_bankfile", auto: true })
const d = computed(() => r.data || {})
const tiles = computed(() => [
  { label: "Total disbursement", value: formatINRShort(d.value.total || 0), sub: `${d.value.ready ?? 0} employees`, icon: "rupee", tone: "accent" },
  { label: "Banks", value: (d.value.banks || []).length, sub: "consolidated files", icon: "card", tone: "neutral" },
])
const columns = [
  { key: "bank", label: "Bank" },
  { key: "emp", label: "Employees", align: "right" },
  { key: "mode", label: "Mode" },
  { key: "amt", label: "Amount", align: "right" },
  { key: "st", label: "Status" },
]
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Bank Disbursement" subtitle="Generate bank advice files for net salary">
      <template #actions><Button variant="solid" theme="blue" :label="`Disburse ${formatINRShort(d.total || 0)}`" @click="downloadCSV('bank-disbursement', columns, d.banks)"><template #prefix><Icon name="card" :size="15" /></template></Button></template>
    </PageHeader>
    <AsyncShell :resource="r" loading-text="Loading disbursement…">
    <StatTiles :items="tiles" :cols="4" />
    <Card class="!p-4">
      <DataTable :columns="columns" :rows="d.banks || []" row-key="bank" :loading="r.loading">
        <template #cell-bank="{ row }"><div class="flex items-center gap-2.5"><div class="flex h-[30px] w-[30px] items-center justify-center rounded-md bg-surface-gray-2 text-ink-gray-7"><Icon name="card" :size="15" /></div><span class="font-medium">{{ row.bank }}</span></div></template>
        <template #cell-emp="{ row }"><span class="tnum">{{ row.emp }}</span></template>
        <template #cell-mode="{ row }"><StatusBadge tone="neutral" size="sm" :label="row.mode" /></template>
        <template #cell-amt="{ row }"><span class="tnum font-medium">{{ formatINR(row.amt) }}</span></template>
        <template #cell-st="{ row }"><StatusBadge :tone="row.tone" size="sm" dot :label="row.st" /></template>
      </DataTable>
    </Card>
    </AsyncShell>
  </div>
</template>
