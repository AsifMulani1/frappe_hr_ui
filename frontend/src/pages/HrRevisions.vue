<script setup>
import { reactive, computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import DataTable from "@/components/ui/DataTable.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"
import FormDrawer from "@/components/ui/FormDrawer.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"
import { formatINRShort } from "@/utils/formatters"
import { useCreate, useLinkOptions } from "@/composables/useDocActions"

const r = createResource({ url: "frappe_hr_ui.api.get_revisions", auto: true })
const rows = computed(() => r.data?.rows || [])

// Create revision (in-app)
const add = useCreate("Salary Structure Assignment", { onDone: () => r.reload(), successLabel: "Revision created" })
const employees = useLinkOptions("Employee")
const salaryStructures = useLinkOptions("Salary Structure")
// Employment state drives state-wise Professional Tax & LWF (india_payroll).
const STATES = ["Andhra Pradesh", "Assam", "Bihar", "Chandigarh", "Chhattisgarh", "Delhi", "Goa", "Gujarat",
  "Haryana", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Meghalaya", "Odisha",
  "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "West Bengal"]
const form = reactive({ employee: "", salary_structure: "", from_date: "", base: "", employment_state: "" })
const fields = computed(() => [
  { key: "employee", label: "Employee", type: "select", options: employees.value, cols: 2 },
  { key: "salary_structure", label: "Salary structure", type: "select", options: salaryStructures.value, cols: 2 },
  { key: "from_date", label: "From date", type: "date", cols: 1 },
  { key: "base", label: "Base", type: "number", placeholder: "Base (optional)", cols: 1 },
  { key: "employment_state", label: "Employment state", type: "select", options: STATES, cols: 2 },
])
function openAdd() {
  Object.assign(form, { employee: "", salary_structure: "", from_date: "", base: "", employment_state: "" })
  add.openDrawer()
}
const columns = [
  { key: "name", label: "Employee" },
  { key: "type", label: "Type" },
  { key: "to", label: "Annual CTC", align: "right" },
  { key: "eff", label: "Effective" },
]
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Revisions & arrears" subtitle="Salary changes and structure assignments">
      <template #actions><Button variant="solid" theme="blue" label="New revision" @click="openAdd"><template #prefix><Icon name="plus" :size="15" /></template></Button></template>
    </PageHeader>
    <AsyncShell :resource="r" loading-text="Loading revisions…">
    <Card class="!p-4">
      <DataTable :columns="columns" :rows="rows" row-key="name" :loading="r.loading" empty-title="No revisions yet">
        <template #cell-name="{ row }"><div class="flex items-center gap-2.5"><InitialsAvatar :name="row.name" :size="30" /><span class="font-medium">{{ row.name }}</span></div></template>
        <template #cell-type="{ row }"><StatusBadge tone="neutral" size="sm" :label="row.type" /></template>
        <template #cell-to="{ row }"><span class="tnum font-medium">{{ formatINRShort(row.to) }}</span></template>
        <template #cell-eff="{ row }"><span class="tnum">{{ row.eff }}</span></template>
      </DataTable>
    </Card>
    </AsyncShell>

    <FormDrawer :open="add.open" title="New revision" subtitle="Assign a salary structure"
      :fields="fields" v-model="form" :loading="add.create.loading" submit-label="Create revision"
      @close="add.open = false" @submit="add.submit(form, ['employee', 'salary_structure', 'from_date'])" />
  </div>
</template>
