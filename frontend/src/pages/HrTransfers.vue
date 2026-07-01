<script setup>
import { reactive, computed } from "vue"
import { Button, createResource, toast } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import DataTable from "@/components/ui/DataTable.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"
import FormDrawer from "@/components/ui/FormDrawer.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"
import { useCreate, useLinkOptions } from "@/composables/useDocActions"

const r = createResource({ url: "frappe_hr_ui.api.get_transfers", auto: true })
const rows = computed(() => r.data?.rows || [])
const columns = [
  { key: "name", label: "Employee" },
  { key: "type", label: "Type" },
  { key: "eff", label: "Effective" },
  { key: "st", label: "Status" },
]

const add = useCreate("Employee Transfer", { onDone: () => r.reload(), successLabel: "Movement recorded" })
const employees = useLinkOptions("Employee")
const departments = useLinkOptions("Department")
const designations = useLinkOptions("Designation")
const form = reactive({ employee: "", transfer_date: "", new_department: "", new_designation: "" })
const fields = computed(() => [
  { key: "employee", label: "Employee", type: "select", options: employees.value, cols: 2 },
  { key: "transfer_date", label: "Transfer date", type: "date", cols: 1 },
  { key: "new_department", label: "New department", type: "select", options: departments.value, cols: 1 },
  { key: "new_designation", label: "New designation", type: "select", options: designations.value, cols: 1 },
])
function openAdd() {
  Object.assign(form, { employee: "", transfer_date: "", new_department: "", new_designation: "" })
  add.openDrawer()
}
function submitMove() {
  if (!form.employee || !form.transfer_date) {
    toast.error("Pick an employee and date")
    return
  }
  if (!form.new_department && !form.new_designation) {
    toast.error("Choose a new department or designation")
    return
  }
  add.submit(form)
}
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Transfers & Promotions" subtitle="Internal movements and role changes">
      <template #actions><Button variant="solid" theme="blue" label="New Movement" @click="openAdd"><template #prefix><Icon name="plus" :size="15" /></template></Button></template>
    </PageHeader>
    <AsyncShell :resource="r" loading-text="Loading movements…">
    <Card class="!p-4">
      <DataTable :columns="columns" :rows="rows" row-key="name" :loading="r.loading" empty-title="No movements yet" empty-message="Transfers and promotions will appear here.">
        <template #cell-name="{ row }"><div class="flex items-center gap-2.5"><InitialsAvatar :name="row.name" :size="30" /><span class="font-medium">{{ row.name }}</span></div></template>
        <template #cell-type="{ row }"><StatusBadge :tone="row.type === 'Promotion' ? 'accent' : 'neutral'" size="sm" :label="row.type" /></template>
        <template #cell-eff="{ row }"><span class="tnum">{{ row.eff }}</span></template>
        <template #cell-st="{ row }"><StatusBadge tone="success" size="sm" dot :label="row.st" /></template>
      </DataTable>
    </Card>
    </AsyncShell>

    <FormDrawer :open="add.open" title="New Movement" subtitle="Record a transfer or promotion"
      :fields="fields" v-model="form" :loading="add.create.loading" submit-label="Record Movement"
      @close="add.open = false" @submit="submitMove" />
  </div>
</template>
