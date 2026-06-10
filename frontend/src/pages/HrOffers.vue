<script setup>
import { reactive, computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import StatTiles from "@/components/ui/StatTiles.vue"
import Card from "@/components/ui/Card.vue"
import DataTable from "@/components/ui/DataTable.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"
import FormDrawer from "@/components/ui/FormDrawer.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"
import { useCreate, useLinkOptions } from "@/composables/useDocActions"

const r = createResource({ url: "frappe_hr_ui.api.get_offers", auto: true })
const d = computed(() => r.data || {})

const add = useCreate("Job Offer", { onDone: () => r.reload(), successLabel: "Offer created" })
const applicants = useLinkOptions("Job Applicant")
const designations = useLinkOptions("Designation")
const form = reactive({ job_applicant: "", designation: "", offer_date: "" })
const fields = computed(() => [
  { key: "job_applicant", label: "Job applicant", type: "select", options: applicants.value, cols: 2 },
  { key: "designation", label: "Designation", type: "select", options: designations.value, cols: 1 },
  { key: "offer_date", label: "Offer date", type: "date", cols: 1 },
])
function openAdd() {
  Object.assign(form, { job_applicant: "", designation: "", offer_date: "" })
  add.openDrawer()
}
const TONE = { Accepted: "success", "Awaiting Response": "warning", Rejected: "danger", "Offer Sent": "warning" }
const tiles = computed(() => {
  const s = d.value.stats || {}
  return [
    { label: "Offers sent", value: s.sent ?? 0, sub: "in flight", icon: "file", tone: "accent" },
    { label: "Accepted", value: s.accepted ?? 0, sub: "joined/joining", icon: "check", tone: "success" },
  ]
})
const columns = [
  { key: "applicant_name", label: "Candidate" },
  { key: "designation", label: "Role" },
  { key: "sent", label: "Sent" },
  { key: "status", label: "Status" },
]
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Offer management" :subtitle="`${(d.offers || []).length} offers`">
      <template #actions><Button variant="solid" theme="blue" label="Create offer" @click="openAdd"><template #prefix><Icon name="plus" :size="15" /></template></Button></template>
    </PageHeader>
    <AsyncShell :resource="r" loading-text="Loading offers…">
    <StatTiles :items="tiles" :cols="4" />
    <Card class="!p-4">
      <DataTable :columns="columns" :rows="d.offers || []" row-key="name" :loading="r.loading" empty-title="No offers yet">
        <template #cell-applicant_name="{ row }"><div class="flex items-center gap-2.5"><InitialsAvatar :name="row.applicant_name" :size="30" /><span class="font-medium">{{ row.applicant_name }}</span></div></template>
        <template #cell-designation="{ row }"><span class="text-ink-gray-7">{{ row.designation }}</span></template>
        <template #cell-sent="{ row }"><span class="tnum">{{ row.sent }}</span></template>
        <template #cell-status="{ row }"><StatusBadge :tone="TONE[row.status] || 'neutral'" size="sm" dot :label="row.status" /></template>
      </DataTable>
    </Card>
    </AsyncShell>

    <FormDrawer :open="add.open" title="Create offer" subtitle="Send a job offer to an applicant"
      :fields="fields" v-model="form" :loading="add.create.loading" submit-label="Create offer"
      @close="add.open = false" @submit="add.submit(form, ['job_applicant', 'designation', 'offer_date'])" />
  </div>
</template>
