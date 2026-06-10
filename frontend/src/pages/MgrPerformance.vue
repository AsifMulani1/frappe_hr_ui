<script setup>
import { reactive, computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import ProgressBar from "@/components/ui/ProgressBar.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import EmptyState from "@/components/ui/EmptyState.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"
import FormDrawer from "@/components/ui/FormDrawer.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"
import { useCreate, useLinkOptions } from "@/composables/useDocActions"

const r = createResource({ url: "frappe_hr_ui.api.get_team_performance", auto: true })
const team = computed(() => r.data?.team || [])

// Start reviews (in-app)
const add = useCreate("Appraisal", { onDone: () => r.reload(), successLabel: "Appraisal created" })
const employees = useLinkOptions("Employee")
const cycles = useLinkOptions("Appraisal Cycle")
const form = reactive({ employee: "", appraisal_cycle: "" })
const fields = computed(() => [
  { key: "employee", label: "Employee", type: "select", options: employees.value, cols: 2 },
  { key: "appraisal_cycle", label: "Appraisal cycle", type: "select", options: cycles.value, cols: 2 },
])
function openAdd() {
  Object.assign(form, { employee: "", appraisal_cycle: "" })
  add.openDrawer()
}
function barColor(p) { return p >= 70 ? "bg-green-500" : p >= 50 ? "bg-blue-500" : "bg-orange-500" }
function tone(p) { return p >= 70 ? "success" : p >= 50 ? "accent" : "warning" }
function label(p) { return p >= 70 ? "On track" : p >= 50 ? "Steady" : "Needs focus" }
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Team performance" subtitle="Goal progress and ratings across your reports">
      <template #actions><Button variant="solid" theme="blue" label="Start reviews" @click="openAdd"><template #prefix><Icon name="target" :size="15" /></template></Button></template>
    </PageHeader>
    <AsyncShell :resource="r" loading-text="Loading team performance…">
    <Card :pad="false">
      <div class="p-5">
        <CardHeader title="Reports" sub="Goal progress and current cycle status" />
        <EmptyState v-if="!team.length && !r.loading" icon="target" title="No appraisals yet" message="Goal progress shows once the cycle starts." />
        <div v-else class="flex flex-col">
          <div v-for="(t, i) in team" :key="t.name" class="flex items-center gap-4 py-3.5" :class="i ? 'border-t border-outline-gray-1' : ''">
            <InitialsAvatar :name="t.name" :size="36" />
            <div class="w-40 min-w-0"><div class="truncate text-[13.5px] font-medium text-ink-gray-9">{{ t.name }}</div><div class="text-[11.5px] text-ink-gray-5">{{ t.designation }}</div></div>
            <div class="max-w-[240px] flex-1">
              <div class="mb-1.5 flex justify-between"><span class="text-[11.5px] text-ink-gray-5">Goal progress</span><span class="tnum text-[12px] font-medium">{{ t.progress }}%</span></div>
              <ProgressBar :value="t.progress" :color="barColor(t.progress)" />
            </div>
            <div class="w-[70px] text-center"><div class="text-[11.5px] text-ink-gray-5">Rating</div><div class="tnum text-[15px] font-medium">{{ t.rating ?? "—" }}</div></div>
            <StatusBadge :tone="tone(t.progress)" size="sm" :label="label(t.progress)" />
          </div>
        </div>
      </div>
    </Card>
    </AsyncShell>

    <FormDrawer :open="add.open" title="Start reviews" subtitle="Create an appraisal for the cycle"
      :fields="fields" v-model="form" :loading="add.create.loading" submit-label="Create appraisal"
      @close="add.open = false" @submit="add.submit(form, ['employee', 'appraisal_cycle'])" />
  </div>
</template>
