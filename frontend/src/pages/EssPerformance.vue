<script setup>
import { computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import StatTiles from "@/components/ui/StatTiles.vue"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import ProgressBar from "@/components/ui/ProgressBar.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import EmptyState from "@/components/ui/EmptyState.vue"
import Icon from "@/components/ui/Icon.vue"

const r = createResource({ url: "frappe_hr_ui.api.get_employee_performance", auto: true })
const d = computed(() => r.data || {})
const goals = computed(() => d.value.goals || [])
const tiles = computed(() => [
  { label: "Overall progress", value: `${d.value.overall || 0}%`, sub: "weighted", icon: "target", tone: "accent" },
  { label: "Goals", value: goals.value.length, sub: "this cycle", icon: "check", tone: "neutral" },
  { label: "Cycle", value: d.value.cycle ? "Active" : "—", sub: d.value.cycle || "no cycle", icon: "chart", tone: "success" },
  { label: "Self-appraisal", value: "Open", sub: "in progress", icon: "calendar", tone: "warning" },
])
function barColor(p) { return p >= 70 ? "bg-green-500" : p >= 40 ? "bg-blue-500" : "bg-orange-500" }
function tone(p) { return p >= 70 ? "success" : p >= 40 ? "accent" : "warning" }
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Performance" :subtitle="d.cycle ? `${d.cycle} cycle · goals, check-ins and appraisal` : 'Goals, check-ins and appraisal'">
      <template #actions>
        <Button variant="outline" theme="gray" label="Request feedback"><template #prefix><Icon name="users" :size="15" /></template></Button>
        <Button variant="solid" theme="gray" label="Start self-appraisal"><template #prefix><Icon name="edit" :size="15" /></template></Button>
      </template>
    </PageHeader>
    <StatTiles :items="tiles" :cols="4" />
    <Card>
      <CardHeader title="Goals & key results" sub="Weighted by impact" />
      <div v-if="goals.length">
        <div v-for="(g, i) in goals" :key="i" class="border-t border-outline-gray-1 py-4 first:border-t-0">
          <div class="flex items-start justify-between gap-3">
            <div class="flex-1">
              <div class="flex items-center gap-2">
                <span class="text-[14px] font-medium text-ink-gray-9">{{ g.title }}</span>
                <StatusBadge :tone="tone(g.progress)" size="sm" :label="g.progress >= 70 ? 'On track' : g.progress >= 40 ? 'At risk' : 'Behind'" />
              </div>
              <div class="mt-1 text-[12.5px] text-ink-gray-5">Weight {{ g.weight }}%</div>
            </div>
            <div class="tnum text-[18px] font-medium text-ink-gray-9">{{ g.progress }}%</div>
          </div>
          <div class="mt-2.5"><ProgressBar :value="g.progress" :color="barColor(g.progress)" /></div>
        </div>
      </div>
      <EmptyState v-else icon="target" title="No goals set for this cycle" message="Goals from your appraisal will appear here once the cycle starts." />
    </Card>
  </div>
</template>
