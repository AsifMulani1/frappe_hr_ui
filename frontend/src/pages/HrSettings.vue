<script setup>
import { ref, computed } from "vue"
import { createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import SectionLabel from "@/components/ui/SectionLabel.vue"
import Field from "@/components/ui/Field.vue"
import DataTable from "@/components/ui/DataTable.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import Icon from "@/components/ui/Icon.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"

const r = createResource({ url: "frappe_hr_ui.api.get_settings", auto: true })
const d = computed(() => r.data || {})
const active = ref("company")
const groups = [
  { id: "company", label: "Company profile", icon: "briefcase" },
  { id: "leave", label: "Leave policies", icon: "calendar" },
  { id: "payroll", label: "Payroll settings", icon: "rupee" },
  { id: "roles", label: "Roles & permissions", icon: "shield" },
]
const leaveCols = [
  { key: "name", label: "Leave type" },
  { key: "max_leaves_allowed", label: "Annual quota", align: "right" },
  { key: "is_carry_forward", label: "Carry forward" },
]
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Settings" subtitle="Configure HR, payroll and compliance" />
    <AsyncShell :resource="r" loading-text="Loading settings…">
    <div class="grid items-start gap-5" style="grid-template-columns: 240px minmax(0,1fr)">
      <Card class="!p-2">
        <button v-for="g in groups" :key="g.id" @click="active = g.id"
          class="flex w-full items-center gap-2.5 rounded-md px-2.5 py-2.5 text-left text-[13.5px]"
          :class="active === g.id ? 'bg-blue-50 font-medium text-blue-700' : 'text-ink-gray-7 hover:bg-surface-gray-1'">
          <Icon :name="g.icon" :size="16" />{{ g.label }}
        </button>
      </Card>
      <Card>
        <div v-if="active === 'company'">
          <SectionLabel label="Company profile" />
          <div class="grid grid-cols-2 gap-x-5 gap-y-4">
            <Field label="Legal name" :value="d.company?.company_name" />
            <Field label="Abbreviation" :value="d.company?.abbr" />
            <Field label="Currency" :value="d.company?.default_currency" />
            <Field label="Country" :value="d.company?.country" />
          </div>
        </div>
        <div v-else-if="active === 'leave'">
          <SectionLabel label="Leave types & policies" />
          <DataTable :columns="leaveCols" :rows="d.leave_types || []" row-key="name">
            <template #cell-name="{ row }"><span class="font-medium">{{ row.name }}</span></template>
            <template #cell-max_leaves_allowed="{ row }"><span class="tnum">{{ row.max_leaves_allowed || '—' }}</span></template>
            <template #cell-is_carry_forward="{ row }"><StatusBadge :tone="row.is_carry_forward ? 'success' : 'neutral'" size="sm" :label="row.is_carry_forward ? 'Yes' : 'No'" /></template>
          </DataTable>
        </div>
        <div v-else>
          <SectionLabel :label="groups.find((g) => g.id === active).label" />
          <div class="flex flex-col">
            <div v-for="(t, i) in ['Auto-approve regularizations under 15 min', 'Lock payroll 5 days before pay date', 'Allow employees to download Form 16', 'Notify managers of pending approvals daily']" :key="t"
              class="flex items-center justify-between py-3.5" :class="i ? 'border-t border-outline-gray-1' : ''">
              <span class="text-[13.5px] text-ink-gray-9">{{ t }}</span>
              <div class="h-[22px] w-[38px] rounded-full p-0.5" :class="i % 2 === 0 ? 'bg-blue-500' : 'bg-surface-gray-3'">
                <div class="h-[18px] w-[18px] rounded-full bg-white shadow-sm transition-transform" :class="i % 2 === 0 ? 'translate-x-4' : ''" />
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
    </AsyncShell>
  </div>
</template>
