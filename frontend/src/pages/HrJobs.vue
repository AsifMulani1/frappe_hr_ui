<script setup>
import { computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import StatTiles from "@/components/ui/StatTiles.vue"
import Card from "@/components/ui/Card.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import EmptyState from "@/components/ui/EmptyState.vue"
import Icon from "@/components/ui/Icon.vue"

const r = createResource({ url: "frappe_hr_ui.api.get_jobs", auto: true })
const d = computed(() => r.data || {})
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
    <PageHeader title="Job openings" :subtitle="`${(d.jobs || []).length} requisitions`">
      <template #actions><Button variant="solid" theme="gray" label="New requisition"><template #prefix><Icon name="plus" :size="15" /></template></Button></template>
    </PageHeader>
    <StatTiles :items="tiles" :cols="4" />
    <EmptyState v-if="!(d.jobs || []).length && !r.loading" icon="briefcase" title="No job openings" message="Create a requisition to start hiring." />
    <div v-else class="grid gap-3.5" style="grid-template-columns: repeat(auto-fill, minmax(330px, 1fr))">
      <Card v-for="j in d.jobs" :key="j.name" hover class="!p-[18px]">
        <div class="mb-2.5 flex items-start justify-between">
          <div><div class="text-[15px] font-medium text-ink-gray-9">{{ j.job_title }}</div><div class="tnum mt-0.5 text-[12px] text-ink-gray-5">{{ j.name }}</div></div>
          <StatusBadge :tone="j.status === 'Open' ? 'success' : 'neutral'" size="sm" dot :label="j.status" />
        </div>
        <div class="mb-3.5 flex flex-wrap gap-1.5">
          <StatusBadge tone="neutral" size="sm" :label="j.dept" /><StatusBadge v-if="j.designation" tone="neutral" size="sm" :label="j.designation" />
        </div>
        <div class="flex items-center justify-between border-t border-outline-gray-1 pt-3.5">
          <div><div class="tnum text-[20px] font-medium">{{ j.apps }}</div><div class="text-[11px] text-ink-gray-5">applicants</div></div>
          <Button variant="outline" theme="gray" size="sm" label="View"><template #suffix><Icon name="chevRight" :size="15" /></template></Button>
        </div>
      </Card>
    </div>
  </div>
</template>
