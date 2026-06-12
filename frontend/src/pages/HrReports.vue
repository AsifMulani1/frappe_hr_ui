<script setup>
import { reactive } from "vue"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import Icon from "@/components/ui/Icon.vue"
import ReportDrawer from "@/components/ui/ReportDrawer.vue"

// Standard report catalogue (links into Frappe's report views).
const CATS = [
  { cat: "Payroll", icon: "rupee", reports: ["Salary register", "TDS computation", "Bank advice", "Bank mandate"] },
  { cat: "Statutory registers", icon: "shield", reports: ["Professional Tax register", "ESIC register", "LWF register", "PF / ESI / PT register"] },
  { cat: "Attendance", icon: "calcheck", reports: ["Monthly muster roll", "Late & early-out", "Leave balance ledger"] },
  { cat: "People", icon: "users", reports: ["Headcount & demographics", "New joiners & exits", "Probation due"] },
  { cat: "Compliance", icon: "shield", reports: ["Form 16 batch", "Form 24Q", "Gratuity liability"] },
]

// Map displayed catalogue labels to real Frappe report names.
const REPORT_MAP = {
  "Salary register": "Salary Register",
  "Professional Tax register": "Professional Tax Register",
  "PF / ESI / PT register": "Salary Register",
  "ESIC register": "ESIC Register",
  "LWF register": "LWF Register",
  "Bank mandate": "Bank Mandate Report",
  "TDS computation": "Income Tax Computation",
  "Bank advice": "Bank Remittance",
  "Monthly muster roll": "Monthly Attendance Sheet",
  "Late & early-out": "Monthly Attendance Sheet",
  "Leave balance ledger": "Employee Leave Balance",
  "Headcount & demographics": "Employee Information",
  "New joiners & exits": "Employee Information",
  "Probation due": "Employee Information",
  "Form 16 batch": "Income Tax Computation",
  "Form 24Q": "Income Tax Computation",
  "Gratuity liability": "Employee Information",
}
const report = reactive({ open: false, name: "", title: "" })
function openRep(label) {
  report.name = REPORT_MAP[label] || label
  report.title = label
  report.open = true
}
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Report builder" subtitle="Generate and schedule standard HR & payroll reports" />
    <div class="grid gap-5" style="grid-template-columns: repeat(auto-fill, minmax(290px, 1fr))">
      <Card v-for="c in CATS" :key="c.cat">
        <CardHeader :title="c.cat" :icon="c.icon" />
        <div class="flex flex-col">
          <button v-for="(rep, i) in c.reports" :key="rep" class="flex items-center gap-2.5 py-2.5 text-left hover:text-blue-600" :class="i ? 'border-t border-outline-gray-1' : ''" @click="openRep(rep)">
            <Icon name="file" :size="15" class="text-ink-gray-5" /><span class="flex-1 text-[13px] text-ink-gray-9">{{ rep }}</span><Icon name="download" :size="14" class="text-ink-gray-4" />
          </button>
        </div>
      </Card>
    </div>

    <ReportDrawer :open="report.open" :report="report.name" :title="report.title" @close="report.open = false" />
  </div>
</template>
