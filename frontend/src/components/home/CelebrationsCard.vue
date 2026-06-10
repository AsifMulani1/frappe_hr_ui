<script setup>
import { Button, toast } from "frappe-ui"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"

defineProps({ celebrations: { type: Array, default: () => [] } })
function congratulate(c) {
  toast.success(`Your wishes were sent to ${c.name} 🎉`)
}
</script>

<template>
  <Card>
    <CardHeader title="Celebrations" icon="gift" />
    <div v-if="celebrations.length" class="flex flex-col gap-3">
      <div v-for="(c, i) in celebrations" :key="i" class="flex items-center gap-2.5">
        <InitialsAvatar :name="c.name" :size="32" />
        <div class="min-w-0 flex-1">
          <div class="text-[13px] font-medium text-ink-gray-9">{{ c.name }}</div>
          <div class="text-[11.5px] text-ink-gray-5">{{ c.label }} · {{ c.sub }}</div>
        </div>
        <Button variant="subtle" theme="gray" size="sm" label="Congrats" @click="congratulate(c)" />
      </div>
    </div>
    <div v-else class="py-4 text-center text-[13px] text-ink-gray-5">No celebrations this week.</div>
  </Card>
</template>
