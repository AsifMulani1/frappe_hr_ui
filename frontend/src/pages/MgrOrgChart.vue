<script setup>
import { computed } from "vue"
import { createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"

const r = createResource({ url: "frappe_hr_ui.api.get_org_chart", auto: true })
const d = computed(() => r.data || {})
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Org chart" subtitle="Your reporting structure" />
    <Card class="overflow-x-auto !p-10">
      <div class="flex min-w-[760px] flex-col items-center">
        <Card v-if="d.manager" class="min-w-[190px] text-center !border-blue-100 !bg-blue-50 !px-4 !py-3">
          <div class="mb-2 flex justify-center"><InitialsAvatar :name="d.manager.name" :size="42" /></div>
          <div class="text-[14px] font-medium text-ink-gray-9">{{ d.manager.name }}</div>
          <div class="text-[11.5px] text-ink-gray-7">{{ d.manager.designation }}</div>
        </Card>
        <div v-if="(d.reports || []).length" class="h-6 w-0.5 bg-outline-gray-2" />
        <div v-if="(d.reports || []).length" class="relative flex gap-5">
          <div class="absolute left-[12%] right-[12%] top-0 h-0.5 bg-outline-gray-2" />
          <div v-for="rp in d.reports" :key="rp.name" class="flex flex-col items-center">
            <div class="h-6 w-0.5 bg-outline-gray-2" />
            <Card hover class="min-w-[140px] cursor-pointer text-center !px-3.5 !py-3">
              <div class="mb-1.5 flex justify-center"><InitialsAvatar :name="rp.name" :size="34" /></div>
              <div class="text-[12.5px] font-medium text-ink-gray-9">{{ rp.name }}</div>
              <div class="text-[11px] text-ink-gray-5">{{ rp.designation }}</div>
            </Card>
          </div>
        </div>
      </div>
    </Card>
  </div>
</template>
