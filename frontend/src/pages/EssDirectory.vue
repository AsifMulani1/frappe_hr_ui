<script setup>
import { ref, computed } from "vue"
import { Button, createResource, toast } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import Toolbar from "@/components/ui/Toolbar.vue"
import Segmented from "@/components/ui/Segmented.vue"
import DataTable from "@/components/ui/DataTable.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import Drawer from "@/components/ui/Drawer.vue"
import Field from "@/components/ui/Field.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"
import { mailto } from "@/utils/actions"

const r = createResource({ url: "frappe_hr_ui.api.get_directory", auto: true })
const view = ref("grid")
const dept = ref("All")
const q = ref("")
const drawer = ref(null)

const depts = computed(() => ["All", ...(r.data?.departments || [])])
const people = computed(() => {
  let list = r.data?.people || []
  if (dept.value !== "All") list = list.filter((p) => p.department === dept.value)
  if (q.value) {
    const s = q.value.toLowerCase()
    list = list.filter((p) => ((p.employee_name || "") + (p.designation || "") + (p.department || "")).toLowerCase().includes(s))
  }
  return list
})
function copyEmail() {
  const email = drawer.value?.company_email
  if (!email) { toast.error("No email address on file"); return }
  navigator.clipboard?.writeText(email)
  toast.success("Email address copied")
}
const STATUS_TONE = { Active: "success", "On Leave": "warning", "Notice period": "neutral", Probation: "info" }
const columns = [
  { key: "employee_name", label: "Name" },
  { key: "designation", label: "Designation" },
  { key: "department", label: "Department" },
  { key: "location", label: "Location" },
  { key: "manager_name", label: "Reports to" },
  { key: "status", label: "Status" },
]
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="People Directory" :subtitle="`${(r.data?.people || []).length} people across ${(r.data?.departments || []).length} departments`" />

    <AsyncShell :resource="r" loading-text="Loading directory…">
    <Toolbar v-model="q" search="Search by name, team or role…">
      <div class="flex flex-wrap gap-1.5">
        <Button v-for="x in depts.slice(0, 6)" :key="x" @click="dept = x"
          :variant="dept === x ? 'subtle' : 'ghost'" theme="gray" size="sm">{{ x }}</Button>
      </div>
      <template #right><Segmented :options="[{ id: 'grid', label: 'Grid' }, { id: 'list', label: 'List' }]" v-model="view" /></template>
    </Toolbar>

    <div v-if="view === 'grid'" class="grid gap-3.5" style="grid-template-columns: repeat(auto-fill, minmax(248px, 1fr))">
      <Card v-for="p in people" :key="p.name" hover class="cursor-pointer !p-4" @click="drawer = p">
        <div class="flex items-start gap-3">
          <InitialsAvatar :name="p.employee_name" :image="p.image" :size="44" />
          <div class="min-w-0 flex-1">
            <div class="truncate text-base font-medium text-ink-gray-9">{{ p.employee_name }}</div>
            <div class="truncate text-xs text-ink-gray-7">{{ p.designation }}</div>
            <div class="mt-1.5 flex items-center gap-1.5 text-xs text-ink-gray-5"><Icon name="mapPin" :size="12" />{{ p.location }}</div>
          </div>
          <StatusBadge v-if="p.status !== 'Active'" :tone="STATUS_TONE[p.status] || 'neutral'" size="sm" :label="p.status" />
        </div>
        <div class="mt-3 flex gap-1.5 border-t border-outline-gray-1 pt-3">
          <StatusBadge tone="neutral" size="sm" :label="p.department" />
        </div>
      </Card>
    </div>

    <DataTable v-else :columns="columns" :rows="people" row-key="name" :loading="r.loading" @row-click="drawer = $event">
      <template #cell-employee_name="{ row }">
        <div class="flex items-center gap-2.5"><InitialsAvatar :name="row.employee_name" :image="row.image" :size="30" />
          <div><div class="font-medium">{{ row.employee_name }}</div><div class="tnum text-xs text-ink-gray-5">{{ row.employee_number }}</div></div></div>
      </template>
      <template #cell-department="{ row }"><StatusBadge tone="neutral" size="sm" :label="row.department" /></template>
      <template #cell-location="{ row }"><span class="inline-flex items-center gap-1.5 text-ink-gray-7"><Icon name="mapPin" :size="13" />{{ row.location }}</span></template>
      <template #cell-manager_name="{ row }"><span class="text-ink-gray-7">{{ row.manager_name }}</span></template>
      <template #cell-status="{ row }"><StatusBadge :tone="STATUS_TONE[row.status] || 'neutral'" size="sm" dot :label="row.status" /></template>
    </DataTable>
    </AsyncShell>

    <Drawer :open="!!drawer" :width="420" @close="drawer = null">
      <template #head>
        <div v-if="drawer" class="flex items-center gap-3.5">
          <InitialsAvatar :name="drawer.employee_name" :image="drawer.image" :size="52" />
          <div><div class="text-lg font-medium text-ink-gray-9">{{ drawer.employee_name }}</div><div class="text-xs text-ink-gray-5">{{ drawer.designation }}</div></div>
        </div>
      </template>
      <div v-if="drawer" class="grid grid-cols-2 gap-x-5 gap-y-4">
        <Field label="Employee ID" :value="drawer.employee_number" />
        <Field label="Department" :value="drawer.department" />
        <Field label="Location" :value="drawer.location" />
        <Field label="Reports to" :value="drawer.manager_name" />
        <Field label="Status" :value="drawer.status" />
        <Field label="Work email" :value="drawer.company_email" full />
      </div>
      <template #footer>
        <Button variant="outline" theme="gray" label="Copy Email" class="flex-1" @click="copyEmail" />
        <Button variant="solid" theme="blue" label="Send Email" class="flex-1" @click="mailto(drawer?.company_email)" />
      </template>
    </Drawer>
  </div>
</template>
