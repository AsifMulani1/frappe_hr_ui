<script setup>
// Admin onboarding spine. A resumable, self-checking "getting started" checklist
// that lives on Home — the primary path for a DIY admin to take a fresh site to
// payroll-ready. Each item auto-detects completion from defaults_status and
// deep-links into the matching setup step; "Apply India defaults" runs inline.
import { ref, computed, watch } from "vue"
import { useRouter } from "vue-router"
import { Button, createResource, toast } from "frappe-ui"
import Icon from "@/components/ui/Icon.vue"

const router = useRouter()
const DISMISS_KEY = "fhrui:getting-started-dismissed"
const dismissed = ref(localStorage.getItem(DISMISS_KEY) === "1")

const status = createResource({ url: "frappe_hr_ui.india_defaults.defaults_status", auto: true })
const stat = createResource({ url: "frappe_hr_ui.api.get_company_statutory" })
const unassigned = createResource({ url: "frappe_hr_ui.api.get_unassigned_employees" })

const s = computed(() => status.data || {})
const st = computed(() => stat.data || {})

// Statutory + assignment counts need a company; fetch them only once one exists.
watch(() => s.value.has_company, (has) => {
  if (!has) return
  if (!stat.data && !stat.loading) stat.fetch()
  if ((s.value.employees ?? 0) > 0 && !unassigned.data && !unassigned.loading) unassigned.fetch()
}, { immediate: true })

const applyDefaults = createResource({
  url: "frappe_hr_ui.india_defaults.apply_defaults",
  onSuccess() { toast.success("India defaults applied"); status.reload() },
  onError(e) { toast.error(e?.messages?.[0] || "Couldn't apply defaults") },
})

const items = computed(() => {
  const emp = s.value.employees ?? 0
  const unassignedCount = unassigned.data?.employees?.length
  const defaultsDone = !!(s.value.has_components && s.value.has_structure && s.value.statutory_enabled)
  const statDone = !!(st.value.pf_registration_number && st.value.esic_registration_number
    && st.value.pt_registration_number && st.value.tan_number)
  return [
    { key: "company", label: "Create your company", done: !!s.value.has_company,
      desc: s.value.has_company ? `${s.value.company} · ${s.value.country || "India"} · ${s.value.currency || "INR"}` : "Everything belongs to a company — start here",
      cta: "Create", to: { name: "SetupWizard", query: { step: "company" } } },
    { key: "defaults", label: "Apply India payroll defaults", done: defaultsDone,
      desc: "Salary components, structure, holiday calendar, and the PT/ESI/LWF engine",
      cta: "Apply", inline: true },
    { key: "people", label: "Add your team", done: emp > 0,
      desc: emp > 0 ? `${emp} employee${emp > 1 ? "s" : ""} added` : "Import a CSV (or add one)",
      cta: "Import", to: { name: "SetupWizard", query: { step: "people" } } },
    { key: "pay", label: "Assign compensation", done: emp > 0 && unassignedCount === 0,
      desc: unassignedCount === 0 && emp > 0 ? "Everyone has pay assigned"
        : (unassignedCount != null ? `${unassignedCount} without pay` : "Set base pay per person"),
      cta: "Assign", to: { name: "SetupWizard", query: { step: "pay" } } },
    { key: "statutory", label: "Statutory registration numbers", done: statDone, optional: true,
      desc: "PF / ESIC / PT / TAN — print on registers & challans",
      cta: "Add", to: { name: "SetupWizard", query: { step: "defaults" } } },
    { key: "preview", label: "Preview your first payslip", done: false, soft: true,
      desc: "See PF, PT, ESI and net computed — nothing is submitted",
      cta: "Preview", to: { name: "SetupWizard", query: { step: "preview" } } },
  ]
})

// Progress is over the REQUIRED items only (optional/soft don't gate "ready").
const required = computed(() => items.value.filter((i) => !i.optional && !i.soft))
const doneCount = computed(() => required.value.filter((i) => i.done).length)
const total = computed(() => required.value.length)
const allDone = computed(() => doneCount.value === total.value)
const show = computed(() => status.data && !(allDone.value && dismissed.value))

function act(it) {
  if (it.done && !it.soft) return
  if (it.inline) { applyDefaults.submit({}); return }
  if (it.to) router.push(it.to)
}
function dismiss() { dismissed.value = true; localStorage.setItem(DISMISS_KEY, "1") }
</script>

<template>
  <div v-if="show" class="rounded-xl border border-outline-gray-1 bg-surface-white p-5">
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0">
        <div class="text-[15px] font-medium text-ink-gray-9">
          {{ allDone ? "You're payroll-ready 🎉" : "Get set up" }}
        </div>
        <p class="mt-0.5 text-[12.5px] text-ink-gray-5">
          {{ allDone
            ? "Everything's configured. Run payroll from Payroll → Run when it's month-end."
            : `${doneCount} of ${total} done — finish setting up ${s.company || "your company"}.` }}
        </p>
      </div>
      <Button class="shrink-0" size="sm" variant="ghost" theme="gray" label="Dismiss" @click="dismiss" />
    </div>

    <!-- progress -->
    <div class="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-surface-gray-2">
      <div class="h-full rounded-full bg-green-500 transition-all duration-300" :style="{ width: `${total ? (doneCount / total) * 100 : 0}%` }" />
    </div>

    <!-- items -->
    <div class="mt-3 flex flex-col">
      <div v-for="it in items" :key="it.key"
        class="group flex items-center gap-3 rounded-lg px-2 py-2.5 hover:bg-surface-gray-1">
        <div class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full"
          :class="it.done ? 'bg-green-500 text-white' : 'border border-outline-gray-3'">
          <Icon v-if="it.done" name="check" :size="12" />
        </div>
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-2">
            <span class="text-[13px] font-medium" :class="it.done && !it.soft ? 'text-ink-gray-5' : 'text-ink-gray-9'">{{ it.label }}</span>
            <span v-if="it.optional && !it.done" class="rounded bg-surface-gray-2 px-1.5 py-0.5 text-[10px] text-ink-gray-5">to file</span>
          </div>
          <div class="truncate text-[11.5px] text-ink-gray-5">{{ it.desc }}</div>
        </div>
        <Button v-if="!it.done || it.soft" size="sm" variant="subtle" theme="gray"
          :label="it.cta" :loading="it.inline && applyDefaults.loading" @click="act(it)" />
        <Icon v-else name="check" :size="15" class="shrink-0 text-green-500" />
      </div>
    </div>
  </div>
</template>
