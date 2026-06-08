<script setup>
import { Button, Badge } from "frappe-ui"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import Icon from "@/components/ui/Icon.vue"

defineProps({ tasks: { type: Array, default: () => [] } })

const TONE = { high: "red", medium: "orange", low: "gray" }
</script>

<template>
  <Card>
    <CardHeader title="Needs your attention" :sub="`${tasks.length} pending`" icon="inbox" />
    <div v-if="tasks.length" class="flex flex-col">
      <div
        v-for="(t, i) in tasks"
        :key="i"
        class="flex items-center gap-3 py-3"
        :class="i ? 'border-t border-outline-gray-1' : ''"
      >
        <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-surface-gray-2 text-ink-gray-7">
          <Icon :name="t.kind" :size="16" />
        </div>
        <div class="min-w-0 flex-1">
          <div class="text-[13.5px] font-medium text-ink-gray-9">{{ t.title }}</div>
          <div class="mt-px text-[12px] text-ink-gray-5">{{ t.due }}</div>
        </div>
        <Badge variant="subtle" :theme="TONE[t.priority] || 'gray'" size="sm" :label="t.priority" />
      </div>
    </div>
    <div v-else class="flex flex-col items-center gap-1.5 py-7 text-center">
      <Icon name="check" :size="22" class="text-green-500" />
      <div class="text-[13px] text-ink-gray-5">You're all caught up.</div>
    </div>
  </Card>
</template>
