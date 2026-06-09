<script setup>
import { computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import StatTiles from "@/components/ui/StatTiles.vue"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import Icon from "@/components/ui/Icon.vue"

const r = createResource({ url: "frappe_hr_ui.api.get_analytics", auto: true })
const d = computed(() => r.data || {})
const genderStr = computed(() => (d.value.gender || []).map(([g, n]) => `${n} ${g[0]}`).join(" · ") || "—")
const tiles = computed(() => [
  { label: "Headcount", value: d.value.headcount ?? 0, sub: "active", icon: "users", tone: "accent" },
  { label: "Departments", value: (d.value.dept_counts || []).length, sub: "teams", icon: "layers", tone: "neutral" },
  { label: "Gender split", value: genderStr, sub: "active", icon: "user", tone: "neutral" },
])
const maxDept = computed(() => Math.max(1, ...(d.value.dept_counts || []).map((x) => x[1])))
const maxTen = computed(() => Math.max(1, ...(d.value.tenure || []).map((x) => x[1])))
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="People analytics" subtitle="Workforce insights">
      <template #actions><Button variant="outline" theme="gray" label="Export"><template #prefix><Icon name="download" :size="15" /></template></Button></template>
    </PageHeader>
    <StatTiles :items="tiles" :cols="4" />
    <div class="grid grid-cols-2 gap-5">
      <Card>
        <CardHeader title="Headcount by department" />
        <div class="flex flex-col gap-2.5">
          <div v-for="[dn, n] in d.dept_counts || []" :key="dn" class="flex items-center gap-2.5">
            <div class="w-28 truncate text-[12.5px] text-ink-gray-7">{{ dn }}</div>
            <div class="h-4 flex-1 overflow-hidden rounded bg-surface-gray-2"><div class="h-full rounded bg-blue-500/85" :style="{ width: (n / maxDept * 100) + '%' }" /></div>
            <div class="tnum w-6 text-right text-[12.5px] font-medium">{{ n }}</div>
          </div>
        </div>
      </Card>
      <Card>
        <CardHeader title="Tenure distribution" />
        <div class="flex h-[160px] items-end gap-2.5 px-1">
          <div v-for="[l, n] in d.tenure || []" :key="l" class="flex flex-1 flex-col items-center gap-1.5">
            <div class="tnum text-[12px] font-medium">{{ n }}</div>
            <div class="w-full rounded-t bg-blue-500/85" :style="{ height: (n / maxTen * 100) + '%', minHeight: '6px' }" />
            <div class="text-[11px] text-ink-gray-5">{{ l }}</div>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>
