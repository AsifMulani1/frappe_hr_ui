<script setup>
import { computed } from "vue"
import { createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"

const r = createResource({ url: "frappe_hr_ui.api.get_calibration", auto: true })
const boxes = computed(() => r.data?.boxes || [])
function color(b) {
  const score = (2 - b.r) + b.c
  if (score >= 3) return "border-green-100 bg-green-50 text-green-700"
  if (score === 2) return "border-blue-100 bg-blue-50 text-blue-700"
  if (score === 1) return "border-orange-100 bg-orange-50 text-orange-700"
  return "border-red-100 bg-red-50 text-red-700"
}
</script>

<template>
  <div class="mx-auto max-w-[1100px] px-6 py-[22px]">
    <PageHeader title="Calibration — 9-box grid" :subtitle="`${r.data?.total ?? 0} employees plotted by performance & potential`" />
    <AsyncShell :resource="r" loading-text="Loading calibration…">
    <Card>
      <div class="flex gap-3.5">
        <div class="flex items-center pb-7 pr-1"><span class="text-[11.5px] font-medium text-ink-gray-5" style="writing-mode: vertical-rl; transform: rotate(180deg)">Performance →</span></div>
        <div class="flex-1">
          <div class="grid grid-cols-3 gap-2.5">
            <div v-for="b in boxes" :key="`${b.r}-${b.c}`" class="flex min-h-[110px] flex-col justify-between rounded-md border p-3.5" :class="color(b)">
              <div class="text-[11.5px] font-medium">{{ b.label }}</div>
              <div><div class="tnum text-[26px] font-medium">{{ b.n }}</div><div class="text-[11px] text-ink-gray-5">employees</div></div>
            </div>
          </div>
          <div class="mt-2.5 text-center text-[11.5px] font-medium text-ink-gray-5">Potential →</div>
        </div>
      </div>
    </Card>
    </AsyncShell>
  </div>
</template>
