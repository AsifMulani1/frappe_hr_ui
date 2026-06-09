<script setup>
import { ref, reactive, computed } from "vue"
import { Button, FormControl, createResource, toast } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import StatTiles from "@/components/ui/StatTiles.vue"
import Card from "@/components/ui/Card.vue"
import Toolbar from "@/components/ui/Toolbar.vue"
import FilterChip from "@/components/ui/FilterChip.vue"
import DataTable from "@/components/ui/DataTable.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import Drawer from "@/components/ui/Drawer.vue"
import Icon from "@/components/ui/Icon.vue"
import { formatINR } from "@/utils/formatters"

const props = defineProps({
  title: { type: String, default: "Reimbursements" },
  subtitle: { type: String, default: "Claim work expenses paid out of pocket" },
  addLabel: { type: String, default: "New reimbursement" },
})
const r = createResource({ url: "frappe_hr_ui.api.get_expense_claims_screen", auto: true })
const d = computed(() => r.data || {})
const open = ref(false)

const expenseTypes = createResource({ url: "frappe_hr_ui.api.get_expense_types", auto: true })
const typeOptions = computed(() => (expenseTypes.data?.types || []))
const form = reactive({ expense_type: "", amount: "", expense_date: "", description: "" })
const submit = createResource({
  url: "frappe_hr_ui.api.submit_expense_claim",
  onSuccess() {
    toast.success("Claim submitted")
    open.value = false
    Object.assign(form, { expense_type: "", amount: "", expense_date: "", description: "" })
    r.reload()
  },
  onError(e) { toast.error(e?.messages?.[0] || "Couldn't submit claim") },
})
function submitClaim() {
  if (!form.expense_type || !form.amount) { toast.error("Pick a category and amount"); return }
  submit.submit({ ...form })
}
const STATUS_TONE = { Approved: "success", Draft: "warning", Paid: "accent", Rejected: "danger" }
const tiles = computed(() => {
  const s = d.value.summary || {}
  return [
    { label: "Total claimed (FY)", value: formatINR(s.total), sub: `${s.count || 0} claims`, icon: "wallet", tone: "neutral" },
    { label: "Approved & paid", value: formatINR(s.approved), sub: "credited with payroll", icon: "check", tone: "success" },
    { label: "Awaiting approval", value: formatINR(s.pending), sub: `${s.pending_count || 0} pending`, icon: "clock", tone: "warning" },
  ]
})
const columns = [
  { key: "id", label: "Claim", width: 120 },
  { key: "category", label: "Category" },
  { key: "desc", label: "Description" },
  { key: "date", label: "Date" },
  { key: "amount", label: "Amount", align: "right" },
  { key: "status", label: "Status" },
]
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader :title="title" :subtitle="subtitle">
      <template #actions>
        <Button variant="solid" theme="gray" :label="addLabel" @click="open = true"><template #prefix><Icon name="plus" :size="15" /></template></Button>
      </template>
    </PageHeader>
    <StatTiles :items="tiles" :cols="3" />
    <Card :pad="false">
      <div class="p-4">
        <Toolbar search="Search claims…"><FilterChip label="Status" active /><FilterChip label="Category" /></Toolbar>
        <DataTable :columns="columns" :rows="d.claims || []" row-key="id" selectable :loading="r.loading"
          empty-title="No claims yet" empty-message="Submit a claim and it'll appear here.">
          <template #cell-id="{ row }"><span class="tnum font-medium">{{ row.id }}</span></template>
          <template #cell-category="{ row }">
            <div class="flex items-center gap-2">
              <div class="flex h-7 w-7 items-center justify-center rounded-md bg-surface-gray-2 text-ink-gray-7"><Icon name="wallet" :size="15" /></div>
              <span class="font-medium">{{ row.category }}</span>
            </div>
          </template>
          <template #cell-desc="{ row }"><span class="text-ink-gray-7">{{ row.desc }}</span></template>
          <template #cell-date="{ row }"><span class="text-ink-gray-5">{{ row.date }}</span></template>
          <template #cell-amount="{ row }"><span class="tnum font-medium">{{ formatINR(row.amount) }}</span></template>
          <template #cell-status="{ row }"><StatusBadge :tone="STATUS_TONE[row.status] || 'neutral'" size="sm" dot :label="row.status" /></template>
        </DataTable>
      </div>
    </Card>
    <Drawer :open="open" :title="addLabel" subtitle="Submit for approval" :width="480" @close="open = false">
      <div class="flex flex-col gap-4">
        <FormControl type="select" label="Category" :options="typeOptions" v-model="form.expense_type" />
        <div class="grid grid-cols-2 gap-3">
          <FormControl type="number" label="Amount (₹)" placeholder="0" v-model="form.amount" />
          <FormControl type="date" label="Date of expense" v-model="form.expense_date" />
        </div>
        <FormControl type="textarea" label="Description" placeholder="What was this for?" v-model="form.description" />
      </div>
      <template #footer><Button variant="ghost" label="Cancel" @click="open = false" /><Button variant="solid" theme="gray" label="Submit claim" :loading="submit.loading" @click="submitClaim" /></template>
    </Drawer>
  </div>
</template>
