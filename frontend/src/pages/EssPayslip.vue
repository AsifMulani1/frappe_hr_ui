<script setup>
import { ref, computed, watch } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import AmountRow from "@/components/ui/AmountRow.vue"
import Icon from "@/components/ui/Icon.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"
import { formatINR } from "@/utils/formatters"
import { downloadPdf } from "@/utils/actions"

const list = createResource({ url: "frappe_hr_ui.api.get_payslips", auto: true })
const sel = ref(null)
const detail = createResource({ url: "frappe_hr_ui.api.get_payslip_detail" })

const slips = computed(() => list.data?.slips || [])
watch(slips, (s) => { if (s.length && !sel.value) select(s[0].name) })
function select(name) { sel.value = name; detail.fetch({ name }) }
const det = computed(() => detail.data || {})
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Payslips" subtitle="View and download your monthly salary slips">
      <template #actions>
        <Button variant="solid" theme="blue" label="Download PDF" :disabled="!sel" @click="downloadPdf('Salary Slip', sel)"><template #prefix><Icon name="download" :size="15" /></template></Button>
      </template>
    </PageHeader>

    <AsyncShell :resource="list" :has-employee="!!list.data?.employee" loading-text="Loading payslips…">
    <div v-if="!slips.length" class="py-16 text-center text-[13px] text-ink-gray-5">No payslips yet.</div>

    <div v-else class="grid items-start gap-5" style="grid-template-columns: 260px minmax(0,1fr)">
      <Card :pad="false" class="p-2">
        <div class="px-2.5 py-2 text-[12px] font-medium text-ink-gray-5">All payslips</div>
        <div class="flex flex-col gap-0.5">
          <button v-for="s in slips" :key="s.name" @click="select(s.name)"
            class="flex items-center justify-between rounded-md px-3 py-2.5 text-left transition-colors"
            :class="sel === s.name ? 'bg-blue-50' : 'hover:bg-surface-gray-1'">
            <div>
              <div class="text-[13.5px] font-medium" :class="sel === s.name ? 'text-blue-700' : 'text-ink-gray-9'">{{ s.month }}</div>
              <div class="tnum text-[11.5px] text-ink-gray-5">{{ formatINR(s.net_pay) }} net</div>
            </div>
            <Icon name="chevRight" :size="15" :class="sel === s.name ? 'text-blue-600' : 'text-ink-gray-4'" />
          </button>
        </div>
      </Card>

      <Card :pad="false">
        <div v-if="det.name">
          <div class="flex flex-wrap items-start justify-between gap-3 border-b border-outline-gray-1 px-6 py-5">
            <div class="flex items-center gap-3">
              <div class="flex h-[38px] w-[38px] items-center justify-center rounded-md bg-blue-600 text-[17px] font-medium text-white">{{ (det.company || 'C').charAt(0) }}</div>
              <div>
                <div class="text-[15px] font-medium text-ink-gray-9">{{ det.company }}</div>
                <div class="text-[12.5px] text-ink-gray-5">Payslip for {{ det.month }}</div>
              </div>
            </div>
            <StatusBadge :tone="det.status === 'Paid' ? 'success' : 'warning'" dot :label="`${det.status} · ${det.posting_date}`" />
          </div>

          <div class="grid grid-cols-4 gap-4 border-b border-outline-gray-1 bg-surface-gray-1 px-6 py-4">
            <div v-for="[l, v] in [['Employee', det.employee_name], ['Employee ID', det.emp_number], ['Designation', det.designation], ['Paid days', `${det.payment_days} / ${det.total_working_days}`]]" :key="l">
              <div class="text-[11.5px] text-ink-gray-5">{{ l }}</div>
              <div class="tnum mt-0.5 text-[13px] font-medium text-ink-gray-9">{{ v }}</div>
            </div>
          </div>

          <div class="grid px-6 pb-5 pt-2" style="grid-template-columns: 1fr 1px 1fr">
            <div class="pr-6">
              <div class="py-3.5 text-[12.5px] font-medium uppercase tracking-[.03em] text-ink-gray-5">Earnings</div>
              <AmountRow v-for="e in det.earnings || []" :key="e.label" :label="e.label" :value="formatINR(e.amount)" />
              <AmountRow label="Gross earnings" :value="formatINR(det.gross)" bold :border="false" />
            </div>
            <div class="bg-outline-gray-1" />
            <div class="pl-6">
              <div class="py-3.5 text-[12.5px] font-medium uppercase tracking-[.03em] text-ink-gray-5">Deductions</div>
              <AmountRow v-for="e in det.deductions || []" :key="e.label" :label="e.label" :value="formatINR(e.amount)" color="text-red-600" />
              <AmountRow label="Total deductions" :value="formatINR(det.total_deduction)" bold :border="false" color="text-red-600" />
            </div>
          </div>

          <div class="mx-6 mb-6 flex flex-wrap items-center justify-between gap-2 rounded-[10px] border border-blue-100 bg-blue-50 px-5 py-4">
            <div>
              <div class="text-[13px] font-medium text-blue-700">Net pay for {{ det.month }}</div>
              <div class="text-[11.5px] text-ink-gray-6">Gross {{ formatINR(det.gross) }} − deductions {{ formatINR(det.total_deduction) }}</div>
            </div>
            <div class="tnum text-[30px] font-medium tracking-tight text-blue-700">{{ formatINR(det.net) }}</div>
          </div>
        </div>
        <div v-else class="p-10 text-center text-[13px] text-ink-gray-5">Select a payslip.</div>
      </Card>
    </div>
    </AsyncShell>
  </div>
</template>
