<script setup>
import { reactive, computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import StatTiles from "@/components/ui/StatTiles.vue"
import Card from "@/components/ui/Card.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import EmptyState from "@/components/ui/EmptyState.vue"
import Icon from "@/components/ui/Icon.vue"
import FormDrawer from "@/components/ui/FormDrawer.vue"
import DetailDrawer from "@/components/ui/DetailDrawer.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"
import { useCreate, useLinkOptions } from "@/composables/useDocActions"

const r = createResource({ url: "frappe_hr_ui.api.get_jobs", auto: true })
const d = computed(() => r.data || {})

// Create requisition (in-app)
const add = useCreate("Job Opening", { onDone: () => r.reload(), successLabel: "Requisition created" })
const designations = useLinkOptions("Designation")
const departments = useLinkOptions("Department")
const form = reactive({ job_title: "", designation: "", department: "", status: "Open" })
const fields = computed(() => [
  { key: "job_title", label: "Job title", type: "text", placeholder: "e.g. Senior Backend Engineer", cols: 2 },
  { key: "designation", label: "Designation", type: "select", options: designations.value, cols: 1 },
  { key: "department", label: "Department", type: "select", options: departments.value, cols: 1 },
  { key: "status", label: "Status", type: "select", options: ["Open", "Closed"], cols: 1 },
])
function openAdd() {
  Object.assign(form, { job_title: "", designation: "", department: "", status: "Open" })
  add.openDrawer()
}

// In-app detail view
const view = reactive({ open: false, name: "" })
function openView(j) {
  view.name = j.name
  view.open = true
}

const tiles = computed(() => {
  const s = d.value.stats || {}
  return [
    { label: "Open positions", value: s.open ?? 0, sub: "active reqs", icon: "briefcase", tone: "accent" },
    { label: "Total applicants", value: s.applicants ?? 0, sub: "in pipeline", icon: "users", tone: "neutral" },
    { label: "Offers", value: s.offers ?? 0, sub: "in flight", icon: "file", tone: "warning" },
  ]
})
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Job Openings" :subtitle="`${(d.jobs || []).length} requisitions`">
      <template #actions><Button variant="solid" theme="blue" label="New Requisition" @click="openAdd"><template #prefix><Icon name="plus" :size="15" /></template></Button></template>
    </PageHeader>
    <AsyncShell :resource="r" loading-text="Loading job openings…">
    <StatTiles :items="tiles" :cols="4" />
    <EmptyState v-if="!(d.jobs || []).length && !r.loading" icon="briefcase" title="No job openings" message="Create a requisition to start hiring." />
    <div v-else class="grid gap-3.5" style="grid-template-columns: repeat(auto-fill, minmax(330px, 1fr))">
      <Card v-for="j in d.jobs" :key="j.name" hover class="!p-[18px]">
        <div class="mb-2.5 flex items-start justify-between">
          <div><div class="text-md font-medium text-ink-gray-9">{{ j.job_title }}</div><div class="tnum mt-0.5 text-xs text-ink-gray-5">{{ j.name }}</div></div>
          <StatusBadge :tone="j.status === 'Open' ? 'success' : 'neutral'" size="sm" dot :label="j.status" />
        </div>
        <div class="mb-3.5 flex flex-wrap gap-1.5">
          <StatusBadge tone="neutral" size="sm" :label="j.dept" /><StatusBadge v-if="j.designation" tone="neutral" size="sm" :label="j.designation" />
        </div>
        <div class="flex items-center justify-between border-t border-outline-gray-1 pt-3.5">
          <div><div class="tnum text-3xl font-medium">{{ j.apps }}</div><div class="text-2xs text-ink-gray-5">applicants</div></div>
          <Button variant="outline" theme="gray" size="sm" label="View" @click="openView(j)"><template #suffix><Icon name="chevRight" :size="15" /></template></Button>
        </div>
      </Card>
    </div>
    </AsyncShell>

    <FormDrawer :open="add.open" title="New Requisition" subtitle="Open a new position for hiring"
      :fields="fields" v-model="form" :loading="add.create.loading" submit-label="Create Requisition"
      @close="add.open = false" @submit="add.submit(form, ['job_title', 'designation'])" />
    <DetailDrawer :open="view.open" doctype="Job Opening" :name="view.name" @close="view.open = false" />
  </div>
</template>
