<script setup>
import { computed } from "vue"
import { Button, createResource, toast } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import StatTiles from "@/components/ui/StatTiles.vue"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import Icon from "@/components/ui/Icon.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"

const r = createResource({ url: "frappe_hr_ui.api.get_reconcile", auto: true })
const d = computed(() => r.data || {})
const tiles = computed(() => [
  { label: "Checks passed", value: `${d.value.passed ?? 0} / ${d.value.total ?? 0}`, sub: "validations", icon: "check", tone: "success" },
  { label: "Warnings", value: d.value.warnings ?? 0, sub: "review advised", icon: "bell", tone: "warning" },
  { label: "Blockers", value: d.value.blockers ?? 0, sub: "must fix", icon: "x", tone: "danger" },
])
const ST = { pass: ["check", "text-green-600", "bg-green-50"], warn: ["bell", "text-orange-600", "bg-orange-50"], fail: ["x", "text-red-600", "bg-red-50"] }
</script>

<template>
  <div class="mx-auto max-w-[1100px] px-6 py-[22px]">
    <PageHeader title="Reconciliation" subtitle="Pre-disbursement validation">
      <template #actions><Button variant="solid" theme="blue" label="Mark reconciled" @click="toast.success('Marked as reconciled')"><template #prefix><Icon name="check" :size="15" /></template></Button></template>
    </PageHeader>
    <AsyncShell :resource="r" loading-text="Loading reconciliation…">
    <StatTiles :items="tiles" :cols="3" />
    <Card>
      <CardHeader title="Validation checks" sub="Run before locking payroll" />
      <div class="flex flex-col">
        <div v-for="(c, i) in d.checks || []" :key="i" class="flex items-center gap-3 py-3.5" :class="i ? 'border-t border-outline-gray-1' : ''">
          <div class="flex h-[26px] w-[26px] items-center justify-center rounded-full" :class="[ST[c.st][2], ST[c.st][1]]"><Icon :name="ST[c.st][0]" :size="15" :stroke-width="2.4" /></div>
          <div class="flex-1"><div class="text-[13.5px] font-medium text-ink-gray-9">{{ c.label }}</div><div class="text-[12px] text-ink-gray-5">{{ c.detail }}</div></div>
          <Button v-if="c.st !== 'pass'" variant="outline" theme="gray" size="sm" label="Resolve" @click="toast.success('Marked resolved')" />
        </div>
      </div>
    </Card>
    </AsyncShell>
  </div>
</template>
