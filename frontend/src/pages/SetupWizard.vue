<script setup>
// Self-serviceable onboarding — apply India defaults, import employees, go live.
// All in-UI; no Desk.
import { ref, reactive, computed } from "vue"
import { Button, createResource, toast } from "frappe-ui"
import { useRouter, useRoute } from "vue-router"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import Icon from "@/components/ui/Icon.vue"

const router = useRouter()
const route = useRoute()
const STEPS = ["Overview", "Defaults", "Employees", "Done"]
// deep-link: /setup?step=employees jumps straight to the importer
const step = ref(route.query.step === "employees" ? 3 : 1)

const status = createResource({ url: "frappe_hr_ui.india_defaults.defaults_status", auto: true })
const applyDefaults = createResource({ url: "frappe_hr_ui.india_defaults.apply_defaults" })
const tpl = createResource({ url: "frappe_hr_ui.employee_import.import_template", auto: true })
const importRes = createResource({ url: "frappe_hr_ui.employee_import.import_employees" })

const s = computed(() => status.data || {})

function runDefaults() {
  applyDefaults.submit({}, {
    onSuccess: () => { toast.success("Defaults applied"); status.reload() },
    onError: (e) => toast.error(e?.messages?.[0] || "Couldn't apply defaults"),
  })
}

// --- CSV import ---
const parsed = reactive({ rows: [], headers: [] })
const fileName = ref("")
function splitLine(line) {
  const out = []; let cur = "", q = false
  for (const ch of line) {
    if (ch === '"') q = !q
    else if (ch === "," && !q) { out.push(cur); cur = "" }
    else cur += ch
  }
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
    parsed.rows = lines.slice(1).map((l) => {
      const cells = splitLine(l); const o = {}
      headers.forEach((h, i) => (o[h] = (cells[i] || "").trim()))
      return o
    })
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
  const header = tpl.data?.header || ""
  const blob = new Blob([header + "\n"], { type: "text/csv" })
  const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "employees-template.csv"
  a.click(); URL.revokeObjectURL(a.href)
}
const cols = computed(() => tpl.data?.columns || [])
</script>

<template>
  <div class="mx-auto max-w-[820px] px-6 py-[22px]">
    <PageHeader title="Setup" subtitle="Get your company live — defaults, people, payroll. No Desk needed." />

    <!-- stepper -->
    <div class="mb-5 flex items-center gap-2">
      <template v-for="(label, i) in STEPS" :key="i">
        <div class="flex items-center gap-2">
          <div class="flex h-6 w-6 items-center justify-center rounded-full text-[12px] font-medium"
            :class="step > i + 1 ? 'bg-blue-600 text-white' : step === i + 1 ? 'bg-blue-100 text-blue-700' : 'bg-surface-gray-2 text-ink-gray-5'">
            <Icon v-if="step > i + 1" name="check" :size="13" /><span v-else>{{ i + 1 }}</span>
          </div>
          <span class="text-[12.5px]" :class="step === i + 1 ? 'font-medium text-ink-gray-9' : 'text-ink-gray-5'">{{ label }}</span>
        </div>
        <div v-if="i < STEPS.length - 1" class="h-px w-6 bg-outline-gray-2" />
      </template>
    </div>

    <!-- 1: overview -->
    <Card v-if="step === 1">
      <div class="text-[15px] font-medium text-ink-gray-9">Welcome 👋</div>
      <p class="mt-1 text-[13px] text-ink-gray-6">We'll set up the essentials for <b>{{ s.company || "your company" }}</b> — salary components, leave types, a salary structure, and a holiday calendar — then import your team.</p>
      <div class="mt-4 grid grid-cols-3 gap-3">
        <div class="rounded-md border border-outline-gray-1 p-3"><div class="tnum text-[20px] font-medium">{{ s.components ?? "—" }}</div><div class="text-[11.5px] text-ink-gray-5">salary components</div></div>
        <div class="rounded-md border border-outline-gray-1 p-3"><div class="tnum text-[20px] font-medium">{{ s.leave_types ?? "—" }}</div><div class="text-[11.5px] text-ink-gray-5">leave types</div></div>
        <div class="rounded-md border border-outline-gray-1 p-3"><div class="tnum text-[20px] font-medium">{{ s.employees ?? "—" }}</div><div class="text-[11.5px] text-ink-gray-5">employees</div></div>
      </div>
      <div class="mt-5 flex justify-end"><Button variant="solid" theme="blue" label="Get started" @click="step = 2" /></div>
    </Card>

    <!-- 2: defaults -->
    <Card v-else-if="step === 2">
      <div class="text-[15px] font-medium text-ink-gray-9">India payroll defaults</div>
      <p class="mt-1 text-[13px] text-ink-gray-6">Applies standard Indian salary components, leave types, a salary structure and a national holiday list. Safe to run again — it only adds what's missing.</p>
      <div class="mt-4 flex flex-col gap-2">
        <div class="flex items-center justify-between rounded-md border border-outline-gray-1 px-3 py-2 text-[13px]"><span>Salary components</span><StatusBadge :tone="s.components ? 'success' : 'neutral'" size="sm" :label="`${s.components || 0}`" /></div>
        <div class="flex items-center justify-between rounded-md border border-outline-gray-1 px-3 py-2 text-[13px]"><span>Leave types</span><StatusBadge :tone="s.leave_types ? 'success' : 'neutral'" size="sm" :label="`${s.leave_types || 0}`" /></div>
        <div class="flex items-center justify-between rounded-md border border-outline-gray-1 px-3 py-2 text-[13px]"><span>Salary structure</span><StatusBadge :tone="s.has_structure ? 'success' : 'neutral'" size="sm" :label="s.has_structure ? 'Ready' : 'None'" /></div>
        <div class="flex items-center justify-between rounded-md border border-outline-gray-1 px-3 py-2 text-[13px]"><span>Holiday lists</span><StatusBadge :tone="s.holiday_lists ? 'success' : 'neutral'" size="sm" :label="`${s.holiday_lists || 0}`" /></div>
      </div>
      <div class="mt-5 flex justify-between">
        <Button variant="ghost" label="Back" @click="step = 1" />
        <div class="flex gap-2">
          <Button variant="subtle" theme="gray" label="Apply India defaults" :loading="applyDefaults.loading" @click="runDefaults" />
          <Button variant="solid" theme="blue" label="Next" @click="step = 3" />
        </div>
      </div>
    </Card>

    <!-- 3: employees -->
    <Card v-else-if="step === 3">
      <div class="flex items-center justify-between">
        <div class="text-[15px] font-medium text-ink-gray-9">Import employees</div>
        <Button variant="ghost" size="sm" label="Download CSV template" @click="downloadTemplate" />
      </div>
      <p class="mt-1 text-[13px] text-ink-gray-6">Columns: {{ cols.map((c) => c.label + (c.reqd ? '*' : '')).join(", ") }}</p>
      <label class="mt-3 flex cursor-pointer items-center justify-center gap-2 rounded-md border border-dashed border-outline-gray-2 py-6 text-[13px] text-ink-gray-6 hover:bg-surface-gray-1">
        <Icon name="download" :size="16" /> {{ fileName || "Choose a CSV file…" }}
        <input type="file" accept=".csv,text/csv" class="hidden" @change="onFile" />
      </label>

      <div v-if="parsed.rows.length" class="mt-3">
        <div class="mb-1 text-[12px] text-ink-gray-5">{{ parsed.rows.length }} rows · preview</div>
        <div class="max-h-[220px] overflow-auto rounded-md border border-outline-gray-1">
          <table class="w-full text-[12px]">
            <thead><tr class="border-b border-outline-gray-1 text-left text-ink-gray-5"><th v-for="c in cols" :key="c.key" class="px-2 py-1.5 font-medium">{{ c.label }}</th></tr></thead>
            <tbody>
              <tr v-for="(row, i) in parsed.rows.slice(0, 8)" :key="i" class="border-b border-outline-gray-1 last:border-0">
                <td v-for="c in cols" :key="c.key" class="px-2 py-1.5 text-ink-gray-8">{{ row[c.key] }}</td>
              </tr>
            </tbody>
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
          <Button variant="solid" theme="blue" label="Finish" @click="step = 4" />
        </div>
      </div>
    </Card>

    <!-- 4: done -->
    <Card v-else>
      <div class="flex flex-col items-center gap-2 py-6 text-center">
        <div class="flex h-12 w-12 items-center justify-center rounded-full bg-green-50 text-green-600"><Icon name="check" :size="24" /></div>
        <div class="text-[16px] font-medium text-ink-gray-9">You're set up</div>
        <p class="max-w-md text-[13px] text-ink-gray-6">Defaults are applied and your team is in. Review people, configure salary structures, or run payroll — all from here.</p>
        <div class="mt-3 flex gap-2">
          <Button variant="subtle" theme="gray" label="Employee directory" @click="router.push({ name: 'HrDirectory' })" />
          <Button variant="solid" theme="blue" label="Go to dashboard" @click="router.push({ name: 'HrDashboard' })" />
        </div>
      </div>
    </Card>
  </div>
</template>
