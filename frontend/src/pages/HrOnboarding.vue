<script setup>
import { computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import ProgressBar from "@/components/ui/ProgressBar.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import EmptyState from "@/components/ui/EmptyState.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"

const r = createResource({ url: "frappe_hr_ui.api.get_onboarding", auto: true })
const hires = computed(() => r.data?.hires || [])
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Onboarding" :subtitle="`${hires.length} new hires in the window`">
      <template #actions><Button variant="solid" theme="gray" label="Start onboarding"><template #prefix><Icon name="plus" :size="15" /></template></Button></template>
    </PageHeader>
    <Card :pad="false">
      <div class="p-5 pb-3.5"><CardHeader title="New hires" sub="Recent and upcoming joiners" /></div>
      <EmptyState v-if="!hires.length && !r.loading" icon="login" title="No recent joiners" compact />
      <div v-else class="flex flex-col">
        <div v-for="(h, i) in hires" :key="h.employee_name + i" class="flex items-center gap-4 border-t border-outline-gray-1 px-5 py-4">
          <InitialsAvatar :name="h.employee_name" :size="38" />
          <div class="w-44 min-w-0"><div class="text-[13.5px] font-medium text-ink-gray-9">{{ h.employee_name }}</div><div class="text-[11.5px] text-ink-gray-5">{{ h.designation }}</div></div>
          <div class="max-w-[200px] flex-1">
            <div class="mb-1.5 flex justify-between"><span class="text-[11.5px] text-ink-gray-5">Starts {{ h.start }}</span><span class="tnum text-[12px] font-medium">{{ h.progress }}%</span></div>
            <ProgressBar :value="h.progress" :color="h.progress === 100 ? 'bg-green-500' : 'bg-blue-500'" />
          </div>
          <StatusBadge :tone="h.progress === 100 ? 'success' : 'warning'" size="sm" :label="h.progress === 100 ? 'Ready' : 'In progress'" />
          <Button variant="outline" theme="gray" size="sm" label="Open"><template #suffix><Icon name="chevRight" :size="15" /></template></Button>
        </div>
      </div>
    </Card>
  </div>
</template>
