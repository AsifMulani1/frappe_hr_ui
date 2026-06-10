<script setup>
import { useRouter } from "vue-router"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import Icon from "@/components/ui/Icon.vue"

const router = useRouter()

// Self-service shortcuts -> their destination screens.
const ACTIONS = [
  { id: "leave", label: "Apply for leave", icon: "calendar", to: "/leave" },
  { id: "payslip", label: "View payslip", icon: "file", to: "/payslips" },
  { id: "reimb", label: "Claim reimbursement", icon: "wallet", to: "/reimbursements" },
  { id: "expense", label: "Expense claim", icon: "card", to: "/expenses" },
  { id: "ticket", label: "Raise a ticket", icon: "help", to: "/helpdesk" },
  { id: "regular", label: "Regularize attendance", icon: "clock", to: "/attendance" },
]
</script>

<template>
  <Card>
    <CardHeader title="Quick actions" />
    <div class="grid grid-cols-3 gap-2.5">
      <button
        v-for="a in ACTIONS"
        :key="a.id"
        @click="router.push(a.to)"
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
