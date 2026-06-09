<script setup>
import { computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import StatTiles from "@/components/ui/StatTiles.vue"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import Icon from "@/components/ui/Icon.vue"

const r = createResource({ url: "frappe_hr_ui.api.get_appraisal_cycle", auto: true })
const d = computed(() => r.data || {})
const tiles = computed(() => [
  { label: "Self-appraisals", value: `${d.value.submitted ?? 0} / ${d.value.total ?? 0}`, sub: "submitted", icon: "check", tone: "accent" },
  { label: "Manager reviews", value: `0 / ${d.value.total ?? 0}`, sub: "pending", icon: "target", tone: "neutral" },
  { label: "Employees", value: d.value.total ?? 0, sub: "in cycle", icon: "users", tone: "success" },
])
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader :title="`Appraisal cycle${d.cycle ? ' — ' + d.cycle.name : ''}`" subtitle="Review progress across the company">
      <template #actions><Button variant="solid" theme="gray" label="Send reminders"><template #prefix><Icon name="bell" :size="15" /></template></Button></template>
    </PageHeader>
    <StatTiles :items="tiles" :cols="4" />
    <Card>
      <CardHeader title="Cycle progress" sub="5 stages" />
      <div class="flex flex-col">
        <div v-for="([t, s, state, prog], i) in d.stages || []" :key="t" class="flex items-stretch gap-3.5">
          <div class="flex flex-col items-center">
            <div class="flex h-[26px] w-[26px] items-center justify-center rounded-full text-[11px] font-medium"
              :class="state === 'done' ? 'bg-green-500 text-white' : state === 'active' ? 'bg-blue-500 text-white' : 'border-[1.5px] border-outline-gray-2 text-ink-gray-5'">
              <Icon v-if="state === 'done'" name="check" :size="13" :stroke-width="3" /><span v-else>{{ i + 1 }}</span>
            </div>
            <div v-if="i < (d.stages || []).length - 1" class="min-h-[20px] w-0.5 flex-1" :class="state === 'done' ? 'bg-green-500' : 'bg-outline-gray-1'" />
          </div>
          <div class="flex flex-1 items-start justify-between pb-4.5">
            <div><div class="text-[14px] font-medium" :class="state === 'todo' ? 'text-ink-gray-5' : 'text-ink-gray-9'">{{ t }}</div>
              <div class="mt-px text-[12px]" :class="state === 'active' ? 'text-blue-600' : 'text-ink-gray-5'">{{ s }}</div></div>
            <span class="tnum text-[12.5px] font-medium text-ink-gray-7">{{ prog }}</span>
          </div>
        </div>
      </div>
    </Card>
  </div>
</template>
