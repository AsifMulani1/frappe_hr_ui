<script setup>
import { computed } from "vue"
import { useRouter } from "vue-router"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import StatTiles from "@/components/ui/StatTiles.vue"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"

const router = useRouter()
const r = createResource({ url: "frappe_hr_ui.api.get_team_overview", auto: true })
const d = computed(() => r.data || {})
const ATT_TONE = { Present: "success", "On Leave": "warning", WFH: "accent", "Not in": "neutral" }
const tiles = computed(() => {
  const s = d.value.summary || {}
  return [
    { label: "Present today", value: `${s.present ?? 0} / ${s.total ?? 0}`, sub: `${s.on_leave ?? 0} on leave`, icon: "calcheck", tone: "success" },
    { label: "Pending approvals", value: s.approvals ?? 0, sub: "awaiting you", icon: "inbox", tone: "warning" },
    { label: "Team size", value: s.total ?? 0, sub: "direct reports", icon: "users", tone: "accent" },
    { label: "On leave", value: s.on_leave ?? 0, sub: "today", icon: "calendar", tone: "neutral" },
  ]
})
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Team Dashboard" :subtitle="`${(d.team || []).length} reports · ${d.manager?.employee_name || ''}`">
      <template #actions>
        <Button variant="solid" theme="blue" :label="`${d.summary?.approvals ?? 0} approvals`" @click="router.push({ name: 'MgrApprovals' })"><template #prefix><Icon name="inbox" :size="15" /></template></Button>
      </template>
    </PageHeader>
    <AsyncShell :resource="r" loading-text="Loading team…">
    <StatTiles :items="tiles" :cols="4" />
    <div class="grid items-start gap-5" style="grid-template-columns: minmax(0, 1fr) 320px">
      <div class="flex flex-col gap-5">
        <Card :pad="false">
          <div class="p-5 pb-3.5"><CardHeader title="Today's Attendance" sub="Live status" /></div>
          <div class="grid border-t border-outline-gray-1" style="grid-template-columns: repeat(auto-fill, minmax(150px, 1fr))">
            <div v-for="t in d.team || []" :key="t.name" class="flex flex-col gap-2 border-b border-r border-outline-gray-1 p-3.5">
              <div class="flex items-center gap-2">
                <InitialsAvatar :name="t.employee_name" :size="30" />
                <div class="min-w-0"><div class="truncate text-xs font-medium text-ink-gray-9">{{ t.employee_name.split(" ")[0] }}</div>
                  <div class="truncate text-2xs text-ink-gray-5">{{ t.today.in !== "—" ? "In " + t.today.in : (t.today.note || "—") }}</div></div>
              </div>
              <StatusBadge :tone="ATT_TONE[t.today.att] || 'neutral'" size="sm" dot :label="t.today.att" />
            </div>
          </div>
        </Card>
      </div>
      <div class="flex flex-col gap-5">
        <Card>
          <CardHeader title="Needs Approval" :sub="`${d.summary?.approvals ?? 0} pending`" icon="inbox">
            <template #action><Button variant="ghost" size="sm" label="All" @click="router.push({ name: 'MgrApprovals' })" /></template>
          </CardHeader>
          <div class="flex flex-col">
            <div v-for="(a, i) in d.approvals || []" :key="a.id" class="flex items-center gap-2.5 py-2.5" :class="i ? 'border-t border-outline-gray-1' : ''">
              <InitialsAvatar :name="a.person" :size="30" />
              <div class="min-w-0 flex-1"><div class="truncate text-sm font-medium text-ink-gray-9">{{ a.person }}</div>
                <div class="text-xs text-ink-gray-5">{{ a.detail }} · {{ a.amount }}</div></div>
              <StatusBadge :tone="a.tone" size="sm" :label="a.kind" />
            </div>
            <div v-if="!(d.approvals || []).length" class="py-3 text-center text-sm text-ink-gray-5">All caught up.</div>
          </div>
          <Button v-if="(d.approvals || []).length" variant="outline" theme="gray" class="mt-3.5 w-full" label="Review All" @click="router.push({ name: 'MgrApprovals' })" />
        </Card>
        <Card>
          <CardHeader title="Upcoming Team Leave" icon="calendar" />
          <div v-if="(d.upcoming_leave || []).length" class="flex flex-col gap-3">
            <div v-for="(u, i) in d.upcoming_leave" :key="i" class="flex items-center gap-2.5">
              <InitialsAvatar :name="u.employee_name" :size="30" />
              <div class="flex-1"><div class="text-sm font-medium text-ink-gray-9">{{ u.employee_name }}</div><div class="text-xs text-ink-gray-5">{{ u.leave_type }}</div></div>
              <span class="text-xs text-ink-gray-5">{{ u.when }}</span>
            </div>
          </div>
          <div v-else class="py-3 text-center text-sm text-ink-gray-5">No upcoming leave.</div>
        </Card>
      </div>
    </div>
    </AsyncShell>
  </div>
</template>
