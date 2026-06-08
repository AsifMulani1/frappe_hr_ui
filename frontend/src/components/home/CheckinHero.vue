<script setup>
import { computed } from "vue"
import { Button, Badge, createResource } from "frappe-ui"
import Card from "@/components/ui/Card.vue"
import Icon from "@/components/ui/Icon.vue"
import Ring from "./Ring.vue"
import WeekStrip from "./WeekStrip.vue"
import { fmtMins } from "@/composables/useEmployeeHome"

const props = defineProps({
  today: { type: Object, default: () => ({}) },
  week: { type: Array, default: () => [] },
  summary: { type: Object, default: () => ({}) },
  shift: { type: String, default: "" },
  onReload: { type: Function, default: () => {} },
})

const checkedIn = computed(() => props.today?.checked_in)
const worked = computed(() => fmtMins(props.today?.worked_minutes))
const shiftHrs = computed(() => Math.round((props.today?.target_minutes || 540) / 60))

const toggle = createResource({
  url: "frappe_hr_ui.api.toggle_checkin",
  onSuccess: () => props.onReload(),
})
</script>

<template>
  <Card :pad="false" class="overflow-hidden">
    <div class="flex items-center justify-between border-b border-outline-gray-1 px-5 py-4">
      <div class="flex items-center gap-2.5">
        <div class="text-[15px] font-medium text-ink-gray-9">Today's attendance</div>
        <Badge v-if="shift" variant="subtle" theme="gray" size="sm" :label="shift" />
      </div>
      <Button variant="ghost" size="sm" label="View history">
        <template #suffix><Icon name="arrowRight" :size="15" /></template>
      </Button>
    </div>

    <div class="grid items-stretch" style="grid-template-columns: minmax(230px, 280px) 1px 1fr">
      <!-- ring + actions -->
      <div class="flex flex-col items-center gap-3.5 p-5">
        <div class="relative h-[116px] w-[116px]">
          <Ring :value="today?.worked_minutes || 0" :max="today?.target_minutes || 540" />
          <div class="absolute inset-0 flex flex-col items-center justify-center">
            <div class="tnum text-[22px] font-medium tracking-tight text-ink-gray-9">{{ worked }}</div>
            <div class="text-[11.5px] text-ink-gray-5">of {{ shiftHrs }}h shift</div>
          </div>
        </div>
        <div class="flex items-center gap-1.5">
          <span
            class="h-[7px] w-[7px] rounded-full"
            :class="checkedIn ? 'bg-green-500 ring-[3px] ring-green-100' : 'bg-ink-gray-4'"
          />
          <span class="text-[13px] text-ink-gray-7">
            <template v-if="checkedIn"
              >Checked in at <b class="font-medium text-ink-gray-9">{{ today?.first_in }}</b></template
            >
            <template v-else-if="today?.last_out"
              >Checked out at <b class="font-medium text-ink-gray-9">{{ today?.last_out }}</b></template
            >
            <template v-else>Not checked in yet</template>
          </span>
        </div>
        <div class="flex w-full gap-2">
          <Button
            class="flex-1"
            :variant="checkedIn ? 'subtle' : 'solid'"
            :theme="checkedIn ? 'red' : 'gray'"
            :loading="toggle.loading"
            :label="checkedIn ? 'Check out' : 'Check in'"
            @click="toggle.submit()"
          >
            <template #prefix><Icon :name="checkedIn ? 'logout' : 'login'" :size="15" /></template>
          </Button>
          <Button variant="outline" theme="gray" label="Break" />
        </div>
      </div>

      <div class="bg-outline-gray-1" />

      <!-- week + stats -->
      <div class="flex flex-col gap-4 p-5">
        <div class="flex items-center justify-between">
          <div class="text-[12.5px] font-medium text-ink-gray-5">This week</div>
          <button class="border-0 bg-transparent p-0 text-[12.5px] font-medium text-blue-600">
            Regularize
          </button>
        </div>
        <WeekStrip :week="week" />
        <div class="mt-0.5 grid grid-cols-3 gap-3">
          <div class="border-l-2 border-outline-gray-1 pl-3">
            <div class="text-[11.5px] text-ink-gray-5">Present</div>
            <div class="tnum mt-0.5 text-[17px] font-medium text-ink-gray-9">{{ summary?.present ?? 0 }} days</div>
            <div class="text-[11px] text-ink-gray-5">last 30 days</div>
          </div>
          <div class="border-l-2 border-outline-gray-1 pl-3">
            <div class="text-[11.5px] text-ink-gray-5">Avg hours</div>
            <div class="tnum mt-0.5 text-[17px] font-medium text-ink-gray-9">{{ summary?.avg_hours || "—" }}</div>
            <div class="text-[11px] text-ink-gray-5">per day</div>
          </div>
          <div class="border-l-2 border-outline-gray-1 pl-3">
            <div class="text-[11.5px] text-ink-gray-5">On leave</div>
            <div class="tnum mt-0.5 text-[17px] font-medium text-ink-gray-9">{{ summary?.leave ?? 0 }} days</div>
            <div class="text-[11px] text-ink-gray-5">this month</div>
          </div>
        </div>
      </div>
    </div>
  </Card>
</template>
