<script setup>
import { computed, watch } from "vue"
import { useRouter } from "vue-router"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import StatTiles from "@/components/ui/StatTiles.vue"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import AmountRow from "@/components/ui/AmountRow.vue"
import Icon from "@/components/ui/Icon.vue"
import { ref } from "vue"
import ReportDrawer from "@/components/ui/ReportDrawer.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"

const props = defineProps({ kind: { type: String, required: true } })
const router = useRouter()
const r = createResource({ url: "frappe_hr_ui.api.get_compliance" })
watch(() => props.kind, (k) => r.fetch({ kind: k }), { immediate: true })
const d = computed(() => r.data || {})

const PORTALS = {
  pf: "https://unifiedportal-emp.epfindia.gov.in",
  esi: "https://www.esic.gov.in",
  pt: "https://www.gst.gov.in",
  lwf: "https://www.labour.gov.in",
  tds: "https://www.incometax.gov.in",
}
// Per-kind statutory register (india_payroll script reports where available).
const REGISTERS = {
  esi: "ESIC Register",
  lwf: "LWF Register",
  pf: "Salary Register",
  pt: "Salary Register",
  tds: "Income Tax Computation",
}
const registerReport = computed(() => REGISTERS[props.kind] || "Salary Register")
const reportOpen = ref(false)
function generateChallan() {
  reportOpen.value = true
}
function openPortal() {
  window.open(PORTALS[props.kind] || "https://www.incometax.gov.in", "_blank", "noopener")
}
function quickLink(label) {
  if (label.startsWith("Open")) openPortal()
  else if (label.startsWith("Download")) reportOpen.value = true
  else router.push("/statutory-calendar")
}
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader :title="d.title || 'Compliance'" :subtitle="d.sub">
      <template #actions><Button variant="solid" theme="blue" label="Generate challan" @click="generateChallan"><template #prefix><Icon name="external" :size="15" /></template></Button></template>
    </PageHeader>
    <AsyncShell :resource="r" loading-text="Loading compliance…">
    <StatTiles :items="d.stats || []" :cols="4" />
    <div class="grid items-start gap-5" style="grid-template-columns: minmax(0,1fr) 340px">
      <Card>
        <CardHeader title="Authority & rate" icon="shield" />
        <AmountRow label="Statutory body" :value="d.authority" />
        <AmountRow label="Code" :value="d.code" />
        <AmountRow label="Establishment" value="MH/BAN/0042851" :border="false" />
        <div class="mt-3 rounded-md border border-outline-gray-1 bg-surface-gray-1 p-3 text-[12.5px] leading-relaxed text-ink-gray-7">
          <b class="font-medium text-ink-gray-9">Rate:</b> {{ d.rate }}
        </div>
      </Card>
      <Card>
        <CardHeader title="Quick links" />
        <div class="flex flex-col gap-0.5">
          <button v-for="[ic, t] in [['external', `Open ${d.authority || ''} portal`], ['file', `Download ${d.code || ''} register`], ['calendar', 'Statutory calendar']]" :key="t"
            @click="quickLink(t)"
            class="flex items-center gap-2.5 rounded-md px-2 py-2 text-left text-ink-gray-7 hover:bg-surface-gray-1">
            <Icon :name="ic" :size="16" /><span class="flex-1 text-[13px] text-ink-gray-9">{{ t }}</span><Icon name="chevRight" :size="14" class="text-ink-gray-4" />
          </button>
        </div>
      </Card>
    </div>
    </AsyncShell>

    <ReportDrawer :open="reportOpen" :report="registerReport" :title="`${d.title || 'Compliance'} register`" @close="reportOpen = false" />
  </div>
</template>
