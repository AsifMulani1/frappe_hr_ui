<script setup>
import { computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import StatTiles from "@/components/ui/StatTiles.vue"
import Card from "@/components/ui/Card.vue"
import Toolbar from "@/components/ui/Toolbar.vue"
import FilterChip from "@/components/ui/FilterChip.vue"
import DataTable from "@/components/ui/DataTable.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"

const r = createResource({ url: "frappe_hr_ui.api.get_team_attendance", auto: true })
const d = computed(() => r.data || {})
const ATT_TONE = { Present: "success", "On Leave": "warning", WFH: "accent", "Not in": "neutral" }
const tiles = computed(() => {
  const s = d.value.summary || {}
  return [
    { label: "Present now", value: `${s.present ?? 0} / ${s.total ?? 0}`, sub: "team", icon: "calcheck", tone: "success" },
    { label: "Team size", value: s.total ?? 0, sub: "direct reports", icon: "users", tone: "accent" },
  ]
})
const columns = [
  { key: "employee_name", label: "Employee" },
  { key: "att", label: "Today" },
  { key: "in", label: "Check in", align: "right" },
  { key: "rate", label: "Month %", align: "right" },
]
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Team attendance" subtitle="Live status and month trends for your reports">
      <template #actions><Button variant="outline" theme="gray" label="Export"><template #prefix><Icon name="download" :size="15" /></template></Button></template>
    </PageHeader>
    <StatTiles :items="tiles" :cols="4" />
    <Card :pad="false">
      <div class="p-4">
        <Toolbar search="Search team…"><FilterChip label="Status" /><FilterChip label="Location" /></Toolbar>
        <DataTable :columns="columns" :rows="d.team || []" row-key="name" :loading="r.loading">
          <template #cell-employee_name="{ row }">
            <div class="flex items-center gap-2.5"><InitialsAvatar :name="row.employee_name" :size="30" />
              <div><div class="font-medium">{{ row.employee_name }}</div><div class="text-[11.5px] text-ink-gray-5">{{ row.designation }}</div></div></div>
          </template>
          <template #cell-att="{ row }"><StatusBadge :tone="ATT_TONE[row.today.att] || 'neutral'" size="sm" dot :label="row.today.att" /></template>
          <template #cell-in="{ row }"><span class="tnum">{{ row.today.in }}</span></template>
          <template #cell-rate="{ row }"><span class="tnum font-medium">{{ row.rate }}%</span></template>
        </DataTable>
      </div>
    </Card>
  </div>
</template>
