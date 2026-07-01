<script setup>
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"

defineProps({ people: { type: Array, default: () => [] } })
</script>

<template>
  <Card>
    <CardHeader title="Who's Out Today" :sub="`${people.length} away`" />
    <div v-if="people.length" class="flex flex-col gap-3">
      <div v-for="(p, i) in people" :key="i" class="flex items-center gap-2.5">
        <InitialsAvatar :name="p.name" :size="32" />
        <div class="min-w-0 flex-1">
          <div class="truncate text-sm font-medium text-ink-gray-9">{{ p.name }}</div>
          <div class="text-xs text-ink-gray-5">{{ p.note }}</div>
        </div>
        <span class="whitespace-nowrap text-xs text-ink-gray-5">{{ p.until }}</span>
      </div>
    </div>
    <div v-else class="py-4 text-center text-sm text-ink-gray-5">Everyone's in today.</div>
  </Card>
</template>
