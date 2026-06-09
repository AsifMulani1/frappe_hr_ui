<script setup>
import { computed } from "vue"
import { useRouter } from "vue-router"
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

const router = useRouter()
const r = createResource({ url: "frappe_hr_ui.api.get_hr_attendance", auto: true })
const d = computed(() => r.data || {})
const ATT_TONE = { Present: "success", WFH: "accent", "On Leave": "warning", "Not in": "neutral" }
const tiles = computed(() => {
  const s = d.value.summary || {}
  return [
    { label: "Present", value: s.present ?? 0, sub: `of ${s.total ?? 0}`, icon: "calcheck", tone: "success" },
    { label: "WFH", value: s.wfh ?? 0, sub: "remote", icon: "home", tone: "accent" },
    { label: "On leave", value: s.leave ?? 0, sub: "today", icon: "calendar", tone: "warning" },
    { label: "Not in", value: s.absent ?? 0, sub: "no punch", icon: "x", tone: "danger" },
  ]
})
const columns = [
  { key: "employee_name", label: "Employee" },
  { key: "att", label: "Status" },
  { key: "inT", label: "Check in", align: "right" },
  { key: "department", label: "Department" },
]
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Attendance workspace" subtitle="Company-wide attendance today">
      <template #actions><Button variant="solid" theme="gray" label="Regularizations" @click="router.push({ name: 'HrRegularize' })"><template #prefix><Icon name="inbox" :size="15" /></template></Button></template>
    </PageHeader>
    <StatTiles :items="tiles" :cols="4" />
    <Card class="!p-4">
      <Toolbar search="Search employees…"><FilterChip label="Department" /><FilterChip label="Status" /><FilterChip label="Location" /></Toolbar>
      <DataTable :columns="columns" :rows="d.rows || []" row-key="name" selectable :loading="r.loading">
        <template #cell-employee_name="{ row }"><div class="flex items-center gap-2.5"><InitialsAvatar :name="row.employee_name" :image="row.image" :size="30" /><span class="font-medium">{{ row.employee_name }}</span></div></template>
        <template #cell-att="{ row }"><StatusBadge :tone="ATT_TONE[row.att] || 'neutral'" size="sm" dot :label="row.att" /></template>
        <template #cell-inT="{ row }"><span class="tnum">{{ row.inT }}</span></template>
        <template #cell-department="{ row }"><span class="text-ink-gray-7">{{ row.department }}</span></template>
      </DataTable>
    </Card>
  </div>
</template>
