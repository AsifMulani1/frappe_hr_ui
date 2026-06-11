<script setup>
// Guided, linear self-implementation — defaults → statutory → people → pay → run.
// One path, zero Desk: a non-technical admin goes from empty to first payroll.
import { ref, reactive, computed, watch } from "vue"
import { Button, createResource, toast, FormControl, Select, TextInput } from "frappe-ui"
import { useRouter, useRoute } from "vue-router"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import DateField from "@/components/ui/DateField.vue"
import Icon from "@/components/ui/Icon.vue"

const router = useRouter()
const route = useRoute()
const STEPS = ["Company", "Defaults", "People", "Pay", "Preview", "Done"]
const STEP_QUERY = { company: 1, defaults: 2, people: 3, employees: 3, pay: 4, preview: 5, run: 5 }
const step = ref(STEP_QUERY[route.query.step] || 1)

const STATES = ["Andhra Pradesh", "Assam", "Bihar", "Chandigarh", "Chhattisgarh", "Delhi", "Goa", "Gujarat",
  "Haryana", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Meghalaya", "Odisha",
  "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "West Bengal"]
const stateOpts = STATES.map((x) => ({ label: x, value: x }))

const status = createResource({ url: "frappe_hr_ui.india_defaults.defaults_status", auto: true })
const s = computed(() => status.data || {})

// ---- 1. Company (create if the site has none) ----
const companyForm = reactive({ company_name: "", country: "India", currency: "INR" })
const createCompany = createResource({
  url: "frappe_hr_ui.india_defaults.create_company",
  onSuccess() { toast.success("Company created"); status.reload(); stat.reload(); step.value = 2 },
  onError(e) { toast.error(e?.messages?.[0] || "Couldn't create company") },
})
function makeCompany() {
  if (!companyForm.company_name.trim()) { toast.error("Enter a company name"); return }
  createCompany.submit({ ...companyForm })
}

// ---- 2. Defaults + statutory numbers ----
const applyDefaults = createResource({ url: "frappe_hr_ui.india_defaults.apply_defaults" })
function runDefaults() {
  applyDefaults.submit({}, {
    onSuccess: () => { toast.success("India defaults applied"); status.reload(); stat.reload() },
    onError: (e) => toast.error(e?.messages?.[0] || "Couldn't apply defaults"),
  })
}
const stat = createResource({ url: "frappe_hr_ui.api.get_company_statutory", auto: true })
const statForm = reactive({ pf_registration_number: "", esic_registration_number: "", pt_registration_number: "", tan_number: "" })
watch(() => stat.data, (d) => { if (d) for (const k of Object.keys(statForm)) statForm[k] = d[k] || "" }, { immediate: true })
const saveStat = createResource({
  url: "frappe_hr_ui.api.save_company_statutory",
  onSuccess() { toast.success("Statutory numbers saved") },
  onError(e) { toast.error(e?.messages?.[0] || "Couldn't save") },
})
function doSaveStat() { saveStat.submit({ values: JSON.stringify({ ...statForm }) }) }

// ---- 3. People (CSV import) ----
const tpl = createResource({ url: "frappe_hr_ui.employee_import.import_template", auto: true })
const importRes = createResource({ url: "frappe_hr_ui.employee_import.import_employees" })
const parsed = reactive({ rows: [], headers: [] })
const fileName = ref("")
const cols = computed(() => tpl.data?.columns || [])
function splitLine(line) {
  const out = []; let cur = "", q = false
  for (const ch of line) { if (ch === '"') q = !q; else if (ch === "," && !q) { out.push(cur); cur = "" } else cur += ch }
  out.push(cur); return out
}
function onFile(ev) {
  const f = ev.target.files?.[0]; if (!f) return
  fileName.value = f.name
  const reader = new FileReader()
  reader.onload = () => {
    const lines = String(reader.result).trim().split(/\r?\n/).filter((l) => l.trim())
    if (!lines.length) { toast.error("Empty file"); return }
    const headers = splitLine(lines[0]).map((h) => h.trim())
    parsed.headers = headers
    parsed.rows = lines.slice(1).map((l) => { const cells = splitLine(l); const o = {}; headers.forEach((h, i) => (o[h] = (cells[i] || "").trim())); return o })
  }
  reader.readAsText(f)
}
function runImport() {
  if (!parsed.rows.length) { toast.error("Upload a CSV first"); return }
  importRes.submit({ rows: JSON.stringify(parsed.rows) }, {
    onSuccess: (r) => { toast.success(`${r.created} of ${r.total} imported`); status.reload() },
    onError: (e) => toast.error(e?.messages?.[0] || "Import failed"),
  })
}
function downloadTemplate() {
  const blob = new Blob([(tpl.data?.header || "") + "\n"], { type: "text/csv" })
  const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "employees-template.csv"; a.click(); URL.revokeObjectURL(a.href)
}

// ---- 4. Pay (bulk salary-structure assignment) ----
const unassigned = createResource({ url: "frappe_hr_ui.api.get_unassigned_employees" })
const bulkStructure = ref("")
const defaultState = ref("Maharashtra")
const bulkRows = ref([])
const structOpts = ref([])
async function loadAssign() {
  const res = await unassigned.fetch()
  structOpts.value = (res?.structures || []).map((x) => ({ label: x, value: x }))
  bulkStructure.value = res?.default_structure || ""
  bulkRows.value = (res?.employees || []).map((e) => ({ ...e, base: "", employment_state: defaultState.value }))
}
watch(defaultState, (st) => bulkRows.value.forEach((r) => { r.employment_state = st }))
const bulkCount = computed(() => bulkRows.value.filter((r) => r.base).length)
const assignRes = createResource({
  url: "frappe_hr_ui.api.bulk_assign_salary",
  onSuccess(res) { res.errors?.length ? toast.warning(`${res.assigned} assigned, ${res.errors.length} failed`) : toast.success(`${res.assigned} assigned`); loadAssign() },
  onError(e) { toast.error(e?.messages?.[0] || "Couldn't assign") },
})
function doAssign() {
  if (!bulkStructure.value) { toast.error("Pick a salary structure"); return }
  const rows = bulkRows.value.filter((r) => r.base)
  if (!rows.length) { toast.error("Enter a base salary for at least one employee"); return }
  assignRes.submit({ salary_structure: bulkStructure.value, rows: JSON.stringify(rows.map((r) => ({ employee: r.employee, base: r.base, employment_state: r.employment_state }))) })
}

// ---- 5. Run (payroll) ----
const period = ref("")
function monthBounds(d) {
  const dt = new Date(d), pad = (n) => String(n).padStart(2, "0")
  const first = `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-01`
  const last = new Date(dt.getFullYear(), dt.getMonth() + 1, 0)
  return { first, last: `${last.getFullYear()}-${pad(last.getMonth() + 1)}-${pad(last.getDate())}` }
}
const preview = createResource({ url: "frappe_hr_ui.api.preview_payroll" })
const sample = createResource({ url: "frappe_hr_ui.api.preview_payslip" })
watch(period, (p) => {
  if (!p) return
  const start = monthBounds(p).first
  preview.fetch({ start_date: start })
  sample.fetch({ start_date: start })
})
function pickSample(e) { if (period.value) sample.fetch({ start_date: monthBounds(period.value).first, employee: e }) }
function inr(n) { return "₹" + Number(n || 0).toLocaleString("en-IN") }
const runRes = createResource({
  url: "frappe_hr_ui.api.run_payroll",
  onSuccess(res) { res.errors?.length ? toast.warning(`${res.created} created, ${res.errors.length} failed`) : toast.success(`${res.created} slip(s) created`); status.reload() },
  onError(e) { toast.error(e?.messages?.[0] || "Couldn't run payroll") },
})
function doRun() {
  if (!period.value) { toast.error("Pick a month"); return }
  const { first, last } = monthBounds(period.value)
  runRes.submit({ start_date: first, end_date: last })
}

// lazy-load step data
watch(step, (n) => {
  if (n === 4 && !unassigned.data) loadAssign()
  if (n === 5 && !period.value) { const d = new Date(); period.value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-01` }
})
</script>

<template>
  <div class="mx-auto max-w-[860px] px-6 py-[22px]">
    <PageHeader title="Set up your company" subtitle="Zero to payroll-ready — defaults, people, pay, preview. No Desk needed." />

    <!-- stepper -->
    <div class="mb-5 flex flex-wrap items-center gap-2">
      <template v-for="(label, i) in STEPS" :key="i">
        <button class="flex items-center gap-2" @click="step = i + 1">
          <div class="flex h-6 w-6 items-center justify-center rounded-full text-[12px] font-medium"
            :class="step > i + 1 ? 'bg-blue-600 text-white' : step === i + 1 ? 'bg-blue-100 text-blue-700' : 'bg-surface-gray-2 text-ink-gray-5'">
            <Icon v-if="step > i + 1" name="check" :size="13" /><span v-else>{{ i + 1 }}</span>
          </div>
          <span class="text-[12.5px]" :class="step === i + 1 ? 'font-medium text-ink-gray-9' : 'text-ink-gray-5'">{{ label }}</span>
        </button>
        <div v-if="i < STEPS.length - 1" class="h-px w-5 bg-outline-gray-2" />
      </template>
    </div>

    <!-- 1: company -->
    <Card v-if="step === 1">
      <!-- no company on the site yet → create one (no Desk needed) -->
      <template v-if="status.data && !s.has_company">
        <div class="text-[15px] font-medium text-ink-gray-9">Create your company</div>
        <p class="mt-1 text-[13px] text-ink-gray-6">Everything — employees, payroll, compliance — belongs to a company. Let's create yours to get started.</p>
        <div class="mt-4 grid grid-cols-2 gap-3">
          <FormControl class="col-span-2" type="text" label="Company name" placeholder="e.g. Acme Technologies Pvt. Ltd." v-model="companyForm.company_name" />
          <FormControl type="text" label="Country" v-model="companyForm.country" />
          <FormControl type="text" label="Currency" v-model="companyForm.currency" />
        </div>
        <p class="mt-3 text-[11.5px] text-ink-gray-4">This builds your chart of accounts — it can take a few seconds.</p>
        <div class="mt-5 flex justify-end">
          <Button variant="solid" theme="blue" label="Create company & continue" :loading="createCompany.loading" @click="makeCompany" />
        </div>
      </template>
      <!-- company exists → show it (identity card) -->
      <template v-else>
        <div class="text-[15px] font-medium text-ink-gray-9">Your company</div>
        <p class="mt-1 text-[13px] text-ink-gray-6">Everything — people, payroll, compliance — belongs to this company. Confirm it and continue; the next five steps take you to your first payroll.</p>
        <div class="mt-4 flex items-center gap-3 rounded-lg border border-outline-gray-1 p-4">
          <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-surface-gray-2 text-[15px] font-semibold text-ink-gray-7">{{ s.abbr || (s.company || "?").slice(0, 2).toUpperCase() }}</div>
          <div class="min-w-0 flex-1">
            <div class="truncate text-[14px] font-medium text-ink-gray-9">{{ s.company || "—" }}</div>
            <div class="mt-0.5 text-[12.5px] text-ink-gray-5">{{ s.country || "India" }} · {{ s.currency || "INR" }}</div>
          </div>
          <div class="shrink-0 text-right"><div class="tnum text-[20px] font-medium text-ink-gray-9">{{ s.employees ?? 0 }}</div><div class="text-[11px] text-ink-gray-5">employees</div></div>
        </div>
        <div class="mt-5 flex justify-end"><Button variant="solid" theme="blue" label="Get started" @click="step = 2" /></div>
      </template>
    </Card>

    <!-- 2: defaults + statutory -->
    <Card v-else-if="step === 2">
      <div class="text-[15px] font-medium text-ink-gray-9">India payroll defaults</div>
      <p class="mt-1 text-[13px] text-ink-gray-6">Standard salary components, leave types, a salary structure, a holiday list — and turns on the statutory engine (PT/ESI/LWF). Safe to re-run.</p>
      <div class="mt-4 grid grid-cols-2 gap-2">
        <div class="flex items-center justify-between rounded-md border border-outline-gray-1 px-3 py-2 text-[13px]"><span>Salary components</span><StatusBadge :tone="s.components ? 'success' : 'neutral'" size="sm" :label="`${s.components || 0}`" /></div>
        <div class="flex items-center justify-between rounded-md border border-outline-gray-1 px-3 py-2 text-[13px]"><span>Leave types</span><StatusBadge :tone="s.leave_types ? 'success' : 'neutral'" size="sm" :label="`${s.leave_types || 0}`" /></div>
        <div class="flex items-center justify-between rounded-md border border-outline-gray-1 px-3 py-2 text-[13px]"><span>Salary structure</span><StatusBadge :tone="s.has_structure ? 'success' : 'neutral'" size="sm" :label="s.has_structure ? 'Ready' : 'None'" /></div>
        <div class="flex items-center justify-between rounded-md border border-outline-gray-1 px-3 py-2 text-[13px]"><span>Statutory engine</span><StatusBadge :tone="s.statutory_enabled ? 'success' : 'neutral'" size="sm" :label="s.statutory_enabled ? 'On' : 'Off'" /></div>
      </div>
      <div class="mt-3"><Button variant="subtle" theme="gray" label="Apply India defaults" :loading="applyDefaults.loading" @click="runDefaults" /></div>

      <div class="mt-6 border-t border-outline-gray-1 pt-5">
        <div class="text-[13.5px] font-medium text-ink-gray-9">Statutory registration numbers</div>
        <p class="mt-0.5 text-[12px] text-ink-gray-5">Optional now, required to file — they print on registers and challans.</p>
        <div class="mt-3 grid grid-cols-2 gap-3">
          <FormControl type="text" label="PF Establishment Code" placeholder="MHBAN1234567000" v-model="statForm.pf_registration_number" />
          <FormControl type="text" label="ESIC Employer Code" placeholder="17-digit" v-model="statForm.esic_registration_number" />
          <FormControl type="text" label="Professional Tax Reg." placeholder="State PT no." v-model="statForm.pt_registration_number" />
          <FormControl type="text" label="TAN (TDS)" placeholder="MUMA12345B" v-model="statForm.tan_number" />
        </div>
        <div class="mt-2"><Button variant="ghost" size="sm" label="Save numbers" :loading="saveStat.loading" @click="doSaveStat" /></div>
      </div>

      <div class="mt-5 flex justify-between">
        <Button variant="ghost" label="Back" @click="step = 1" />
        <Button variant="solid" theme="blue" label="Next: People" @click="step = 3" />
      </div>
    </Card>

    <!-- 3: people (import) -->
    <Card v-else-if="step === 3">
      <div class="flex items-center justify-between">
        <div class="text-[15px] font-medium text-ink-gray-9">Import employees</div>
        <Button variant="ghost" size="sm" label="Download CSV template" @click="downloadTemplate" />
      </div>
      <p class="mt-1 text-[13px] text-ink-gray-6">Columns: {{ cols.map((c) => c.label + (c.reqd ? '*' : '')).join(", ") }}. Departments & designations are created automatically.</p>
      <label class="mt-3 flex cursor-pointer items-center justify-center gap-2 rounded-md border border-dashed border-outline-gray-2 py-6 text-[13px] text-ink-gray-6 hover:bg-surface-gray-1">
        <Icon name="download" :size="16" /> {{ fileName || "Choose a CSV file…" }}
        <input type="file" accept=".csv,text/csv" class="hidden" @change="onFile" />
      </label>
      <div v-if="parsed.rows.length" class="mt-3">
        <div class="mb-1 text-[12px] text-ink-gray-5">{{ parsed.rows.length }} rows · preview</div>
        <div class="max-h-[200px] overflow-auto rounded-md border border-outline-gray-1">
          <table class="w-full text-[12px]">
            <thead><tr class="border-b border-outline-gray-1 text-left text-ink-gray-5"><th v-for="c in cols" :key="c.key" class="px-2 py-1.5 font-medium">{{ c.label }}</th></tr></thead>
            <tbody><tr v-for="(row, i) in parsed.rows.slice(0, 8)" :key="i" class="border-b border-outline-gray-1 last:border-0"><td v-for="c in cols" :key="c.key" class="px-2 py-1.5 text-ink-gray-8">{{ row[c.key] }}</td></tr></tbody>
          </table>
        </div>
      </div>
      <div v-if="importRes.data" class="mt-3 rounded-md bg-surface-gray-1 p-3 text-[12.5px]">
        <div class="font-medium text-ink-gray-9">{{ importRes.data.created }} of {{ importRes.data.total }} imported</div>
        <div v-for="e in importRes.data.errors" :key="e.row" class="mt-0.5 text-red-600">Row {{ e.row }} ({{ e.value }}): {{ e.error }}</div>
      </div>
      <div class="mt-5 flex justify-between">
        <Button variant="ghost" label="Back" @click="step = 2" />
        <div class="flex gap-2">
          <Button variant="subtle" theme="gray" label="Import" :disabled="!parsed.rows.length" :loading="importRes.loading" @click="runImport" />
          <Button variant="solid" theme="blue" label="Next: Pay" @click="step = 4" />
        </div>
      </div>
    </Card>

    <!-- 4: pay (bulk assign) -->
    <Card v-else-if="step === 4">
      <div class="text-[15px] font-medium text-ink-gray-9">Assign compensation</div>
      <p class="mt-1 text-[13px] text-ink-gray-6">Set a salary structure, base and state for employees who don't have one. State drives Professional Tax & LWF.</p>
      <div class="mt-3 grid grid-cols-2 gap-3">
        <div><label class="mb-1.5 block text-xs text-ink-gray-5">Salary structure</label><Select v-model="bulkStructure" :options="structOpts" placeholder="Pick structure" /></div>
        <div><label class="mb-1.5 block text-xs text-ink-gray-5">Default state (applies to all)</label><Select v-model="defaultState" :options="stateOpts" /></div>
      </div>
      <div v-if="!bulkRows.length" class="mt-3 rounded-md border border-outline-gray-1 py-7 text-center text-[13px] text-ink-gray-5">Everyone has a salary structure assigned. 🎉</div>
      <div v-else class="mt-3 overflow-hidden rounded-md border border-outline-gray-1">
        <div class="grid grid-cols-[1fr_120px_150px] gap-2 border-b border-outline-gray-1 bg-surface-gray-1 px-3 py-2 text-[11.5px] font-medium text-ink-gray-5"><span>Employee</span><span>Base (₹/mo)</span><span>State</span></div>
        <div class="max-h-[40vh] overflow-y-auto">
          <div v-for="row in bulkRows" :key="row.employee" class="grid grid-cols-[1fr_120px_150px] items-center gap-2 border-b border-outline-gray-1 px-3 py-2 last:border-b-0">
            <div class="min-w-0"><div class="truncate text-[13px] font-medium text-ink-gray-9">{{ row.employee_name }}</div><div class="truncate text-[11px] text-ink-gray-5">{{ row.designation }}</div></div>
            <TextInput type="number" size="sm" v-model="row.base" placeholder="0" />
            <Select size="sm" v-model="row.employment_state" :options="stateOpts" />
          </div>
        </div>
      </div>
      <div class="mt-5 flex justify-between">
        <Button variant="ghost" label="Back" @click="step = 3" />
        <div class="flex gap-2">
          <Button v-if="bulkCount" variant="subtle" theme="gray" :label="`Assign ${bulkCount}`" :loading="assignRes.loading" @click="doAssign" />
          <Button variant="solid" theme="blue" label="Next: Run" @click="step = 5" />
        </div>
      </div>
    </Card>

    <!-- 5: preview (non-destructive) -->
    <Card v-else-if="step === 5">
      <div class="text-[15px] font-medium text-ink-gray-9">Preview your first payslip</div>
      <p class="mt-1 text-[13px] text-ink-gray-6">See a real payslip — PT, ESI, LWF, PF and TDS computed exactly as a live run would. <b>Nothing is created or saved here</b>; the actual run lives in Payroll, where you do it each month.</p>
      <div class="mt-3 max-w-xs"><DateField label="Payroll month" v-model="period" placeholder="Pick any date in the month" /></div>
      <div v-if="preview.data" class="mt-3 text-[12.5px] text-ink-gray-5">
        <span class="font-medium text-ink-gray-8">{{ preview.data.period }}</span> ·
        <span class="tnum font-medium text-ink-gray-8">{{ preview.data.pending }}</span> ready to process
        <span v-if="preview.data.eligible - preview.data.pending"> · {{ preview.data.eligible - preview.data.pending }} already run</span>
      </div>

      <div v-if="sample.loading" class="mt-3 text-[12.5px] text-ink-gray-5">Computing a sample payslip…</div>
      <!-- real computed payslip (non-destructive) -->
      <div v-else-if="sample.data?.ok" class="mt-3 overflow-hidden rounded-lg border border-outline-gray-1">
        <div class="flex items-center justify-between gap-3 bg-surface-gray-1 px-4 py-3">
          <div class="min-w-0">
            <div class="truncate text-[13.5px] font-medium text-ink-gray-9">{{ sample.data.employee_name }}</div>
            <div class="truncate text-[11.5px] text-ink-gray-5">{{ sample.data.designation || "—" }} · {{ sample.data.state || "—" }} · {{ sample.data.period }}</div>
          </div>
          <Select v-if="sample.data.candidates?.length > 1" size="sm" :model-value="sample.data.employee"
            :options="sample.data.candidates.map((c) => ({ label: c.employee_name, value: c.employee }))"
            @update:model-value="pickSample" />
        </div>
        <div class="grid grid-cols-2 divide-x divide-outline-gray-1">
          <div class="p-4">
            <div class="mb-1.5 text-[10.5px] font-medium uppercase tracking-wide text-ink-gray-5">Earnings</div>
            <div v-for="e in sample.data.earnings" :key="e.component" class="flex justify-between py-0.5 text-[12.5px]"><span class="text-ink-gray-7">{{ e.component }}</span><span class="tnum text-ink-gray-9">{{ inr(e.amount) }}</span></div>
            <div class="mt-2 flex justify-between border-t border-outline-gray-1 pt-2 text-[12.5px] font-medium text-ink-gray-9"><span>Gross</span><span class="tnum">{{ inr(sample.data.gross_pay) }}</span></div>
          </div>
          <div class="p-4">
            <div class="mb-1.5 text-[10.5px] font-medium uppercase tracking-wide text-ink-gray-5">Deductions</div>
            <div v-for="dd in sample.data.deductions" :key="dd.component" class="flex justify-between py-0.5 text-[12.5px]"><span class="text-ink-gray-7">{{ dd.component }}</span><span class="tnum text-ink-gray-9">{{ inr(dd.amount) }}</span></div>
            <div class="mt-2 flex justify-between border-t border-outline-gray-1 pt-2 text-[12.5px] font-medium text-ink-gray-9"><span>Total</span><span class="tnum">{{ inr(sample.data.total_deduction) }}</span></div>
          </div>
        </div>
        <div class="flex items-center justify-between bg-green-50 px-4 py-2.5">
          <span class="text-[12.5px] font-medium text-green-800">Net pay</span>
          <span class="tnum text-[15px] font-semibold text-green-800">{{ inr(sample.data.net_pay) }}</span>
        </div>
      </div>
      <div v-else-if="sample.data && !sample.data.ok" class="mt-3 rounded-md border border-outline-gray-1 bg-surface-gray-1 p-3 text-[12.5px] text-ink-gray-6">
        <span v-if="sample.data.reason === 'no_assignment'">Assign compensation first (the Pay step) to preview a payslip.</span>
        <span v-else>Couldn't compute a preview: {{ sample.data.error }}</span>
      </div>

      <div class="mt-5 flex justify-between">
        <Button variant="ghost" label="Back" @click="step = 4" />
        <div class="flex gap-2">
          <Button variant="subtle" theme="gray" label="Run payroll in Payroll →" @click="router.push({ name: 'HrPayrun' })" />
          <Button variant="solid" theme="blue" label="Finish" @click="step = 6" />
        </div>
      </div>
    </Card>

    <!-- 6: done -->
    <Card v-else>
      <div class="flex flex-col items-center gap-2 py-6 text-center">
        <div class="flex h-12 w-12 items-center justify-center rounded-full bg-green-50 text-green-600"><Icon name="check" :size="24" /></div>
        <div class="text-[16px] font-medium text-ink-gray-9">You're live 🎉</div>
        <p class="max-w-md text-[13px] text-ink-gray-6">Defaults applied, statutory engine on, people in, pay assigned and your first payroll run. Review compliance or head to the dashboard.</p>
        <div class="mt-3 flex gap-2">
          <Button variant="subtle" theme="gray" label="Compliance" @click="router.push({ name: 'CompliancePf' })" />
          <Button variant="solid" theme="blue" label="Go to dashboard" @click="router.push({ name: 'HrDashboard' })" />
        </div>
      </div>
    </Card>
  </div>
</template>
