<script setup>
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import Icon from "@/components/ui/Icon.vue"

// Static shortcuts (route as each target screen ships).
const ACTIONS = [
  { id: "leave", label: "Apply for leave", icon: "calendar" },
  { id: "payslip", label: "View payslip", icon: "file" },
  { id: "reimb", label: "Claim reimbursement", icon: "wallet" },
  { id: "expense", label: "Expense claim", icon: "card" },
  { id: "ticket", label: "Raise a ticket", icon: "help" },
  { id: "regular", label: "Regularize attendance", icon: "clock" },
]
</script>

<template>
  <Card>
    <CardHeader title="Quick actions" />
    <div class="grid grid-cols-3 gap-2.5">
      <button
        v-for="a in ACTIONS"
        :key="a.id"
        class="flex items-center gap-2.5 rounded-md border border-outline-gray-1 bg-surface-white px-3 py-2.5 text-left transition-colors hover:border-outline-gray-2 hover:bg-surface-gray-1"
      >
        <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-blue-50 text-blue-600">
          <Icon :name="a.icon" :size="17" />
        </div>
        <span class="text-[13px] font-medium text-ink-gray-9">{{ a.label }}</span>
      </button>
    </div>
  </Card>
</template>
