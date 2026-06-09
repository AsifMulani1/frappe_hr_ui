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

const r = createResource({ url: "frappe_hr_ui.api.get_offers", auto: true })
const d = computed(() => r.data || {})
const TONE = { Accepted: "success", "Awaiting Response": "warning", Rejected: "danger", "Offer Sent": "warning" }
const tiles = computed(() => {
  const s = d.value.stats || {}
  return [
    { label: "Offers sent", value: s.sent ?? 0, sub: "in flight", icon: "file", tone: "accent" },
    { label: "Accepted", value: s.accepted ?? 0, sub: "joined/joining", icon: "check", tone: "success" },
  ]
})
const columns = [
  { key: "applicant_name", label: "Candidate" },
  { key: "designation", label: "Role" },
  { key: "sent", label: "Sent" },
  { key: "status", label: "Status" },
]
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Offer management" :subtitle="`${(d.offers || []).length} offers`">
      <template #actions><Button variant="solid" theme="gray" label="Create offer"><template #prefix><Icon name="plus" :size="15" /></template></Button></template>
    </PageHeader>
    <StatTiles :items="tiles" :cols="4" />
    <Card class="!p-4">
      <DataTable :columns="columns" :rows="d.offers || []" row-key="name" :loading="r.loading" empty-title="No offers yet">
        <template #cell-applicant_name="{ row }"><div class="flex items-center gap-2.5"><InitialsAvatar :name="row.applicant_name" :size="30" /><span class="font-medium">{{ row.applicant_name }}</span></div></template>
        <template #cell-designation="{ row }"><span class="text-ink-gray-7">{{ row.designation }}</span></template>
        <template #cell-sent="{ row }"><span class="tnum">{{ row.sent }}</span></template>
        <template #cell-status="{ row }"><StatusBadge :tone="TONE[row.status] || 'neutral'" size="sm" dot :label="row.status" /></template>
      </DataTable>
    </Card>
  </div>
</template>
