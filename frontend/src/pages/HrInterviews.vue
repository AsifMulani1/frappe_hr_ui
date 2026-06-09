<script setup>
import { computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import EmptyState from "@/components/ui/EmptyState.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"

const r = createResource({ url: "frappe_hr_ui.api.get_interviews", auto: true })
const items = computed(() => r.data?.interviews || [])
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Interview scheduling" :subtitle="`${items.length} interviews`">
      <template #actions><Button variant="solid" theme="gray" label="Schedule interview"><template #prefix><Icon name="plus" :size="15" /></template></Button></template>
    </PageHeader>
    <Card :pad="false">
      <div class="border-b border-outline-gray-1 p-5"><CardHeader title="Schedule" /></div>
      <EmptyState v-if="!items.length && !r.loading" icon="calendar" title="No interviews scheduled" compact />
      <div v-else class="flex flex-col">
        <div v-for="(iv, i) in items" :key="i" class="flex items-center gap-4 px-5 py-4" :class="i < items.length - 1 ? 'border-b border-outline-gray-1' : ''">
          <InitialsAvatar :name="iv.cand" :size="36" />
          <div class="flex-1"><div class="text-[14px] font-medium text-ink-gray-9">{{ iv.cand }}</div><div class="text-[12.5px] text-ink-gray-7">{{ iv.round }} · {{ iv.when }}</div></div>
          <StatusBadge :tone="iv.status === 'Cleared' ? 'success' : 'neutral'" size="sm" :label="iv.status" />
          <Button variant="outline" theme="gray" size="sm" label="Feedback" />
        </div>
      </div>
    </Card>
  </div>
</template>
