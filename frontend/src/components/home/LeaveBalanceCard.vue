<script setup>
import { Button } from "frappe-ui"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import ProgressBar from "@/components/ui/ProgressBar.vue"
import Icon from "@/components/ui/Icon.vue"
import { LEAVE_THEME } from "@/composables/useEmployeeHome"

defineProps({ balances: { type: Array, default: () => [] } })
</script>

<template>
  <Card>
    <CardHeader title="Leave balance" sub="Current financial year">
      <template #action>
        <Button variant="outline" theme="gray" size="sm" label="Apply">
          <template #prefix><Icon name="plus" :size="15" /></template>
        </Button>
      </template>
    </CardHeader>
    <div v-if="balances.length" class="grid grid-cols-4 gap-3.5">
      <div v-for="l in balances" :key="l.code" class="py-0.5">
        <div class="flex items-baseline gap-1.5">
          <span class="tnum text-[24px] font-medium text-ink-gray-9">{{ l.balance }}</span>
          <span class="text-[12.5px] text-ink-gray-5">/ {{ l.total }}</span>
        </div>
        <div class="my-2 text-[12.5px] font-medium text-ink-gray-7">{{ l.type }}</div>
        <ProgressBar :value="l.used" :max="l.total || 1" :color="(LEAVE_THEME[l.color] || LEAVE_THEME.blue).bar" :height="5" />
        <div class="mt-1.5 text-[11px] text-ink-gray-5">
          {{ l.used }} used<span v-if="l.pending"> · {{ l.pending }} pending</span>
        </div>
      </div>
    </div>
    <div v-else class="py-6 text-center text-[13px] text-ink-gray-5">No leave allocated yet.</div>
  </Card>
</template>
