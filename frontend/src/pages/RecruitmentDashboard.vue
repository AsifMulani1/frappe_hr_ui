<script setup>
import { computed } from "vue"
import { useRouter } from "vue-router"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import StatTiles from "@/components/ui/StatTiles.vue"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import Icon from "@/components/ui/Icon.vue"
import EmptyState from "@/components/ui/EmptyState.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"

const router = useRouter()
const r = createResource({ url: "frappe_hr_ui.api.get_recruitment_dashboard", auto: true })
const d = computed(() => r.data || {})
const s = computed(() => d.value.stats || {})

const tiles = computed(() => [
  { label: "Open positions", value: s.value.open_jobs ?? 0, sub: `of ${s.value.total_jobs ?? 0} total`, icon: "briefcase", tone: "accent" },
  { label: "Applicants", value: s.value.applicants ?? 0, sub: "in pipeline", icon: "users", tone: "neutral" },
  { label: "Interviews", value: s.value.interviews ?? 0, sub: "scheduled", icon: "calendar", tone: "neutral" },
  { label: "Offers", value: s.value.offers ?? 0, sub: `${s.value.hired ?? 0} accepted`, icon: "file", tone: "warning" },
])
const maxFunnel = computed(() => Math.max(1, ...(d.value.funnel || []).map((x) => x[1])))
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Recruitment Dashboard" :subtitle="`Hiring · ${s.open_jobs ?? 0} open positions`">
      <template #actions><Button variant="solid" theme="blue" label="Job Openings" @click="router.push({ name: 'HrJobs' }).catch(() => {})"><template #prefix><Icon name="briefcase" :size="15" /></template></Button></template>
    </PageHeader>
    <AsyncShell :resource="r" loading-text="Loading recruitment…">
      <StatTiles :items="tiles" :cols="4" />
      <div class="grid items-start gap-5" style="grid-template-columns: minmax(0,1fr) 340px">
        <div class="flex flex-col gap-5">
          <Card>
            <CardHeader title="Hiring Funnel" :sub="`${s.applicants ?? 0} applicants`">
              <template #action><Button variant="ghost" size="sm" label="Pipeline" @click="router.push({ name: 'HrPipeline' }).catch(() => {})" /></template>
            </CardHeader>
            <div class="flex items-stretch gap-0">
              <div v-for="[l, n] in d.funnel || []" :key="l" class="flex-1 text-center">
                <div class="flex h-[70px] items-end justify-center px-1.5"><div class="w-full rounded-t bg-blue-500/85" :style="{ height: (n / maxFunnel * 100) + '%', minHeight: '8px' }" /></div>
                <div class="tnum mt-1.5 text-xl font-medium">{{ n }}</div>
                <div class="text-xs text-ink-gray-5">{{ l }}</div>
              </div>
            </div>
          </Card>
          <Card>
            <CardHeader title="Open Positions">
              <template #action><Button variant="ghost" size="sm" label="All Jobs" @click="router.push({ name: 'HrJobs' }).catch(() => {})" /></template>
            </CardHeader>
            <div v-if="(d.open_positions || []).length" class="flex flex-col">
              <Button v-for="j in d.open_positions" :key="j.name" variant="ghost" @click="router.push({ name: 'HrPipeline' }).catch(() => {})"
                class="w-full !justify-start border-t border-outline-gray-1 text-left first:border-t-0">
                <div class="flex w-full items-center gap-3">
                  <div class="min-w-0 flex-1">
                    <div class="truncate text-sm font-medium text-ink-gray-9">{{ j.job_title || j.designation || j.name }}</div>
                    <div class="text-xs text-ink-gray-5">{{ j.dept || "—" }}</div>
                  </div>
                  <span class="tnum rounded-full bg-surface-gray-2 px-2 py-0.5 text-xs font-medium text-ink-gray-7">{{ j.apps }} applicants</span>
                </div>
              </Button>
            </div>
            <EmptyState v-else icon="briefcase" title="No open positions" compact />
          </Card>
        </div>
        <Card>
          <CardHeader title="Upcoming Interviews" icon="calendar" />
          <div v-if="(d.upcoming || []).length" class="flex flex-col">
            <div v-for="(iv, i) in d.upcoming" :key="i" class="flex items-center gap-3 border-t border-outline-gray-1 py-3 first:border-t-0">
              <div class="flex h-[30px] w-[30px] items-center justify-center rounded-md bg-surface-gray-2 text-ink-gray-7"><Icon name="calendar" :size="15" /></div>
              <div class="min-w-0 flex-1"><div class="truncate text-sm font-medium text-ink-gray-9">{{ iv.cand }}</div><div class="text-xs text-ink-gray-5">{{ iv.round }}</div></div>
              <span class="tnum text-xs text-ink-gray-6">{{ iv.when }}</span>
            </div>
          </div>
          <EmptyState v-else icon="calendar" title="Nothing scheduled" compact />
        </Card>
      </div>
    </AsyncShell>
  </div>
</template>
