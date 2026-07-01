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
const r = createResource({ url: "frappe_hr_ui.api.get_hr_dashboard", auto: true })
const d = computed(() => r.data || {})
const maxDept = computed(() => Math.max(1, ...(d.value.dept_counts || []).map((x) => x[1])))
const tiles = computed(() => [
  { label: "Headcount", value: d.value.headcount ?? 0, sub: "active employees", icon: "users", tone: "accent" },
  { label: "Open positions", value: d.value.open_jobs ?? 0, sub: "across teams", icon: "briefcase", tone: "warning" },
  { label: "Applicants", value: d.value.applicants ?? 0, sub: "in pipeline", icon: "inbox", tone: "neutral" },
  { label: "Latest payroll", value: formatINRShort(d.value.payroll_cost || 0), sub: "gross", icon: "rupee", tone: "neutral" },
])
const monthTiles = computed(() => {
  const m = d.value.month || {}
  return [["Joined", m.joined, "success"], ["Exited", m.exited, "danger"], ["On probation", m.probation, "warning"], ["On notice", m.on_notice, "neutral"]]
})
const maxFunnel = computed(() => Math.max(1, ...(d.value.funnel || []).map((x) => x[1])))
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="HR dashboard" :subtitle="`Frappe Technologies · ${d.headcount ?? 0} employees`">
      <template #actions><Button variant="solid" theme="blue" label="Run payroll" @click="router.push({ name: 'HrPayrun' }).catch(() => {})"><template #prefix><Icon name="rupee" :size="15" /></template></Button></template>
    </PageHeader>
    <AsyncShell :resource="r" loading-text="Loading dashboard…">
    <StatTiles :items="tiles" :cols="4" />
    <div class="grid items-start gap-5" style="grid-template-columns: minmax(0,1fr) 340px">
      <div class="flex flex-col gap-5">
        <div class="grid grid-cols-2 gap-5">
          <Card>
            <CardHeader title="Headcount by department" />
            <div class="flex flex-col gap-2.5">
              <div v-for="[dn, n] in d.dept_counts || []" :key="dn" class="flex items-center gap-2.5">
                <div class="w-28 truncate text-[12.5px] text-ink-gray-7">{{ dn }}</div>
                <div class="h-4 flex-1 overflow-hidden rounded bg-surface-gray-2"><div class="h-full rounded bg-blue-500/85" :style="{ width: (n / maxDept * 100) + '%' }" /></div>
                <div class="tnum w-6 text-right text-[12.5px] font-medium">{{ n }}</div>
              </div>
            </div>
          </Card>
          <Card>
            <CardHeader title="This month" sub="Operational pulse" />
            <div class="grid grid-cols-2 gap-3.5">
              <div v-for="[l, v, t] in monthTiles" :key="l" class="rounded-md border border-outline-gray-1 p-3">
                <div class="tnum text-[22px] font-medium" :class="{ 'text-green-600': t === 'success', 'text-red-600': t === 'danger', 'text-orange-600': t === 'warning', 'text-ink-gray-9': t === 'neutral' }">{{ v ?? 0 }}</div>
                <div class="mt-0.5 text-[12px] text-ink-gray-5">{{ l }}</div>
              </div>
            </div>
          </Card>
        </div>
        <Card>
          <CardHeader title="Recruitment funnel" :sub="`${d.open_jobs ?? 0} open positions`">
            <template #action><Button variant="ghost" size="sm" label="Pipeline" @click="router.push({ name: 'HrPipeline' }).catch(() => {})" /></template>
          </CardHeader>
          <div class="flex items-stretch gap-0">
            <div v-for="[l, n] in d.funnel || []" :key="l" class="flex-1 text-center">
              <div class="flex h-[70px] items-end justify-center px-1.5"><div class="w-full rounded-t bg-blue-500/85" :style="{ height: (n / maxFunnel * 100) + '%', minHeight: '8px' }" /></div>
              <div class="tnum mt-1.5 text-[17px] font-medium">{{ n }}</div>
              <div class="text-[11.5px] text-ink-gray-5">{{ l }}</div>
            </div>
          </div>
        </Card>
      </div>
      <Card>
        <CardHeader title="Action centre" icon="inbox" />
        <div class="flex flex-col">
          <Button v-for="[t, s, ic, to] in [['Run June payroll', 'Locks soon', 'rupee', 'HrPayrun'], ['File TDS 24Q', 'Due 7 Jun', 'file', 'ComplianceTds'], ['Onboarding tasks', 'New hires', 'login', 'HrOnboarding'], ['Exit clearances', 'On notice', 'logout', 'HrSeparation'], ['Offers to review', 'Recruitment', 'briefcase', 'HrOffers']]" :key="t"
            variant="ghost" @click="router.push({ name: to }).catch(() => {})" class="w-full !justify-start border-t border-outline-gray-1 text-left first:border-t-0">
            <div class="flex w-full items-center gap-3">
              <div class="flex h-[30px] w-[30px] items-center justify-center rounded-md bg-surface-gray-2 text-ink-gray-7"><Icon :name="ic" :size="15" /></div>
              <div class="min-w-0 flex-1"><div class="text-[13px] font-medium text-ink-gray-9">{{ t }}</div><div class="text-[11.5px] text-ink-gray-5">{{ s }}</div></div>
              <Icon name="chevRight" :size="15" class="text-ink-gray-4" />
            </div>
          </Button>
        </div>
      </Card>
    </div>
    </AsyncShell>
  </div>
</template>
