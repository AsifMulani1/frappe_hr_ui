<script setup>
import { ref, reactive, computed, watch } from "vue"
import { Button, FormControl, createResource, toast } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import DateField from "@/components/ui/DateField.vue"
import Tabs from "@/components/ui/Tabs.vue"
import DataTable from "@/components/ui/DataTable.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import ProgressBar from "@/components/ui/ProgressBar.vue"
import Drawer from "@/components/ui/Drawer.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"
import { LEAVE_THEME } from "@/composables/useEmployeeHome"

const r = createResource({ url: "frappe_hr_ui.api.get_employee_leave", auto: true })
const d = computed(() => r.data || {})
const tab = ref("upcoming")
const open = ref(false)

const leaveTypes = createResource({ url: "frappe_hr_ui.api.get_leave_types", auto: true })
const typeOptions = computed(() =>
  (leaveTypes.data?.types || []).map((t) => ({ label: t.balance != null ? `${t.label} (${t.balance} left)` : t.label, value: t.value }))
)
const form = reactive({ leave_type: "", from_date: "", to_date: "", reason: "" })

// live days + balance preview, computed by hrms
const preview = createResource({ url: "frappe_hr_ui.api.get_leave_days" })
watch(() => [form.leave_type, form.from_date, form.to_date], ([lt, f, t]) => {
  if (lt && f && t && t >= f) preview.fetch({ leave_type: lt, from_date: f, to_date: t })
})

const apply = createResource({
  url: "frappe_hr_ui.api.apply_leave",
  onSuccess() {
    toast.success("Leave application submitted")
    open.value = false
    Object.assign(form, { leave_type: "", from_date: "", to_date: "", reason: "" })
    r.reload()
  },
  onError(e) {
    toast.error(e?.messages?.[0] || "Couldn't submit leave")
  },
})
function submitLeave() {
  if (!form.leave_type || !form.from_date || !form.to_date) {
    toast.error("Pick a leave type and dates")
    return
  }
  if (form.to_date < form.from_date) {
    toast.error("The end date can't be before the start date")
    return
  }
  apply.submit({ ...form })
}

const TYPE_TONE = { "Casual Leave": "info", "Sick Leave": "success", "Earned Leave": "accent", "Comp Off": "warning" }
const STATUS_TONE = { Approved: "success", Open: "warning", Rejected: "danger", Cancelled: "neutral" }
const requests = computed(() => d.value.requests || [])
const filtered = computed(() =>
  tab.value === "upcoming" ? requests.value.filter((x) => x.status === "Open" || x.status === "Approved") : requests.value
)
const tabs = computed(() => [
  { id: "upcoming", label: "Upcoming & approved", count: requests.value.filter((x) => x.status === "Open" || x.status === "Approved").length },
  { id: "all", label: "All requests", count: requests.value.length },
])
const columns = [
  { key: "id", label: "Request", width: 120 },
  { key: "type", label: "Type" },
  { key: "dates", label: "Dates" },
  { key: "days", label: "Days", align: "right" },
  { key: "reason", label: "Reason" },
  { key: "applied", label: "Applied" },
  { key: "status", label: "Status" },
]
const totalLeft = computed(() => (d.value.balance || []).reduce((s, b) => s + (Number(b.balance) || 0), 0))
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Leave" subtitle="Apply for time off and track your requests">
      <template #actions>
        <Button variant="solid" theme="blue" label="Apply for Leave" @click="open = true"><template #prefix><Icon name="plus" :size="15" /></template></Button>
      </template>
    </PageHeader>

    <AsyncShell :resource="r" :has-employee="!!d.employee" loading-text="Loading your leave…">
    <div class="grid items-start gap-5" style="grid-template-columns: minmax(0,1fr) 340px">
      <Card :pad="false">
        <div class="px-5"><Tabs :tabs="tabs" v-model:active="tab" /></div>
        <div class="p-5">
          <DataTable :columns="columns" :rows="filtered" row-key="id" :loading="r.loading"
            empty-title="No leave requests" empty-message="Apply for leave and it'll show up here.">
            <template #cell-id="{ row }"><span class="tnum font-medium">{{ row.id }}</span></template>
            <template #cell-type="{ row }"><StatusBadge :tone="TYPE_TONE[row.type] || 'neutral'" size="sm" :label="row.type" /></template>
            <template #cell-dates="{ row }">{{ row.from }} → {{ row.to }}</template>
            <template #cell-days="{ row }"><span class="tnum">{{ row.days }}</span></template>
            <template #cell-reason="{ row }"><span class="text-ink-gray-7">{{ row.reason }}</span></template>
            <template #cell-applied="{ row }"><span class="text-ink-gray-5">{{ row.applied }}</span></template>
            <template #cell-status="{ row }"><StatusBadge :tone="STATUS_TONE[row.status] || 'neutral'" size="sm" dot :label="row.status" /></template>
          </DataTable>
        </div>
      </Card>

      <div class="flex flex-col gap-5">
        <Card>
          <CardHeader title="Leave Balance" sub="Current financial year" />
          <div class="mb-3 text-center">
            <div class="tnum text-7xl font-medium text-ink-gray-9">{{ totalLeft }}</div>
            <div class="text-xs text-ink-gray-5">days available</div>
          </div>
          <div class="flex flex-col gap-2.5">
            <div v-for="b in d.balance || []" :key="b.code" class="flex items-center gap-2.5">
              <span class="h-2.5 w-2.5 shrink-0 rounded-[3px]" :class="(LEAVE_THEME[b.color] || LEAVE_THEME.blue).dot" />
              <span class="flex-1 truncate text-sm text-ink-gray-7">{{ b.type }}</span>
              <span class="tnum whitespace-nowrap text-sm font-medium text-ink-gray-9">{{ b.balance }}<span class="font-normal text-ink-gray-5"> / {{ b.total }}</span></span>
            </div>
          </div>
        </Card>
        <Card>
          <CardHeader title="Team on Leave" sub="Next 7 days" />
          <div v-if="(d.who_is_out || []).length" class="flex flex-col gap-3">
            <div v-for="(p, i) in d.who_is_out" :key="i" class="flex items-center gap-2.5">
              <InitialsAvatar :name="p.name" :size="30" />
              <div class="min-w-0 flex-1"><div class="text-sm font-medium text-ink-gray-9">{{ p.name }}</div><div class="text-xs text-ink-gray-5">{{ p.note }}</div></div>
              <span class="text-xs text-ink-gray-5">{{ p.until }}</span>
            </div>
          </div>
          <div v-else class="py-3 text-center text-sm text-ink-gray-5">No one's out.</div>
        </Card>
      </div>
    </div>
    </AsyncShell>

    <Drawer :open="open" title="Apply for leave" subtitle="Request time off — your manager will be notified" :width="480" @close="open = false">
      <div class="flex flex-col gap-4">
        <FormControl type="select" label="Leave type" :options="typeOptions" v-model="form.leave_type" />
        <div class="grid grid-cols-2 gap-3">
          <DateField label="From" v-model="form.from_date" />
          <DateField label="To" v-model="form.to_date" />
        </div>
        <div v-if="preview.data && form.leave_type && form.from_date" class="flex items-center justify-between rounded-md bg-surface-gray-2 px-3 py-2 text-xs">
          <span class="text-ink-gray-7"><span class="font-medium text-ink-gray-9 tnum">{{ preview.data.days }}</span> day(s) requested</span>
          <span v-if="preview.data.balance != null" class="text-ink-gray-7"><span class="font-medium text-ink-gray-9 tnum">{{ preview.data.balance }}</span> available</span>
        </div>
        <FormControl type="textarea" label="Reason" placeholder="Add a reason (optional)…" v-model="form.reason" />
      </div>
      <template #footer>
        <Button variant="ghost" label="Cancel" @click="open = false" />
        <Button variant="solid" theme="blue" label="Submit Request" :loading="apply.loading" @click="submitLeave" />
      </template>
    </Drawer>
  </div>
</template>
