<script setup>
import { computed } from "vue"
import { useRouter } from "vue-router"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import StatTiles from "@/components/ui/StatTiles.vue"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import Icon from "@/components/ui/Icon.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"
import { formatINRShort } from "@/utils/formatters"

const router = useRouter()
const r = createResource({ url: "frappe_hr_ui.api.get_payroll_dashboard", auto: true })
const d = computed(() => r.data || {})
const t = computed(() => d.value.totals || {})

const tiles = computed(() => [
  { label: "Net payout", value: formatINRShort(t.value.net || 0), sub: d.value.period || "—", icon: "rupee", tone: "accent" },
  { label: "Gross", value: formatINRShort(t.value.gross || 0), sub: "before deductions", icon: "wallet", tone: "neutral" },
  { label: "On payroll", value: d.value.on_payroll ?? 0, sub: "with salary structure", icon: "users", tone: "neutral" },
  { label: "Draft slips", value: d.value.drafts ?? 0, sub: "in progress", icon: "file", tone: "warning" },
])
const maxDept = computed(() => Math.max(1, ...(d.value.dept_cost || []).map((x) => x[1])))
const maxStat = computed(() => Math.max(1, ...(d.value.statutory || []).map((x) => x[1])))
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Payroll dashboard" :subtitle="`Pay & compliance · ${d.period || '—'}`">
      <template #actions><Button variant="solid" theme="blue" label="Run payroll" @click="router.push({ name: 'HrPayrun' }).catch(() => {})"><template #prefix><Icon name="rupee" :size="15" /></template></Button></template>
    </PageHeader>
    <AsyncShell :resource="r" loading-text="Loading payroll…">
      <StatTiles :items="tiles" :cols="4" />
      <div class="grid items-start gap-5" style="grid-template-columns: minmax(0,1fr) 340px">
        <div class="flex flex-col gap-5">
          <Card>
            <CardHeader title="Cost by department" :sub="`${t.count ?? 0} payslips`" />
            <div v-if="(d.dept_cost || []).length" class="flex flex-col gap-2.5">
              <div v-for="[dn, n] in d.dept_cost || []" :key="dn" class="flex items-center gap-2.5">
                <div class="w-32 truncate text-[12.5px] text-ink-gray-7">{{ dn }}</div>
                <div class="h-4 flex-1 overflow-hidden rounded bg-surface-gray-2"><div class="h-full rounded bg-blue-500/85" :style="{ width: (n / maxDept * 100) + '%' }" /></div>
                <div class="tnum w-20 text-right text-[12.5px] font-medium">{{ formatINRShort(n) }}</div>
              </div>
            </div>
            <div v-else class="py-6 text-center text-[12.5px] text-ink-gray-4">No processed payroll yet.</div>
          </Card>
          <Card>
            <CardHeader title="Statutory deductions" sub="Across processed slips">
              <template #action><Button variant="ghost" size="sm" label="Compliance" @click="router.push({ name: 'ComplianceTds' }).catch(() => {})" /></template>
            </CardHeader>
            <div class="flex flex-col gap-2.5">
              <div v-for="[l, n] in d.statutory || []" :key="l" class="flex items-center gap-2.5">
                <div class="w-32 truncate text-[12.5px] text-ink-gray-7">{{ l }}</div>
                <div class="h-4 flex-1 overflow-hidden rounded bg-surface-gray-2"><div class="h-full rounded bg-blue-500/70" :style="{ width: (n / maxStat * 100) + '%' }" /></div>
                <div class="tnum w-20 text-right text-[12.5px] font-medium">{{ formatINRShort(n) }}</div>
              </div>
            </div>
          </Card>
        </div>
        <Card>
          <CardHeader title="Action centre" icon="inbox" />
          <div class="flex flex-col">
            <Button v-for="[ti, s, ic, to] in [['Process payroll run', 'Generate slips', 'rupee', 'HrPayrun'], ['Salary structure', 'Earnings & deductions', 'layers', 'HrSalStructure'], ['Bank disbursement', 'Pay out', 'card', 'HrBankfile'], ['Reconciliation', 'Match & verify', 'check', 'HrReconcile'], ['TDS & challan', 'Statutory filing', 'shield', 'ComplianceTds']]" :key="ti"
              variant="ghost" @click="router.push({ name: to }).catch(() => {})" class="w-full !justify-start border-t border-outline-gray-1 text-left first:border-t-0">
              <div class="flex w-full items-center gap-3">
                <div class="flex h-[30px] w-[30px] items-center justify-center rounded-md bg-surface-gray-2 text-ink-gray-7"><Icon :name="ic" :size="15" /></div>
                <div class="min-w-0 flex-1"><div class="text-[13px] font-medium text-ink-gray-9">{{ ti }}</div><div class="text-[11.5px] text-ink-gray-5">{{ s }}</div></div>
                <Icon name="chevRight" :size="15" class="text-ink-gray-4" />
              </div>
            </Button>
          </div>
        </Card>
      </div>
    </AsyncShell>
  </div>
</template>
