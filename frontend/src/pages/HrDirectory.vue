<script setup>
import { ref, computed } from "vue"
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
import { formatINRShort } from "@/utils/formatters"

const router = useRouter()
const r = createResource({ url: "frappe_hr_ui.api.get_hr_directory", auto: true })
const q = ref("")
const d = computed(() => r.data || {})
const people = computed(() => {
  let list = d.value.people || []
  if (q.value) { const s = q.value.toLowerCase(); list = list.filter((p) => (p.employee_name + p.designation + (p.department || "")).toLowerCase().includes(s)) }
  return list
})
const STATUS_TONE = { Active: "success", "On Leave": "warning", "Notice period": "neutral", Probation: "info" }
const tiles = computed(() => {
  const s = d.value.stats || {}
  return [
    { label: "Total employees", value: s.total ?? 0, sub: "active", icon: "users", tone: "accent" },
    { label: "On probation", value: s.probation ?? 0, sub: "confirming", icon: "clock", tone: "warning" },
    { label: "On notice", value: s.notice ?? 0, sub: "exits ahead", icon: "logout", tone: "neutral" },
  ]
})
const columns = [
  { key: "employee_name", label: "Employee" },
  { key: "designation", label: "Designation" },
  { key: "department", label: "Department" },
  { key: "location", label: "Location" },
  { key: "doj", label: "Joined" },
  { key: "ctc", label: "CTC", align: "right" },
  { key: "status", label: "Status" },
]
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Employee directory" :subtitle="`${(d.people || []).length} employees · manage records, status and compensation`">
      <template #actions><Button variant="solid" theme="gray" label="Add employee"><template #prefix><Icon name="plus" :size="15" /></template></Button></template>
    </PageHeader>
    <StatTiles :items="tiles" :cols="4" />
    <Card :pad="false">
      <div class="p-4">
        <Toolbar v-model="q" search="Search employees…"><FilterChip label="Department" /><FilterChip label="Status" /><FilterChip label="Type" /></Toolbar>
        <DataTable :columns="columns" :rows="people" row-key="name" selectable :loading="r.loading" @row-click="router.push({ name: 'HrEmployee360', query: { id: $event.name } })">
          <template #cell-employee_name="{ row }">
            <div class="flex items-center gap-2.5"><InitialsAvatar :name="row.employee_name" :image="row.image" :size="32" />
              <div><div class="font-medium">{{ row.employee_name }}</div><div class="tnum text-[11.5px] text-ink-gray-5">{{ row.employee_number }}</div></div></div>
          </template>
          <template #cell-department="{ row }"><StatusBadge tone="neutral" size="sm" :label="(row.department || '').split(' - ')[0]" /></template>
          <template #cell-location="{ row }"><span class="text-ink-gray-7">{{ row.location }}</span></template>
          <template #cell-doj="{ row }"><span class="tnum text-ink-gray-7">{{ row.doj }}</span></template>
          <template #cell-ctc="{ row }"><span class="tnum">{{ formatINRShort(row.ctc) }}</span></template>
          <template #cell-status="{ row }"><StatusBadge :tone="STATUS_TONE[row.status] || 'neutral'" size="sm" dot :label="row.status" /></template>
        </DataTable>
      </div>
    </Card>
  </div>
</template>
