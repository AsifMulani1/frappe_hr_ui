<script setup>
import { reactive, computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import StatTiles from "@/components/ui/StatTiles.vue"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import DataTable from "@/components/ui/DataTable.vue"
import AmountRow from "@/components/ui/AmountRow.vue"
import Icon from "@/components/ui/Icon.vue"
import FormDrawer from "@/components/ui/FormDrawer.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"
import { toast } from "frappe-ui"
import { formatINR, formatINRShort } from "@/utils/formatters"
import { useCreate, useLinkOptions } from "@/composables/useDocActions"

const r = createResource({ url: "frappe_hr_ui.api.get_tax_screen", auto: true })

// Update declaration (in-app, self)
const add = useCreate("Employee Tax Exemption Declaration", { onDone: () => r.reload(), successLabel: "Declaration created" })
const periods = useLinkOptions("Payroll Period")
const form = reactive({ payroll_period: "" })
const fields = computed(() => [
  { key: "payroll_period", label: "Payroll period", type: "select", options: periods.value, cols: 2 },
])
function openDeclaration() {
  form.payroll_period = ""
  add.openDrawer()
}
function getForm16() {
  toast.success("Form 16 is issued by Payroll after year-end; you'll be notified when it's ready.")
}
const d = computed(() => r.data || {})
const fbpTotal = computed(() => (d.value.fbp || []).reduce((s, x) => s + (Number(x?.[1]) || 0), 0))
const tiles = computed(() => [
  { label: "Tax paid (TDS)", value: formatINR(d.value.tds_paid || 0), sub: "this financial year", icon: "check", tone: "success" },
  { label: "Total declared", value: formatINRShort(d.value.declared_total || 0), sub: "across sections", icon: "file", tone: "neutral" },
  { label: "Flexible benefits", value: formatINR(fbpTotal.value), sub: "monthly allocation", icon: "wallet", tone: "accent" },
  { label: "Declarations", value: `${(d.value.declarations || []).length}`, sub: "sections declared", icon: "file", tone: "neutral" },
])
const columns = [
  { key: "sec", label: "Section", width: 120 },
  { key: "limit", label: "Max limit", align: "right" },
  { key: "declared", label: "Declared", align: "right" },
]
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Tax & Flexible Benefits" subtitle="Investment declaration and tax regime">
      <template #actions>
        <Button variant="outline" theme="gray" label="Form 16" @click="getForm16"><template #prefix><Icon name="download" :size="15" /></template></Button>
        <Button variant="solid" theme="blue" label="Update Declaration" @click="openDeclaration"><template #prefix><Icon name="edit" :size="15" /></template></Button>
      </template>
    </PageHeader>
    <AsyncShell :resource="r" :has-employee="!!d.employee" loading-text="Loading tax & benefits…">
    <StatTiles :items="tiles" :cols="4" />
    <div class="grid items-start gap-5" style="grid-template-columns: minmax(0,1fr) 320px">
      <Card :pad="false">
        <div class="p-5">
          <CardHeader title="Investment Declarations" sub="Declare to reduce monthly TDS" />
          <DataTable :columns="columns" :rows="d.declarations || []" row-key="sec"
            empty-title="No declarations yet" empty-message="Declare your investments to reduce monthly TDS.">
            <template #cell-limit="{ row }"><span class="tnum">{{ formatINR(row.limit) }}</span></template>
            <template #cell-declared="{ row }"><span class="tnum font-medium">{{ formatINR(row.declared) }}</span></template>
          </DataTable>
        </div>
      </Card>
      <Card>
        <CardHeader title="Flexible Benefits (FBP)" sub="Monthly allocation" />
        <AmountRow v-for="[l, v] in d.fbp || []" :key="l" :label="l" :value="formatINR(Number(v) || 0)" />
        <AmountRow label="Total FBP" :value="formatINR(fbpTotal)" bold :border="false" />
        <div v-if="!(d.fbp || []).length" class="py-2 text-center text-xs text-ink-gray-5">No flexible benefits configured.</div>
      </Card>
    </div>
    </AsyncShell>

    <FormDrawer :open="add.open" title="Update Declaration" subtitle="Declare investments to reduce monthly TDS"
      :fields="fields" v-model="form" :loading="add.create.loading" submit-label="Create Declaration"
      @close="add.open = false" @submit="add.submit(form, ['payroll_period'])" />
  </div>
</template>
