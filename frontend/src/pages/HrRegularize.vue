<script setup>
import { computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import EmptyState from "@/components/ui/EmptyState.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"

const r = createResource({ url: "frappe_hr_ui.api.get_regularizations", auto: true })
const items = computed(() => r.data?.items || [])
const pending = computed(() => items.value.filter((i) => i.st === "pending"))
</script>

<template>
  <div class="mx-auto max-w-[1100px] px-6 py-[22px]">
    <PageHeader title="Regularization queue" :subtitle="`${pending.length} attendance corrections awaiting review`">
      <template #actions><Button variant="outline" theme="gray" label="Approve all"><template #prefix><Icon name="check" :size="15" /></template></Button></template>
    </PageHeader>
    <Card :pad="false">
      <EmptyState v-if="!items.length && !r.loading" icon="inbox" title="Queue is clear" message="Attendance requests appear here for review." compact />
      <div v-else class="flex flex-col">
        <div v-for="(it, i) in items" :key="it.id" class="flex items-center gap-3.5 px-5 py-4" :class="[i < items.length - 1 ? 'border-b border-outline-gray-1' : '', it.st !== 'pending' ? 'opacity-60' : '']">
          <InitialsAvatar :name="it.name" :size="38" />
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2"><span class="text-[13.5px] font-medium text-ink-gray-9">{{ it.name }}</span><StatusBadge tone="neutral" size="sm" :label="it.date" /></div>
            <div class="mt-0.5 text-[12.5px] text-ink-gray-7">{{ it.reason }}</div>
          </div>
          <div v-if="it.st === 'pending'" class="flex gap-2">
            <Button variant="outline" theme="gray" size="sm" label="Reject" />
            <Button variant="solid" theme="gray" size="sm" label="Approve" />
          </div>
          <StatusBadge v-else tone="success" size="sm" dot label="Approved" />
        </div>
      </div>
    </Card>
  </div>
</template>
