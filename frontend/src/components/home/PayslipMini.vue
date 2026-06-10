<script setup>
import { useRouter } from "vue-router"
import { Button, Badge } from "frappe-ui"
import Card from "@/components/ui/Card.vue"
import Icon from "@/components/ui/Icon.vue"
import { formatINR } from "@/utils/formatters"
import { downloadPdf } from "@/utils/actions"

const props = defineProps({ payslip: { type: Object, default: null } })
const router = useRouter()
</script>

<template>
  <Card>
    <template v-if="payslip">
      <div class="mb-3.5 flex items-center justify-between">
        <div class="text-[13px] font-medium text-ink-gray-5">Latest payslip · {{ payslip.month }}</div>
        <Badge variant="subtle" theme="green" size="sm" :label="payslip.status" />
      </div>
      <div class="tnum text-[28px] font-medium tracking-tight text-ink-gray-9">{{ formatINR(payslip.net) }}</div>
      <div class="mt-0.5 text-[12px] text-ink-gray-5">Net pay · credited {{ payslip.credited }}</div>
      <div class="my-3.5 flex gap-[18px] border-t border-outline-gray-1 pt-3.5">
        <div>
          <div class="text-[11.5px] text-ink-gray-5">Gross</div>
          <div class="tnum text-[14px] font-medium text-ink-gray-9">{{ formatINR(payslip.gross) }}</div>
        </div>
        <div>
          <div class="text-[11.5px] text-ink-gray-5">Deductions</div>
          <div class="tnum text-[14px] font-medium text-ink-gray-9">{{ formatINR(payslip.deductions) }}</div>
        </div>
      </div>
      <div class="flex gap-2">
        <Button class="flex-1" variant="outline" theme="gray" size="sm" label="View" @click="router.push('/payslips')">
          <template #prefix><Icon name="file" :size="15" /></template>
        </Button>
        <Button class="flex-1" variant="outline" theme="gray" size="sm" label="Download" @click="downloadPdf('Salary Slip', props.payslip.name)">
          <template #prefix><Icon name="download" :size="15" /></template>
        </Button>
      </div>
    </template>
    <div v-else class="py-6 text-center text-[13px] text-ink-gray-5">No payslips yet.</div>
  </Card>
</template>
