<script setup>
import { computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import StatTiles from "@/components/ui/StatTiles.vue"
import Card from "@/components/ui/Card.vue"
import DataTable from "@/components/ui/DataTable.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"
import { formatINR, formatINRShort } from "@/utils/formatters"

const r = createResource({ url: "frappe_hr_ui.api.get_offcycle", auto: true })
const d = computed(() => r.data || {})
const tiles = computed(() => [
  { label: "Off-cycle total", value: formatINRShort(d.value.total || 0), sub: `${(d.value.rows || []).length} payouts`, icon: "gift", tone: "accent" },
])
const columns = [
  { key: "name", label: "Beneficiary" },
  { key: "type", label: "Type" },
  { key: "amt", label: "Amount", align: "right" },
  { key: "date", label: "Pay date" },
  { key: "st", label: "Status" },
]
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Bonus & off-cycle" subtitle="One-time payouts processed outside the regular run">
      <template #actions><Button variant="solid" theme="gray" label="New payout"><template #prefix><Icon name="plus" :size="15" /></template></Button></template>
    </PageHeader>
    <StatTiles :items="tiles" :cols="4" />
    <Card class="!p-4">
      <DataTable :columns="columns" :rows="d.rows || []" row-key="name" :loading="r.loading" empty-title="No off-cycle payouts" empty-message="Bonuses and incentives appear here.">
        <template #cell-name="{ row }"><div class="flex items-center gap-2.5"><InitialsAvatar :name="row.name" :size="30" /><span class="font-medium">{{ row.name }}</span></div></template>
        <template #cell-type="{ row }"><StatusBadge tone="accent" size="sm" :label="row.type" /></template>
        <template #cell-amt="{ row }"><span class="tnum font-medium">{{ formatINR(row.amt) }}</span></template>
        <template #cell-date="{ row }"><span class="tnum">{{ row.date }}</span></template>
        <template #cell-st="{ row }"><StatusBadge :tone="row.st === 'Approved' ? 'success' : 'warning'" size="sm" dot :label="row.st" /></template>
      </DataTable>
    </Card>
  </div>
</template>
