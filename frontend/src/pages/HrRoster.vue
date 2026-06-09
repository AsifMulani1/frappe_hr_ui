<script setup>
import { computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import EmptyState from "@/components/ui/EmptyState.vue"
import Icon from "@/components/ui/Icon.vue"

const r = createResource({ url: "frappe_hr_ui.api.get_roster", auto: true })
const shifts = computed(() => r.data?.shifts || [])
const COLORS = ["#0289F7", "#0B9E92", "#DB7706", "#8642C2"]
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Shift & roster" subtitle="Plan and assign shifts">
      <template #actions><Button variant="solid" theme="gray" label="Assign shift"><template #prefix><Icon name="plus" :size="15" /></template></Button></template>
    </PageHeader>
    <div v-if="shifts.length" class="mb-5 grid grid-cols-4 gap-5">
      <Card v-for="(s, i) in shifts" :key="s.name" class="!p-4">
        <div class="mb-2 flex items-center gap-2"><span class="h-2.5 w-2.5 rounded-[3px]" :style="{ background: COLORS[i % 4] }" /><span class="text-[13.5px] font-medium">{{ s.name }}</span></div>
        <div class="tnum text-[12.5px] text-ink-gray-5">{{ s.time }}</div>
        <div class="tnum mt-2 text-[22px] font-medium">{{ s.emp }}<span class="text-[12px] font-normal text-ink-gray-5"> assigned</span></div>
      </Card>
    </div>
    <Card v-else><EmptyState icon="calendar" title="No shift types defined" message="Create shift types to plan rosters." compact /></Card>
  </div>
</template>
