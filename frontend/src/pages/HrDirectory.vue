<script setup>
import { ref, reactive, computed } from "vue"
import { useRouter } from "vue-router"
import { Button, FormControl, createResource, toast } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import StatTiles from "@/components/ui/StatTiles.vue"
import Card from "@/components/ui/Card.vue"
import Toolbar from "@/components/ui/Toolbar.vue"
import FilterChip from "@/components/ui/FilterChip.vue"
import DataTable from "@/components/ui/DataTable.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import Drawer from "@/components/ui/Drawer.vue"
import DateField from "@/components/ui/DateField.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"
import { formatINRShort } from "@/utils/formatters"

const router = useRouter()
const r = createResource({ url: "frappe_hr_ui.api.get_hr_directory", auto: true })
const q = ref("")
const d = computed(() => r.data || {})

// --- Add employee (in-app) ---
const open = ref(false)
const opts = createResource({ url: "frappe_hr_ui.api.get_new_employee_options" })
const form = reactive({
  first_name: "", last_name: "", gender: "", date_of_birth: "",
  date_of_joining: "", company: "", designation: "", department: "", company_email: "",
})
function openAdd() {
  Object.assign(form, {
    first_name: "", last_name: "", gender: "", date_of_birth: "",
    date_of_joining: "", company: "", designation: "", department: "", company_email: "",
  })
  if (!opts.data) opts.fetch()
  open.value = true
}
const create = createResource({
  url: "frappe_hr_ui.api.create_employee",
  onSuccess(res) {
    toast.success(`${res.employee_name} added`)
    open.value = false
    r.reload()
  },
  onError(e) { toast.error(e?.messages?.[0] || "Couldn't create employee") },
})
function submitEmployee() {
  if (!form.first_name || !form.gender || !form.date_of_birth || !form.date_of_joining) {
    toast.error("Fill in name, gender, date of birth and joining date")
    return
  }
  create.submit({ ...form })
}
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
    <PageHeader title="Employee Directory" :subtitle="`${(d.people || []).length} employees · manage records, status and compensation`">
      <template #actions>
        <Button variant="outline" theme="gray" label="Import (CSV)" @click="router.push({ name: 'SetupWizard', query: { step: 'employees' } })"><template #prefix><Icon name="download" :size="15" /></template></Button>
        <Button variant="solid" theme="blue" label="Add Employee" @click="openAdd"><template #prefix><Icon name="plus" :size="15" /></template></Button>
      </template>
    </PageHeader>
    <AsyncShell :resource="r" loading-text="Loading directory…">
    <StatTiles :items="tiles" :cols="4" />
    <Card :pad="false">
      <div class="p-4">
        <Toolbar v-model="q" search="Search employees…"><FilterChip label="Department" /><FilterChip label="Status" /><FilterChip label="Type" /></Toolbar>
        <DataTable :columns="columns" :rows="people" row-key="name" selectable :loading="r.loading" @row-click="router.push({ name: 'HrEmployee360', query: { id: $event.name } })">
          <template #cell-employee_name="{ row }">
            <div class="flex items-center gap-2.5"><InitialsAvatar :name="row.employee_name" :image="row.image" :size="32" />
              <div><div class="font-medium">{{ row.employee_name }}</div><div class="tnum text-xs text-ink-gray-5">{{ row.employee_number }}</div></div></div>
          </template>
          <template #cell-department="{ row }"><StatusBadge tone="neutral" size="sm" :label="(row.department || '').split(' - ')[0]" /></template>
          <template #cell-location="{ row }"><span class="text-ink-gray-7">{{ row.location }}</span></template>
          <template #cell-doj="{ row }"><span class="tnum text-ink-gray-7">{{ row.doj }}</span></template>
          <template #cell-ctc="{ row }"><span class="tnum">{{ formatINRShort(row.ctc) }}</span></template>
          <template #cell-status="{ row }"><StatusBadge :tone="STATUS_TONE[row.status] || 'neutral'" size="sm" dot :label="row.status" /></template>
        </DataTable>
      </div>
    </Card>
    </AsyncShell>

    <Drawer :open="open" title="Add Employee" subtitle="Create a new employee record" :width="520" @close="open = false">
      <div class="flex flex-col gap-4">
        <div class="grid grid-cols-2 gap-3">
          <FormControl type="text" label="First name" v-model="form.first_name" />
          <FormControl type="text" label="Last name" v-model="form.last_name" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <FormControl type="select" label="Gender" :options="opts.data?.genders || []" v-model="form.gender" />
          <DateField label="Date of birth" v-model="form.date_of_birth" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <DateField label="Date of joining" v-model="form.date_of_joining" />
          <FormControl type="select" label="Company" :options="opts.data?.companies || []" v-model="form.company" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <FormControl type="select" label="Designation" :options="['', ...(opts.data?.designations || [])]" v-model="form.designation" />
          <FormControl type="select" label="Department" :options="['', ...(opts.data?.departments || [])]" v-model="form.department" />
        </div>
        <FormControl type="email" label="Work email" v-model="form.company_email" />
      </div>
      <template #footer>
        <Button variant="ghost" label="Cancel" @click="open = false" />
        <Button variant="solid" theme="blue" label="Create Employee" :loading="create.loading" @click="submitEmployee" />
      </template>
    </Drawer>
  </div>
</template>
