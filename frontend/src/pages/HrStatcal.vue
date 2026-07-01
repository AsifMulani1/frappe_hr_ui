<script setup>
import { computed } from "vue"
import { createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import Icon from "@/components/ui/Icon.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"

const r = createResource({ url: "frappe_hr_ui.api.get_statcal", auto: true })
const events = computed(() => r.data?.events || [])
const TONE_BG = { danger: "border-red-100 bg-red-50 text-red-600", warning: "border-orange-100 bg-orange-50 text-orange-600", info: "border-blue-100 bg-blue-50 text-blue-600", accent: "border-blue-100 bg-blue-50 text-blue-600" }
</script>

<template>
  <div class="mx-auto max-w-[1100px] px-6 py-[22px]">
    <PageHeader title="Statutory Calendar" subtitle="Upcoming compliance deadlines" />
    <AsyncShell :resource="r" loading-text="Loading calendar…">
    <Card>
      <CardHeader title="Upcoming Deadlines" :sub="`${events.length} events`" icon="calendar" />
      <div class="flex flex-col">
        <div v-for="(e, i) in events" :key="i" class="flex gap-4 py-4" :class="i ? 'border-t border-outline-gray-1' : ''">
          <div class="w-14 shrink-0 rounded-md border py-1.5 text-center" :class="TONE_BG[e.tone]">
            <div class="tnum text-3xl font-medium leading-none">{{ e.date }}</div>
            <div class="mt-0.5 text-2xs uppercase tracking-[.03em]">{{ e.mon }}</div>
          </div>
          <div class="flex-1">
            <div class="mb-0.5 flex items-center gap-2"><span class="text-base font-medium text-ink-gray-9">{{ e.title }}</span><StatusBadge :tone="e.tone === 'info' ? 'info' : e.tone" size="sm" :label="e.tag" /></div>
          </div>
          <Icon name="chevRight" :size="16" class="self-center text-ink-gray-4" />
        </div>
      </div>
    </Card>
    </AsyncShell>
  </div>
</template>
