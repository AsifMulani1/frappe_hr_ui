<script setup>
import { computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import StatTiles from "@/components/ui/StatTiles.vue"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import DataTable from "@/components/ui/DataTable.vue"
import AmountRow from "@/components/ui/AmountRow.vue"
import Icon from "@/components/ui/Icon.vue"
import { formatINR, formatINRShort } from "@/utils/formatters"

const r = createResource({ url: "frappe_hr_ui.api.get_tax_screen", auto: true })
const d = computed(() => r.data || {})
const tiles = computed(() => [
  { label: "Tax paid (TDS)", value: formatINR(d.value.tds_paid || 0), sub: "this financial year", icon: "check", tone: "success" },
  { label: "Total declared", value: formatINRShort(d.value.declared_total || 0), sub: "across sections", icon: "file", tone: "neutral" },
  { label: "Regime", value: "New", sub: "default", icon: "rupee", tone: "accent" },
  { label: "Proof submission", value: "31 Dec", sub: "deadline", icon: "calendar", tone: "warning" },
])
const columns = [
  { key: "sec", label: "Section", width: 120 },
  { key: "limit", label: "Max limit", align: "right" },
  { key: "declared", label: "Declared", align: "right" },
]
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Tax & flexible benefits" subtitle="Investment declaration and tax regime">
      <template #actions>
        <Button variant="outline" theme="gray" label="Form 16"><template #prefix><Icon name="download" :size="15" /></template></Button>
        <Button variant="solid" theme="gray" label="Update declaration"><template #prefix><Icon name="edit" :size="15" /></template></Button>
      </template>
    </PageHeader>
    <StatTiles :items="tiles" :cols="4" />
    <div class="grid items-start gap-5" style="grid-template-columns: minmax(0,1fr) 320px">
      <Card :pad="false">
        <div class="p-5">
          <CardHeader title="Investment declarations" sub="Declare to reduce monthly TDS" />
          <DataTable :columns="columns" :rows="d.declarations || []" row-key="sec"
            empty-title="No declarations yet" empty-message="Declare your investments to reduce monthly TDS.">
            <template #cell-limit="{ row }"><span class="tnum">{{ formatINR(row.limit) }}</span></template>
            <template #cell-declared="{ row }"><span class="tnum font-medium">{{ formatINR(row.declared) }}</span></template>
          </DataTable>
        </div>
      </Card>
      <Card>
        <CardHeader title="Flexible benefits (FBP)" sub="Monthly allocation" />
        <AmountRow v-for="[l, v] in d.fbp || []" :key="l" :label="l" :value="formatINR(v)" />
        <AmountRow label="Total FBP" :value="formatINR((d.fbp || []).reduce((s, x) => s + x[1], 0))" bold :border="false" />
      </Card>
    </div>
  </div>
</template>
