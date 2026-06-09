<script setup>
import { ref, computed, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import Tabs from "@/components/ui/Tabs.vue"
import Field from "@/components/ui/Field.vue"
import SectionLabel from "@/components/ui/SectionLabel.vue"
import AmountRow from "@/components/ui/AmountRow.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"
import { formatINR } from "@/utils/formatters"

const route = useRoute(); const router = useRouter()
const r = createResource({ url: "frappe_hr_ui.api.get_employee_360" })
const tab = ref("overview")
function load() { if (route.query.id) r.fetch({ name: route.query.id }) }
watch(() => route.query.id, load, { immediate: true })
const e = computed(() => r.data?.employee || {})
const grid = "grid grid-cols-3 gap-x-6 gap-y-[18px]"
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader back="Employee directory" title="Employee 360" subtitle="Complete record · HR admin view" @back="router.push({ name: 'HrDirectory' })" />
    <div v-if="!e.name && !r.loading" class="py-16 text-center text-[13px] text-ink-gray-5">Open an employee from the directory.</div>
    <template v-else>
      <Card :pad="false" class="mb-5">
        <div class="flex flex-wrap items-center gap-[18px] p-5">
          <InitialsAvatar :name="e.employee_name" :image="e.image" :size="64" />
          <div class="min-w-[200px] flex-1">
            <div class="flex items-center gap-2.5"><h2 class="text-[19px] font-medium text-ink-gray-9">{{ e.employee_name }}</h2>
              <StatusBadge tone="success" size="sm" dot label="Active" /><StatusBadge v-if="e.grade" tone="neutral" size="sm" :label="e.grade" /></div>
            <div class="mt-0.5 text-[13px] text-ink-gray-7">{{ e.designation }} · {{ (e.department || '').split(' - ')[0] }} · {{ e.location }}</div>
            <div class="tnum mt-1 text-[12.5px] text-ink-gray-5">{{ e.employee_number }} · Reports to {{ e.manager_name || '—' }}</div>
          </div>
          <div class="flex gap-2">
            <Button variant="outline" theme="gray" label="Edit"><template #prefix><Icon name="edit" :size="15" /></template></Button>
            <Button variant="subtle" theme="red" label="Initiate exit"><template #prefix><Icon name="logout" :size="15" /></template></Button>
          </div>
        </div>
        <div class="px-5"><Tabs :tabs="[{ id: 'overview', label: 'Overview' }, { id: 'comp', label: 'Compensation' }, { id: 'stats', label: 'Quick stats' }]" v-model:active="tab" /></div>
      </Card>

      <div class="grid items-start gap-5" style="grid-template-columns: minmax(0,1fr) 320px">
        <Card>
          <div v-if="tab === 'comp'">
            <SectionLabel :label="`Current compensation · ${formatINR(e.ctc || 0)} per annum`" />
            <AmountRow v-for="[l, v] in r.data?.comp || []" :key="l" :label="l" :value="formatINR(Math.round(v))" />
            <AmountRow label="Total CTC" :value="formatINR(e.ctc || 0)" bold :border="false" />
          </div>
          <div v-else-if="tab === 'stats'">
            <SectionLabel label="Recent payslips" />
            <AmountRow v-for="s in r.data?.slips || []" :key="s.name" :label="s.name" :value="formatINR(s.net_pay)" />
          </div>
          <div v-else class="flex flex-col gap-6">
            <div><SectionLabel label="Personal" /><div :class="grid">
              <Field label="Date of birth" :value="e.date_of_birth" /><Field label="Gender" :value="e.gender" /><Field label="Blood group" :value="e.blood_group" />
              <Field label="Personal email" :value="e.personal_email" /><Field label="Mobile" :value="e.cell_number" /><Field label="Marital status" :value="e.marital_status" />
            </div></div>
            <div><SectionLabel label="Employment" /><div :class="grid">
              <Field label="Employee ID" :value="e.employee_number" /><Field label="Department" :value="(e.department || '').split(' - ')[0]" /><Field label="Designation" :value="e.designation" />
              <Field label="Reporting manager" :value="e.manager_name" /><Field label="Grade" :value="e.grade" /><Field label="Location" :value="e.location" />
            </div></div>
            <div><SectionLabel label="Statutory" /><div :class="grid">
              <Field label="PAN" :value="e.pan_number" /><Field label="UAN" :value="e.provident_fund_account" /><Field label="IFSC" :value="e.ifsc_code" />
            </div></div>
          </div>
        </Card>
        <Card>
          <CardHeader title="Quick stats" />
          <AmountRow label="Tenure" :value="e.tenure" />
          <AmountRow label="CTC" :value="formatINR(e.ctc || 0)" />
          <AmountRow label="Grade" :value="e.grade || '—'" :border="false" />
        </Card>
      </div>
    </template>
  </div>
</template>
