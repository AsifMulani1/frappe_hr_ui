<script setup>
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"

defineProps({ holidays: { type: Array, default: () => [] } })
</script>

<template>
  <Card>
    <CardHeader title="Upcoming holidays" icon="calendar" />
    <div v-if="holidays.length" class="flex flex-col gap-0.5">
      <div
        v-for="(h, i) in holidays"
        :key="i"
        class="flex items-center gap-3 py-2"
        :class="i ? 'border-t border-outline-gray-1' : ''"
      >
        <div class="w-[42px] shrink-0 text-center">
          <div class="tnum text-[16px] font-medium leading-none text-ink-gray-9">{{ h.date }}</div>
          <div class="text-[11px] uppercase tracking-[.03em] text-ink-gray-5">{{ h.mon }}</div>
        </div>
        <div class="h-[26px] w-px bg-outline-gray-1" />
        <div class="min-w-0 flex-1">
          <div class="text-[13px] font-medium text-ink-gray-9">{{ h.name }}</div>
          <div class="text-[11.5px] text-ink-gray-5">{{ h.day }}</div>
        </div>
      </div>
    </div>
    <div v-else class="py-4 text-center text-[13px] text-ink-gray-5">No upcoming holidays.</div>
  </Card>
</template>
