<script setup>
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import Icon from "@/components/ui/Icon.vue"

// Standard report catalogue (links into Frappe's report views).
const CATS = [
  { cat: "Payroll", icon: "rupee", reports: ["Salary register", "PF / ESI / PT register", "TDS computation", "Bank advice"] },
  { cat: "Attendance", icon: "calcheck", reports: ["Monthly muster roll", "Late & early-out", "Leave balance ledger"] },
  { cat: "People", icon: "users", reports: ["Headcount & demographics", "New joiners & exits", "Probation due"] },
  { cat: "Compliance", icon: "shield", reports: ["Form 16 batch", "Form 24Q", "Gratuity liability"] },
]
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Report builder" subtitle="Generate and schedule standard HR & payroll reports" />
    <div class="grid gap-5" style="grid-template-columns: repeat(auto-fill, minmax(290px, 1fr))">
      <Card v-for="c in CATS" :key="c.cat">
        <CardHeader :title="c.cat" :icon="c.icon" />
        <div class="flex flex-col">
          <button v-for="(rep, i) in c.reports" :key="rep" class="flex items-center gap-2.5 py-2.5 text-left hover:text-blue-600" :class="i ? 'border-t border-outline-gray-1' : ''">
            <Icon name="file" :size="15" class="text-ink-gray-5" /><span class="flex-1 text-[13px] text-ink-gray-9">{{ rep }}</span><Icon name="download" :size="14" class="text-ink-gray-4" />
          </button>
        </div>
      </Card>
    </div>
  </div>
</template>
