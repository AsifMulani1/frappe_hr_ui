<script setup>
import { reactive, computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import StatTiles from "@/components/ui/StatTiles.vue"
import Card from "@/components/ui/Card.vue"
import DataTable from "@/components/ui/DataTable.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"
import FormDrawer from "@/components/ui/FormDrawer.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"
import { formatINR, formatINRShort } from "@/utils/formatters"
import { useCreate, useLinkOptions } from "@/composables/useDocActions"

const r = createResource({ url: "frappe_hr_ui.api.get_offcycle", auto: true })
const d = computed(() => r.data || {})

// Create payout (in-app)
const add = useCreate("Additional Salary", { onDone: () => r.reload(), successLabel: "Payout created" })
const employees = useLinkOptions("Employee")
const salaryComponents = useLinkOptions("Salary Component")
const form = reactive({ employee: "", salary_component: "", amount: "", payroll_date: "" })
const fields = computed(() => [
  { key: "employee", label: "Employee", type: "select", options: employees.value, cols: 2 },
  { key: "salary_component", label: "Salary component", type: "select", options: salaryComponents.value, cols: 2 },
  { key: "amount", label: "Amount", type: "number", placeholder: "₹", cols: 1 },
  { key: "payroll_date", label: "Payroll date", type: "date", cols: 1 },
])
function openAdd() {
  Object.assign(form, { employee: "", salary_component: "", amount: "", payroll_date: "" })
  add.openDrawer()
}
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
      <template #actions><Button variant="solid" theme="blue" label="New payout" @click="openAdd"><template #prefix><Icon name="plus" :size="15" /></template></Button></template>
    </PageHeader>
    <AsyncShell :resource="r" loading-text="Loading payouts…">
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
    </AsyncShell>

    <FormDrawer :open="add.open" title="New payout" subtitle="One-time off-cycle payout"
      :fields="fields" v-model="form" :loading="add.create.loading" submit-label="Create payout"
      @close="add.open = false" @submit="add.submit(form, ['employee', 'salary_component', 'amount', 'payroll_date'])" />
  </div>
</template>
