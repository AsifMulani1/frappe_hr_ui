<script setup>
import { computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import DataTable from "@/components/ui/DataTable.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"
import { formatINRShort } from "@/utils/formatters"

const r = createResource({ url: "frappe_hr_ui.api.get_revisions", auto: true })
const rows = computed(() => r.data?.rows || [])
const columns = [
  { key: "name", label: "Employee" },
  { key: "type", label: "Type" },
  { key: "to", label: "Annual CTC", align: "right" },
  { key: "eff", label: "Effective" },
]
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Revisions & arrears" subtitle="Salary changes and structure assignments">
      <template #actions><Button variant="solid" theme="gray" label="New revision"><template #prefix><Icon name="plus" :size="15" /></template></Button></template>
    </PageHeader>
    <Card class="!p-4">
      <DataTable :columns="columns" :rows="rows" row-key="name" :loading="r.loading" empty-title="No revisions yet">
        <template #cell-name="{ row }"><div class="flex items-center gap-2.5"><InitialsAvatar :name="row.name" :size="30" /><span class="font-medium">{{ row.name }}</span></div></template>
        <template #cell-type="{ row }"><StatusBadge tone="neutral" size="sm" :label="row.type" /></template>
        <template #cell-to="{ row }"><span class="tnum font-medium">{{ formatINRShort(row.to) }}</span></template>
        <template #cell-eff="{ row }"><span class="tnum">{{ row.eff }}</span></template>
      </DataTable>
    </Card>
  </div>
</template>
