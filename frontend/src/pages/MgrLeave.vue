<script setup>
import { computed } from "vue"
import { createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"

const r = createResource({ url: "frappe_hr_ui.api.get_team_leave", auto: true })
const d = computed(() => r.data || {})
const days = computed(() => Array.from({ length: d.value.days_in_month || 30 }, (_, i) => i + 1))
function isWeekend(day) {
  // approximate from today anchor not available; mark Sat/Sun via day-of-week unknown — skip shading
  return false
}
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Team Leave" :subtitle="`${d.month || ''} · plan coverage across your team`" />
    <AsyncShell :resource="r" loading-text="Loading team leave…">
    <Card :pad="false" class="overflow-hidden">
      <div class="flex items-center justify-between border-b border-outline-gray-1 px-5 py-4">
        <CardHeader title="Leave Calendar" sub="Approved leave this month" />
        <div class="flex gap-3.5">
          <span v-for="[l, c] in [['CL', '#0289F7'], ['SL', '#0B9E92'], ['EL', '#8642C2']]" :key="l" class="inline-flex items-center gap-1.5 text-xs text-ink-gray-7">
            <span class="h-2.5 w-2.5 rounded-[3px]" :style="{ background: c }" />{{ l }}
          </span>
        </div>
      </div>
      <div class="overflow-x-auto">
        <div style="min-width: 900px">
          <div class="grid border-b border-outline-gray-1" :style="{ gridTemplateColumns: `180px repeat(${days.length}, 1fr)` }">
            <div class="bg-surface-gray-1 px-3 py-2 text-xs font-medium text-ink-gray-5">Employee</div>
            <div v-for="day in days" :key="day" class="py-2 text-center text-2xs tnum" :class="day === d.today ? 'font-semibold text-blue-600' : 'text-ink-gray-5'">{{ day }}</div>
          </div>
          <div v-for="(t, ri) in d.team || []" :key="t.name" class="grid" :class="ri < (d.team || []).length - 1 ? 'border-b border-outline-gray-1' : ''" :style="{ gridTemplateColumns: `180px repeat(${days.length}, 1fr)` }">
            <div class="flex items-center gap-2 border-r border-outline-gray-1 px-3 py-2">
              <InitialsAvatar :name="t.employee_name" :size="24" />
              <span class="truncate text-xs font-medium text-ink-gray-9">{{ t.employee_name }}</span>
            </div>
            <div v-for="day in days" :key="day" class="flex h-9 items-center px-0.5 py-1.5">
              <div v-if="d.leave_map[t.name] && d.leave_map[t.name].days.includes(day)"
                class="flex h-[22px] w-full items-center justify-center text-2xs font-semibold text-white"
                :class="[
                  !d.leave_map[t.name].days.includes(day - 1) ? 'rounded-l-[5px]' : '',
                  !d.leave_map[t.name].days.includes(day + 1) ? 'rounded-r-[5px]' : '',
                ]"
                :style="{ background: d.leave_map[t.name].color, opacity: 0.9 }">
                {{ !d.leave_map[t.name].days.includes(day - 1) ? d.leave_map[t.name].type : "" }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Card>
    </AsyncShell>
  </div>
</template>
