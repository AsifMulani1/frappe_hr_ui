<script setup>
import { ref, computed, watch } from "vue"
import { Button, createResource, toast } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import StatTiles from "@/components/ui/StatTiles.vue"
import Card from "@/components/ui/Card.vue"
import Toolbar from "@/components/ui/Toolbar.vue"
import DataTable from "@/components/ui/DataTable.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import Drawer from "@/components/ui/Drawer.vue"
import DateField from "@/components/ui/DateField.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"
import { formatINR, formatINRShort } from "@/utils/formatters"

// ---- Run payroll (generate + submit slips for the month) ----
const runOpen = ref(false)
const period = ref("")
function monthBounds(dateStr) {
  const d = new Date(dateStr), pad = (n) => String(n).padStart(2, "0")
  const first = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-01`
  const last = new Date(d.getFullYear(), d.getMonth() + 1, 0)
  return { first, last: `${last.getFullYear()}-${pad(last.getMonth() + 1)}-${pad(last.getDate())}` }
}
const preview = createResource({ url: "frappe_hr_ui.api.preview_payroll" })
watch(period, (p) => { if (p) preview.fetch({ start_date: monthBounds(p).first }) })
function openRun() {
  const now = new Date()
  period.value = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-01`
  runOpen.value = true
}
const run = createResource({
  url: "frappe_hr_ui.api.run_payroll",
  onSuccess(res) {
    const msg = `${res.created} slip(s) created${res.skipped ? `, ${res.skipped} skipped` : ""}${res.errors?.length ? `, ${res.errors.length} failed` : ""}`
    res.errors?.length ? toast.warning(msg) : toast.success(msg)
    runOpen.value = false
    r.reload()
  },
  onError(e) { toast.error(e?.messages?.[0] || "Couldn't run payroll") },
})
function doRun() {
  if (!period.value) { toast.error("Pick a month"); return }
  const { first, last } = monthBounds(period.value)
  run.submit({ start_date: first, end_date: last })
}

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
      <template #actions><Button variant="solid" theme="blue" label="Run payroll" @click="openRun"><template #prefix><Icon name="rupee" :size="15" /></template></Button></template>
    </PageHeader>
    <AsyncShell :resource="r" loading-text="Loading payroll run…">
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
    </AsyncShell>

    <Drawer :open="runOpen" title="Run payroll" subtitle="Generate and submit salary slips for the month" :width="460" @close="runOpen = false">
      <div class="flex flex-col gap-4">
        <DateField label="Payroll month" v-model="period" placeholder="Pick any date in the month" />
        <div v-if="preview.data" class="rounded-md border border-outline-gray-1 bg-surface-gray-1 p-3.5 text-[13px]">
          <div class="font-medium text-ink-gray-9">{{ preview.data.period }}</div>
          <div class="mt-1 text-ink-gray-6">
            <span class="font-medium text-ink-gray-9 tnum">{{ preview.data.pending }}</span> employee(s) to process
            <span v-if="preview.data.eligible - preview.data.pending"> · {{ preview.data.eligible - preview.data.pending }} already run</span>
          </div>
        </div>
        <p class="text-[11.5px] text-ink-gray-4">Statutory deductions (PF, PT, ESI, LWF, TDS) are computed automatically. Slips already created for this month are skipped.</p>
      </div>
      <template #footer>
        <Button variant="ghost" label="Cancel" @click="runOpen = false" />
        <Button variant="solid" theme="blue" :label="`Run payroll${preview.data?.pending ? ` (${preview.data.pending})` : ''}`" :loading="run.loading" :disabled="!preview.data?.pending" @click="doRun" />
      </template>
    </Drawer>
  </div>
</template>
