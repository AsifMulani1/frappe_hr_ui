<script setup>
import { ref, reactive, computed, watch } from "vue"
import { Button, createResource, toast, Select, TextInput } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import DataTable from "@/components/ui/DataTable.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import AmountRow from "@/components/ui/AmountRow.vue"
import Icon from "@/components/ui/Icon.vue"
import FormDrawer from "@/components/ui/FormDrawer.vue"
import Drawer from "@/components/ui/Drawer.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"
import { useCreate } from "@/composables/useDocActions"

const r = createResource({ url: "frappe_hr_ui.api.get_salary_structure", auto: true })
const d = computed(() => r.data || {})

// ---- Bulk-assign compensation to employees who don't have a structure yet ----
const STATES = ["Andhra Pradesh", "Assam", "Bihar", "Chandigarh", "Chhattisgarh", "Delhi", "Goa", "Gujarat",
  "Haryana", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Meghalaya", "Odisha",
  "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "West Bengal"]
const stateOpts = STATES.map((s) => ({ label: s, value: s }))
const bulkOpen = ref(false)
const bulkStructure = ref("")
const defaultState = ref("Maharashtra")
const bulkRows = ref([])
const structOpts = ref([])
const unassigned = createResource({ url: "frappe_hr_ui.api.get_unassigned_employees" })
async function openBulk() {
  const res = await unassigned.fetch()
  structOpts.value = (res?.structures || []).map((s) => ({ label: s, value: s }))
  bulkStructure.value = res?.default_structure || ""
  bulkRows.value = (res?.employees || []).map((e) => ({ ...e, base: "", employment_state: defaultState.value }))
  bulkOpen.value = true
}
watch(defaultState, (s) => bulkRows.value.forEach((row) => { row.employment_state = s }))
const bulkCount = computed(() => bulkRows.value.filter((row) => row.base).length)
const assignRes = createResource({
  url: "frappe_hr_ui.api.bulk_assign_salary",
  onSuccess(res) {
    const m = `${res.assigned} assigned${res.errors?.length ? `, ${res.errors.length} failed` : ""}`
    res.errors?.length ? toast.warning(m) : toast.success(m)
    bulkOpen.value = false
    r.reload()
  },
  onError(e) { toast.error(e?.messages?.[0] || "Couldn't assign compensation") },
})
function doBulkAssign() {
  if (!bulkStructure.value) { toast.error("Pick a salary structure"); return }
  const rows = bulkRows.value.filter((row) => row.base)
  if (!rows.length) { toast.error("Enter a base salary for at least one employee"); return }
  assignRes.submit({
    salary_structure: bulkStructure.value,
    rows: JSON.stringify(rows.map((row) => ({ employee: row.employee, base: row.base, employment_state: row.employment_state }))),
  })
}

// Create component (in-app)
const add = useCreate("Salary Component", { onDone: () => r.reload(), successLabel: "Component created" })
const form = reactive({ salary_component: "", salary_component_abbr: "", type: "Earning" })
const fields = computed(() => [
  { key: "salary_component", label: "Salary component", type: "text", placeholder: "e.g. Internet Allowance", cols: 2 },
  { key: "salary_component_abbr", label: "Abbreviation", type: "text", placeholder: "Abbr", cols: 1 },
  { key: "type", label: "Type", type: "select", options: ["Earning", "Deduction"], cols: 1 },
])
function openAdd() {
  Object.assign(form, { salary_component: "", salary_component_abbr: "", type: "Earning" })
  add.openDrawer()
}
const columns = [
  { key: "name", label: "Component" },
  { key: "type", label: "Type" },
  { key: "formula", label: "Calculation" },
]
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Salary Structure" :subtitle="d.structure || 'Standard structure'">
      <template #actions>
        <Button variant="outline" theme="gray" label="Assign to Employees" @click="openBulk"><template #prefix><Icon name="users" :size="15" /></template></Button>
        <Button variant="solid" theme="blue" label="New Component" @click="openAdd"><template #prefix><Icon name="plus" :size="15" /></template></Button>
      </template>
    </PageHeader>
    <AsyncShell :resource="r" loading-text="Loading salary structure…">
    <div class="grid items-start gap-5" style="grid-template-columns: minmax(0,1fr) 320px">
      <Card class="!p-4">
        <DataTable :columns="columns" :rows="d.components || []" row-key="name" :loading="r.loading" empty-title="No structure found">
          <template #cell-name="{ row }"><span class="font-medium">{{ row.name }}</span></template>
          <template #cell-type="{ row }"><StatusBadge :tone="row.type === 'Earning' ? 'success' : 'danger'" size="sm" :label="row.type" /></template>
          <template #cell-formula="{ row }"><span class="tnum text-ink-gray-6">{{ row.formula }}</span></template>
        </DataTable>
      </Card>
      <Card>
        <CardHeader title="Structure Summary" />
        <AmountRow label="Earning components" :value="d.earnings ?? 0" />
        <AmountRow label="Deduction components" :value="d.deductions ?? 0" />
        <AmountRow label="Employees assigned" :value="d.employees ?? 0" :border="false" />
      </Card>
    </div>
    </AsyncShell>

    <FormDrawer :open="add.open" title="New Component" subtitle="Add a salary component"
      :fields="fields" v-model="form" :loading="add.create.loading" submit-label="Create Component"
      @close="add.open = false" @submit="add.submit(form, ['salary_component', 'salary_component_abbr', 'type'])" />

    <Drawer :open="bulkOpen" title="Assign Compensation" subtitle="Set structure, base & state for employees who don't have one yet" :width="680" @close="bulkOpen = false">
      <div class="flex flex-col gap-4">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="mb-1.5 block text-xs text-ink-gray-5">Salary structure</label>
            <Select v-model="bulkStructure" :options="structOpts" placeholder="Pick structure" />
          </div>
          <div>
            <label class="mb-1.5 block text-xs text-ink-gray-5">Default state (applies to all)</label>
            <Select v-model="defaultState" :options="stateOpts" />
          </div>
        </div>
        <div v-if="!bulkRows.length" class="rounded-md border border-outline-gray-1 py-8 text-center text-sm text-ink-gray-5">
          Everyone already has a salary structure assigned. 🎉
        </div>
        <div v-else class="overflow-hidden rounded-md border border-outline-gray-1">
          <div class="grid grid-cols-[1fr_120px_160px] gap-2 border-b border-outline-gray-1 bg-surface-gray-1 px-3 py-2 text-xs font-medium text-ink-gray-5">
            <span>Employee</span><span>Base (₹/month)</span><span>Employment state</span>
          </div>
          <div class="max-h-[44vh] overflow-y-auto">
            <div v-for="row in bulkRows" :key="row.employee" class="grid grid-cols-[1fr_120px_160px] items-center gap-2 border-b border-outline-gray-1 px-3 py-2 last:border-b-0">
              <div class="min-w-0">
                <div class="truncate text-sm font-medium text-ink-gray-9">{{ row.employee_name }}</div>
                <div class="truncate text-2xs text-ink-gray-5">{{ row.designation }} · {{ row.department }}</div>
              </div>
              <TextInput type="number" size="sm" v-model="row.base" placeholder="0" />
              <Select size="sm" v-model="row.employment_state" :options="stateOpts" />
            </div>
          </div>
        </div>
        <p class="text-xs text-ink-gray-4">Only rows with a base salary are assigned. Employment state drives Professional Tax & LWF.</p>
      </div>
      <template #footer>
        <Button variant="ghost" label="Cancel" @click="bulkOpen = false" />
        <Button variant="solid" theme="blue" :label="`Assign${bulkCount ? ' ' + bulkCount : ''}`" :loading="assignRes.loading" :disabled="!bulkCount" @click="doBulkAssign" />
      </template>
    </Drawer>
  </div>
</template>
