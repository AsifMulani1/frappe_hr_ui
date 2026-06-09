<script setup>
import { computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"

const r = createResource({ url: "frappe_hr_ui.api.get_pipeline", auto: true })
const cols = computed(() => r.data?.columns || [])
const DOT = ["bg-ink-gray-4", "bg-blue-500", "bg-blue-500", "bg-green-500", "bg-ink-gray-4"]
</script>

<template>
  <div class="px-6 py-[22px]">
    <PageHeader title="Candidate pipeline" subtitle="Drag candidates across stages">
      <template #actions><Button variant="solid" theme="gray" label="Add candidate"><template #prefix><Icon name="plus" :size="15" /></template></Button></template>
    </PageHeader>
    <div class="flex gap-3.5 overflow-x-auto pb-2">
      <div v-for="(col, ci) in cols" :key="col.id" class="flex flex-[0_0_268px] flex-col">
        <div class="flex items-center gap-2 px-1 pb-2.5">
          <span class="h-2 w-2 rounded-[3px]" :class="DOT[ci % DOT.length]" />
          <span class="text-[13.5px] font-medium">{{ col.label }}</span>
          <span class="rounded-full bg-surface-gray-2 px-2 text-[12px] text-ink-gray-5">{{ col.cards.length }}</span>
        </div>
        <div class="flex min-h-[200px] flex-col gap-2.5 rounded-[10px] border border-outline-gray-1 bg-surface-gray-1 p-2.5">
          <Card v-for="(c, i) in col.cards" :key="i" hover class="cursor-grab !p-3">
            <div class="flex gap-2.5">
              <InitialsAvatar :name="c.name" :size="34" />
              <div class="min-w-0"><div class="truncate text-[13px] font-medium text-ink-gray-9">{{ c.name }}</div><div class="truncate text-[11.5px] text-ink-gray-5">{{ c.role }}</div></div>
            </div>
          </Card>
          <div v-if="!col.cards.length" class="py-6 text-center text-[12px] text-ink-gray-5">Empty</div>
        </div>
      </div>
    </div>
  </div>
</template>
