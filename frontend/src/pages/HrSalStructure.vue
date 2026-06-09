<script setup>
import { computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import DataTable from "@/components/ui/DataTable.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import AmountRow from "@/components/ui/AmountRow.vue"
import Icon from "@/components/ui/Icon.vue"

const r = createResource({ url: "frappe_hr_ui.api.get_salary_structure", auto: true })
const d = computed(() => r.data || {})
const columns = [
  { key: "name", label: "Component" },
  { key: "type", label: "Type" },
  { key: "formula", label: "Calculation" },
]
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Salary structure" :subtitle="d.structure || 'Standard structure'">
      <template #actions><Button variant="solid" theme="gray" label="New component"><template #prefix><Icon name="plus" :size="15" /></template></Button></template>
    </PageHeader>
    <div class="grid items-start gap-5" style="grid-template-columns: minmax(0,1fr) 320px">
      <Card class="!p-4">
        <DataTable :columns="columns" :rows="d.components || []" row-key="name" :loading="r.loading" empty-title="No structure found">
          <template #cell-name="{ row }"><span class="font-medium">{{ row.name }}</span></template>
          <template #cell-type="{ row }"><StatusBadge :tone="row.type === 'Earning' ? 'success' : 'danger'" size="sm" :label="row.type" /></template>
          <template #cell-formula="{ row }"><span class="tnum text-ink-gray-6">{{ row.formula }}</span></template>
        </DataTable>
      </Card>
      <Card>
        <CardHeader title="Structure summary" />
        <AmountRow label="Earning components" :value="d.earnings ?? 0" />
        <AmountRow label="Deduction components" :value="d.deductions ?? 0" />
        <AmountRow label="Employees assigned" :value="d.employees ?? 0" :border="false" />
      </Card>
    </div>
  </div>
</template>
