<script setup>
import { computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import ProgressBar from "@/components/ui/ProgressBar.vue"
import EmptyState from "@/components/ui/EmptyState.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"

const r = createResource({ url: "frappe_hr_ui.api.get_separation", auto: true })
const rows = computed(() => r.data?.rows || [])
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Separation & exit" :subtitle="`${rows.length} employees on notice · manage clearances and F&F`">
      <template #actions><Button variant="solid" theme="gray" label="Initiate exit"><template #prefix><Icon name="logout" :size="15" /></template></Button></template>
    </PageHeader>
    <Card :pad="false">
      <div class="p-5 pb-3.5"><CardHeader title="On notice period" /></div>
      <EmptyState v-if="!rows.length && !r.loading" icon="logout" title="No active separations" compact />
      <div v-else class="flex flex-col">
        <div v-for="(s, i) in rows" :key="s.employee_name + i" class="flex items-center gap-4 border-t border-outline-gray-1 px-5 py-4">
          <InitialsAvatar :name="s.employee_name" :size="38" />
          <div class="w-40 min-w-0"><div class="text-[13.5px] font-medium text-ink-gray-9">{{ s.employee_name }}</div><div class="text-[11.5px] text-ink-gray-5">{{ s.designation }}</div></div>
          <div class="max-w-[200px] flex-1">
            <div class="mb-1.5 flex justify-between"><span class="text-[11.5px] text-ink-gray-5">LWD {{ s.lwd }}</span><span class="tnum text-[12px] font-medium">{{ s.progress }}%</span></div>
            <ProgressBar :value="s.progress" color="bg-orange-500" />
          </div>
          <Button variant="outline" theme="gray" size="sm" label="Clearance"><template #suffix><Icon name="chevRight" :size="15" /></template></Button>
        </div>
      </div>
    </Card>
  </div>
</template>
