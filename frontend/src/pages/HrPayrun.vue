<script setup>
import { computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import StatTiles from "@/components/ui/StatTiles.vue"
import Card from "@/components/ui/Card.vue"
import Toolbar from "@/components/ui/Toolbar.vue"
import DataTable from "@/components/ui/DataTable.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"
import { formatINR, formatINRShort } from "@/utils/formatters"

const r = createResource({ url: "frappe_hr_ui.api.get_payroll_run", auto: true })
const d = computed(() => r.data || {})
const tiles = computed(() => {
  const t = d.value.totals || {}
  return [
    { label: "Gross payout", value: formatINRShort(t.gross || 0), sub: `${t.count || 0} employees`, icon: "rupee", tone: "neutral" },
    { label: "Total deductions", value: formatINRShort(t.deductions || 0), sub: "PF · PT · TDS", icon: "layers", tone: "neutral" },
    { label: "Net disbursement", value: formatINRShort(t.net || 0), sub: "via NEFT", icon: "card", tone: "accent" },
    { label: "Employees", value: t.count || 0, sub: "in this run", icon: "users", tone: "neutral" },
  ]
})
const STEPS = ["Setup", "Compute", "Review", "Approve", "Disburse"]
const columns = [
  { key: "employee_name", label: "Employee" },
  { key: "department", label: "Dept" },
  { key: "gross_pay", label: "Gross", align: "right" },
  { key: "pf", label: "PF", align: "right" },
  { key: "tds", label: "TDS", align: "right" },
  { key: "net_pay", label: "Net pay", align: "right" },
]
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader :title="`Payroll run — ${d.period || ''}`" subtitle="Monthly cycle">
      <template #actions><Button variant="solid" theme="gray" label="Submit for approval"><template #prefix><Icon name="check" :size="15" /></template></Button></template>
    </PageHeader>
    <Card class="mb-5">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center">
          <template v-for="(s, i) in STEPS" :key="s">
            <div class="flex items-center gap-2">
              <div class="flex h-[26px] w-[26px] items-center justify-center rounded-full text-[12px] font-medium"
                :class="i < 2 ? 'bg-green-500 text-white' : i === 2 ? 'bg-blue-500 text-white' : 'border-[1.5px] border-outline-gray-2 text-ink-gray-5'">
                <Icon v-if="i < 2" name="check" :size="13" :stroke-width="3" /><span v-else>{{ i + 1 }}</span>
              </div>
              <span class="text-[13px]" :class="i === 2 ? 'font-medium text-ink-gray-9' : 'text-ink-gray-5'">{{ s }}</span>
            </div>
            <div v-if="i < STEPS.length - 1" class="mx-3 h-0.5 w-9" :class="i < 2 ? 'bg-green-500' : 'bg-outline-gray-1'" />
          </template>
        </div>
        <StatusBadge tone="warning" dot label="Draft · review" />
      </div>
    </Card>
    <StatTiles :items="tiles" :cols="4" />
    <Card class="!p-4">
      <Toolbar search="Search employees…" />
      <DataTable :columns="columns" :rows="d.slips || []" row-key="name" selectable :loading="r.loading">
        <template #cell-employee_name="{ row }"><div class="flex items-center gap-2.5"><InitialsAvatar :name="row.employee_name" :size="28" /><span class="font-medium">{{ row.employee_name }}</span></div></template>
        <template #cell-department="{ row }"><StatusBadge tone="neutral" size="sm" :label="row.department" /></template>
        <template #cell-gross_pay="{ row }"><span class="tnum">{{ formatINR(row.gross_pay) }}</span></template>
        <template #cell-pf="{ row }"><span class="tnum text-ink-gray-6">{{ formatINR(row.pf) }}</span></template>
        <template #cell-tds="{ row }"><span class="tnum text-ink-gray-6">{{ formatINR(row.tds) }}</span></template>
        <template #cell-net_pay="{ row }"><span class="tnum font-medium">{{ formatINR(row.net_pay) }}</span></template>
      </DataTable>
    </Card>
  </div>
</template>
