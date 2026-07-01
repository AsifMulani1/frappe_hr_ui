<script setup>
import { ref, reactive, computed } from "vue"
import { Button, FormControl, createResource, toast } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import StatTiles from "@/components/ui/StatTiles.vue"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import SectionLabel from "@/components/ui/SectionLabel.vue"
import DataTable from "@/components/ui/DataTable.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import Drawer from "@/components/ui/Drawer.vue"
import DateField from "@/components/ui/DateField.vue"
import Icon from "@/components/ui/Icon.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"
import { downloadCSV } from "@/utils/actions"

const r = createResource({ url: "frappe_hr_ui.api.get_employee_attendance", auto: true })
const d = computed(() => r.data || {})
const open = ref(false)

const form = reactive({ from_date: "", reason: "Work From Home", explanation: "" })
const submit = createResource({
  url: "frappe_hr_ui.api.submit_regularization",
  onSuccess() {
    toast.success("Regularization submitted")
    open.value = false
    Object.assign(form, { from_date: "", reason: "Work From Home", explanation: "" })
    r.reload()
  },
  onError(e) { toast.error(e?.messages?.[0] || "Couldn't submit") },
})
function submitReg() {
  if (!form.from_date) { toast.error("Pick a date"); return }
  if (form.from_date > new Date().toISOString().slice(0, 10)) { toast.error("You can't regularize a future date"); return }
  submit.submit({ ...form })
}

const STATUS_TONE = {
  Present: "success", "Work From Home": "accent", "On Leave": "warning",
  "Half Day": "warning", Absent: "danger",
}
const tiles = computed(() => {
  const s = d.value.summary || {}
  return [
    { label: "Present", value: `${s.present ?? 0} days`, sub: "last 30 days", icon: "calcheck", tone: "success" },
    { label: "Avg hours / day", value: s.avg_hours || "—", sub: "worked", icon: "clock", tone: "accent" },
    { label: "On leave", value: `${s.leave ?? 0} days`, sub: "last 30 days", icon: "calendar", tone: "warning" },
    { label: "WFH days", value: s.wfh ?? 0, sub: "last 30 days", icon: "home", tone: "neutral" },
  ]
})
const columns = [
  { key: "date", label: "Date", width: 130 },
  { key: "in", label: "Check in", align: "right" },
  { key: "out", label: "Check out", align: "right" },
  { key: "hrs", label: "Hours", align: "right" },
  { key: "mode", label: "Mode" },
  { key: "status", label: "Status" },
]

const CAL_TONE = {
  Present: "border-green-100 bg-green-50 text-green-700",
  "Work From Home": "border-blue-100 bg-blue-50 text-blue-700",
  "On Leave": "border-orange-100 bg-orange-50 text-orange-700",
  "Half Day": "border-purple-100 bg-purple-50 text-purple-700",
  Absent: "border-red-100 bg-red-50 text-red-700",
}
const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
const monthStart = computed(() => { const t = new Date(); return new Date(t.getFullYear(), t.getMonth(), 1) })
const leadingBlanks = computed(() => (monthStart.value.getDay() + 6) % 7) // Mon-first
const daysInMonth = computed(() => new Date(monthStart.value.getFullYear(), monthStart.value.getMonth() + 1, 0).getDate())
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Attendance" subtitle="Your check-in history, hours, and regularization requests">
      <template #actions>
        <Button variant="outline" theme="gray" label="Export" @click="downloadCSV('my-attendance', columns, d.logs || [])"><template #prefix><Icon name="download" :size="15" /></template></Button>
        <Button variant="solid" theme="blue" label="Regularize" @click="open = true"><template #prefix><Icon name="clock" :size="15" /></template></Button>
      </template>
    </PageHeader>

    <AsyncShell :resource="r" :has-employee="!!d.employee" loading-text="Loading attendance…">
    <StatTiles :items="tiles" :cols="4" />

    <div class="grid items-start gap-5" style="grid-template-columns: minmax(0,1fr) 380px">
      <div>
        <SectionLabel label="Daily Log" />
        <DataTable :columns="columns" :rows="d.logs || []" row-key="date" :loading="r.loading"
          empty-title="No attendance yet" empty-message="Your daily check-in records will appear here.">
          <template #cell-date="{ row }"><span class="font-medium">{{ row.date }}</span></template>
          <template #cell-in="{ row }"><span class="tnum">{{ row.in }}</span></template>
          <template #cell-out="{ row }"><span class="tnum">{{ row.out }}</span></template>
          <template #cell-hrs="{ row }"><span class="tnum">{{ row.hrs }}</span></template>
          <template #cell-mode="{ row }">
            <StatusBadge v-if="row.mode !== '—'" tone="neutral" size="sm" :label="row.mode" />
            <span v-else class="text-ink-gray-5">—</span>
          </template>
          <template #cell-status="{ row }">
            <StatusBadge :tone="STATUS_TONE[row.status] || 'neutral'" size="sm" dot :label="row.status" />
          </template>
        </DataTable>
      </div>

      <Card>
        <CardHeader :title="d.month" sub="Attendance calendar" />
        <div class="grid grid-cols-7 gap-1.5">
          <div v-for="dd in days" :key="dd" class="pb-1 text-center text-xs font-medium text-ink-gray-5">{{ dd }}</div>
          <div v-for="b in leadingBlanks" :key="'b' + b" />
          <div v-for="day in daysInMonth" :key="day"
            class="min-h-[52px] rounded-md border p-1.5"
            :class="[CAL_TONE[d.calendar?.[day]] || 'border-outline-gray-1 bg-surface-base text-ink-gray-5', day === d.today ? 'outline outline-1 outline-blue-500' : '']">
            <div class="tnum text-xs font-medium text-ink-gray-9">{{ day }}</div>
            <div v-if="d.calendar?.[day]" class="mt-1 text-2xs font-medium leading-tight">
              {{ ({ "Present": "Present", "Work From Home": "WFH", "On Leave": "Leave", "Half Day": "½ day", "Absent": "Absent" })[d.calendar[day]] }}
            </div>
          </div>
        </div>
      </Card>
    </div>
    </AsyncShell>

    <Drawer :open="open" title="Regularize Attendance" subtitle="Request a correction for a missed or incorrect punch" @close="open = false">
      <div class="flex flex-col gap-4">
        <DateField label="Date" v-model="form.from_date" />
        <FormControl type="select" label="Reason" :options="['Work From Home', 'On Duty']" v-model="form.reason" />
        <FormControl type="textarea" label="Explanation" placeholder="Add context for your manager…" v-model="form.explanation" />
      </div>
      <template #footer>
        <Button variant="ghost" label="Cancel" @click="open = false" />
        <Button variant="solid" theme="blue" label="Submit Request" :loading="submit.loading" @click="submitReg" />
      </template>
    </Drawer>
  </div>
</template>
