<script setup>
import { ref, computed } from "vue"
import { Button, createResource } from "frappe-ui"
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
    <Drawer :open="open" :title="addLabel" subtitle="Attach a receipt and submit for approval" :width="480" @close="open = false">
      <div class="text-[13px] text-ink-gray-6">Pick a category, amount and receipt. Submitting routes to your approver.</div>
      <template #footer><Button variant="ghost" label="Save draft" @click="open = false" /><Button variant="solid" theme="gray" label="Submit claim" @click="open = false" /></template>
    </Drawer>
  </div>
</template>
