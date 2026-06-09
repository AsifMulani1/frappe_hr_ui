<script setup>
import { computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import StatTiles from "@/components/ui/StatTiles.vue"
import Card from "@/components/ui/Card.vue"
import DataTable from "@/components/ui/DataTable.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import Icon from "@/components/ui/Icon.vue"

const r = createResource({ url: "frappe_hr_ui.api.get_biometric", auto: true })
const d = computed(() => r.data || {})
const tiles = computed(() => [
  { label: "Devices online", value: `${d.value.online ?? 0} / ${(d.value.devices || []).length}`, sub: "across sites", icon: "dot", tone: "success" },
  { label: "Punches today", value: d.value.total_punches ?? 0, sub: "all sites", icon: "login", tone: "accent" },
])
const columns = [
  { key: "id", label: "Device" },
  { key: "loc", label: "Location" },
  { key: "status", label: "Status" },
  { key: "last", label: "Last sync" },
  { key: "punches", label: "Punches today", align: "right" },
]
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Biometric sync" subtitle="Device health and punch synchronisation across offices">
      <template #actions><Button variant="solid" theme="gray" label="Force sync"><template #prefix><Icon name="download" :size="15" /></template></Button></template>
    </PageHeader>
    <StatTiles :items="tiles" :cols="4" />
    <Card class="!p-4">
      <DataTable :columns="columns" :rows="d.devices || []" row-key="id" :loading="r.loading" empty-title="No devices configured" empty-message="Branch-level punch devices appear here.">
        <template #cell-id="{ row }"><span class="tnum font-medium">{{ row.id }}</span></template>
        <template #cell-loc="{ row }"><span class="inline-flex items-center gap-1.5 text-ink-gray-7"><Icon name="mapPin" :size="13" />{{ row.loc }}</span></template>
        <template #cell-status="{ row }"><StatusBadge :tone="row.tone" size="sm" dot :label="row.status" /></template>
        <template #cell-last="{ row }"><span class="text-ink-gray-7">{{ row.last }}</span></template>
        <template #cell-punches="{ row }"><span class="tnum">{{ row.punches }}</span></template>
      </DataTable>
    </Card>
  </div>
</template>
