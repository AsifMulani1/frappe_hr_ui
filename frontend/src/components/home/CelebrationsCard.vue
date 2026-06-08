<script setup>
import { Avatar, Button } from "frappe-ui"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"

defineProps({ celebrations: { type: Array, default: () => [] } })
</script>

<template>
  <Card>
    <CardHeader title="Celebrations" icon="gift" />
    <div v-if="celebrations.length" class="flex flex-col gap-3">
      <div v-for="(c, i) in celebrations" :key="i" class="flex items-center gap-2.5">
        <Avatar :label="c.name" size="md" />
        <div class="min-w-0 flex-1">
          <div class="text-[13px] font-medium text-ink-gray-9">{{ c.name }}</div>
          <div class="text-[11.5px] text-ink-gray-5">{{ c.label }} · {{ c.sub }}</div>
        </div>
        <Button variant="subtle" theme="gray" size="sm" label="Congrats" />
      </div>
    </div>
    <div v-else class="py-4 text-center text-[13px] text-ink-gray-5">No celebrations this week.</div>
  </Card>
</template>
