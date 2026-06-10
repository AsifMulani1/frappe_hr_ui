<script setup>
// Company statutory identity — the registration numbers a company files returns
// under (PF/ESI/PT/TAN). These stamp onto the statutory registers and challans.
import { reactive, watch } from "vue"
import { Button, FormControl, createResource, toast } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"

const r = createResource({ url: "frappe_hr_ui.api.get_company_statutory", auto: true })
const form = reactive({ pf_registration_number: "", esic_registration_number: "", pt_registration_number: "", tan_number: "" })
watch(() => r.data, (d) => { if (d) for (const k of Object.keys(form)) form[k] = d[k] || "" }, { immediate: true })

const save = createResource({
  url: "frappe_hr_ui.api.save_company_statutory",
  onSuccess() { toast.success("Statutory profile saved"); r.reload() },
  onError(e) { toast.error(e?.messages?.[0] || "Couldn't save") },
})
function doSave() { save.submit({ values: JSON.stringify({ ...form }) }) }
</script>

<template>
  <div class="mx-auto max-w-[760px] px-6 py-[22px]">
    <PageHeader title="Statutory profile"
      :subtitle="`Registration numbers for ${r.data?.company_name || r.data?.company || 'your company'} — they appear on registers, challans and returns`" />
    <AsyncShell :resource="r" loading-text="Loading statutory profile…">
      <Card>
        <div class="grid grid-cols-2 gap-4">
          <FormControl type="text" label="PF Establishment Code" placeholder="e.g. MHBAN1234567000" v-model="form.pf_registration_number" />
          <FormControl type="text" label="ESIC Employer Code" placeholder="17-digit ESIC code" v-model="form.esic_registration_number" />
          <FormControl type="text" label="Professional Tax Reg. No." placeholder="State PT registration" v-model="form.pt_registration_number" />
          <FormControl type="text" label="TAN (for TDS / 24Q)" placeholder="e.g. MUMA12345B" v-model="form.tan_number" />
        </div>
        <p class="mt-4 text-[12px] leading-relaxed text-ink-gray-5">
          These identify your company to <span class="font-medium text-ink-gray-7">EPFO, ESIC, the state government and the Income Tax department</span>.
          They print on the statutory registers and challans you file each cycle.
        </p>
        <div class="mt-5 flex justify-end">
          <Button variant="solid" theme="blue" label="Save profile" :loading="save.loading" @click="doSave" />
        </div>
      </Card>
    </AsyncShell>
  </div>
</template>
