<script setup>
import { ref, computed } from "vue"
import { Badge, Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import SectionLabel from "@/components/ui/SectionLabel.vue"
import Tabs from "@/components/ui/Tabs.vue"
import Field from "@/components/ui/Field.vue"
import Icon from "@/components/ui/Icon.vue"

const profile = createResource({
  url: "frappe_hr_ui.api.get_employee_profile",
  auto: true,
  cache: "frappe_hr_ui:employee_profile",
})

const e = computed(() => profile.data?.employee || {})
const tab = ref("personal")

function maskAcct(n) {
  if (!n) return "—"
  const s = String(n)
  return "XXXXXX " + s.slice(-4)
}
function maskAadhaar() {
  return "—"
}

const metaItems = computed(() => [
  ["briefcase", e.value.employee_number],
  ["mapPin", e.value.location],
  ["mail", e.value.company_email],
  ["phone", e.value.cell_number],
])

const tabs = computed(() => [
  { id: "personal", label: "Personal" },
  { id: "job", label: "Job" },
  { id: "bank", label: "Bank & tax" },
  { id: "documents", label: "Documents", count: profile.data?.documents?.length || 0 },
])
const grid = "grid grid-cols-3 gap-x-7 gap-y-[18px]"
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="My profile" subtitle="View and manage your personal and job information" />

    <div v-if="profile.loading && !profile.data" class="py-20 text-center text-[13px] text-ink-gray-5">
      Loading profile…
    </div>

    <div v-else-if="!e.name" class="py-20 text-center text-[13px] text-ink-gray-5">
      No employee record linked to this user.
    </div>

    <div v-else class="grid items-start gap-5" style="grid-template-columns: minmax(0, 1fr) 320px">
      <!-- left column -->
      <div class="flex flex-col gap-5">
        <!-- header card -->
        <Card :pad="false" class="overflow-hidden">
          <div class="h-[76px] border-b border-outline-gray-1 bg-blue-50" />
          <div class="-mt-[34px] flex flex-wrap items-end gap-[18px] px-6 pb-5">
            <div class="rounded-full ring-4 ring-surface-white">
              <InitialsAvatar :name="e.employee_name" :image="e.image" :size="84" />
            </div>
            <div class="min-w-[200px] flex-1 pb-0.5">
              <div class="flex items-center gap-2.5">
                <h2 class="text-[20px] font-medium text-ink-gray-9">{{ e.employee_name }}</h2>
                <Badge variant="subtle" theme="green" size="sm" :label="e.status || 'Active'" />
                <Badge v-if="e.grade" variant="subtle" theme="gray" size="sm" :label="e.grade" />
              </div>
              <div class="mt-[3px] text-[13.5px] text-ink-gray-7">
                {{ e.designation }} · {{ e.department }}
              </div>
              <div class="mt-2 flex flex-wrap gap-4">
                <span
                  v-for="([ic, tx], i) in metaItems"
                  :key="i"
                  class="inline-flex items-center gap-1.5 text-[12.5px] text-ink-gray-5"
                >
                  <Icon :name="ic" :size="14" />{{ tx || "—" }}
                </span>
              </div>
            </div>
            <div class="flex gap-2 pb-0.5">
              <Button variant="outline" theme="gray" label="Edit details">
                <template #prefix><Icon name="edit" :size="15" /></template>
              </Button>
              <Button variant="outline" theme="gray" label="Documents">
                <template #prefix><Icon name="download" :size="15" /></template>
              </Button>
            </div>
          </div>
        </Card>

        <!-- tabbed details -->
        <Card :pad="false">
          <div class="px-5"><Tabs :tabs="tabs" v-model:active="tab" /></div>
          <div class="p-[22px]">
            <!-- personal -->
            <div v-if="tab === 'personal'" class="flex flex-col gap-6">
              <div>
                <SectionLabel label="Personal information" />
                <div :class="grid">
                  <Field label="Full name" :value="e.employee_name" />
                  <Field label="Date of birth" :value="e.date_of_birth" />
                  <Field label="Gender" :value="e.gender" />
                  <Field label="Blood group" :value="e.blood_group" />
                  <Field label="Marital status" :value="e.marital_status" />
                  <Field label="Employee ID" :value="e.employee_number" />
                </div>
              </div>
              <div>
                <SectionLabel label="Contact" />
                <div :class="grid">
                  <Field label="Personal email" :value="e.personal_email" />
                  <Field label="Work email" :value="e.company_email" />
                  <Field label="Mobile" :value="e.cell_number" />
                  <Field label="Emergency contact" :value="e.person_to_be_contacted ? `${e.person_to_be_contacted} · ${e.emergency_phone_number || ''}` : ''" />
                  <Field label="Current address" :value="e.current_address" full />
                </div>
              </div>
            </div>

            <!-- job -->
            <div v-else-if="tab === 'job'" class="flex flex-col gap-6">
              <div>
                <SectionLabel label="Employment" />
                <div :class="grid">
                  <Field label="Employee ID" :value="e.employee_number" />
                  <Field label="Designation" :value="e.designation" />
                  <Field label="Department" :value="e.department" />
                  <Field label="Reporting manager" :value="e.manager_name" />
                  <Field label="Grade" :value="e.grade" />
                  <Field label="Employment type" :value="e.employment_type" />
                  <Field label="Date of joining" :value="e.date_of_joining" />
                  <Field label="Work location" :value="e.location" />
                  <Field label="Shift" :value="e.shift_label" />
                </div>
              </div>
              <div>
                <SectionLabel label="Statutory IDs" />
                <div :class="grid">
                  <Field label="PAN" :value="e.pan_number" />
                  <Field label="Aadhaar" :value="maskAadhaar()" />
                  <Field label="UAN (PF)" :value="e.provident_fund_account" />
                </div>
              </div>
            </div>

            <!-- bank -->
            <div v-else-if="tab === 'bank'">
              <SectionLabel label="Bank & salary account" />
              <div :class="grid">
                <Field label="Bank name" :value="e.bank_name" />
                <Field label="Account number" :value="maskAcct(e.bank_ac_no)" />
                <Field label="IFSC code" :value="e.ifsc_code" />
                <Field label="Payment mode" :value="e.salary_mode" />
              </div>
            </div>

            <!-- documents -->
            <div v-else>
              <SectionLabel label="Documents">
                <template #action>
                  <Button variant="outline" theme="gray" size="sm" label="Upload">
                    <template #prefix><Icon name="plus" :size="15" /></template>
                  </Button>
                </template>
              </SectionLabel>
              <div v-if="profile.data?.documents?.length" class="grid grid-cols-2 gap-2.5">
                <div
                  v-for="doc in profile.data.documents"
                  :key="doc.name"
                  class="flex items-center gap-3 rounded-md border border-outline-gray-1 p-3"
                >
                  <div class="flex h-[34px] w-[34px] items-center justify-center rounded-md bg-surface-gray-2 text-ink-gray-7">
                    <Icon name="file" :size="17" />
                  </div>
                  <div class="min-w-0 flex-1">
                    <div class="truncate text-[13px] font-medium text-ink-gray-9">{{ doc.name }}</div>
                    <div class="text-[11.5px] text-ink-gray-5">{{ doc.size }}</div>
                  </div>
                  <a :href="doc.url" target="_blank" class="text-ink-gray-5 hover:text-ink-gray-8">
                    <Icon name="download" :size="16" />
                  </a>
                </div>
              </div>
              <div v-else class="rounded-md border border-dashed border-outline-gray-2 py-10 text-center">
                <div class="text-[13px] font-medium text-ink-gray-7">No documents uploaded</div>
                <div class="mt-1 text-[12px] text-ink-gray-5">Upload your offer letter, ID proofs and certificates.</div>
              </div>
            </div>
          </div>
        </Card>
      </div>

      <!-- right rail -->
      <div class="flex flex-col gap-5">
        <Card>
          <CardHeader title="Reporting line" />
          <div class="flex flex-col gap-3">
            <div v-for="m in profile.data?.reporting_line || []" :key="m.employee_number" class="flex items-center gap-2.5">
              <InitialsAvatar :name="m.employee_name" :size="32" />
              <div class="flex-1">
                <div class="text-[13px] font-medium text-ink-gray-9">{{ m.employee_name }}</div>
                <div class="text-[11.5px] text-ink-gray-5">{{ m.designation }}</div>
              </div>
            </div>
            <div class="mt-0.5 border-t border-outline-gray-1 pt-3">
              <div class="mb-2 text-[11.5px] text-ink-gray-5">Peers · {{ e.department }}</div>
              <div class="flex">
                <div v-for="(p, i) in (profile.data?.peers || []).slice(0, 5)" :key="p.employee_number" :class="i ? '-ml-2' : ''">
                  <InitialsAvatar :name="p.employee_name" :size="26" ring />
                </div>
                <div
                  v-if="(profile.data?.peers || []).length > 5"
                  class="-ml-2 flex h-[26px] w-[26px] items-center justify-center rounded-full border-2 border-surface-white bg-surface-gray-2 text-[11px] font-medium text-ink-gray-7"
                >
                  +{{ profile.data.peers.length - 5 }}
                </div>
              </div>
            </div>
          </div>
        </Card>

        <Card>
          <CardHeader title="Tenure & assets" />
          <div class="flex flex-col gap-3.5">
            <div>
              <div class="text-[12px] text-ink-gray-5">With {{ e.company?.split(' ')[0] || 'the company' }} for</div>
              <div class="text-[17px] font-medium text-ink-gray-9">{{ e.tenure }}</div>
            </div>
            <div class="border-t border-outline-gray-1 pt-3">
              <div class="mb-2 text-[12px] text-ink-gray-5">Assigned assets</div>
              <div v-if="profile.data?.assets?.length" class="flex flex-col gap-1.5">
                <div v-for="a in profile.data.assets" :key="a.name" class="flex justify-between text-[13px]">
                  <span class="text-ink-gray-9">{{ a.asset_name }}</span>
                  <span class="tnum text-ink-gray-5">{{ a.name }}</span>
                </div>
              </div>
              <div v-else class="text-[12.5px] text-ink-gray-5">No assets assigned.</div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  </div>
</template>
