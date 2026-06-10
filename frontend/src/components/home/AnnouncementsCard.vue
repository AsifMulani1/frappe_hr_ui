<script setup>
import { useRouter } from "vue-router"
import { Button } from "frappe-ui"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import Icon from "@/components/ui/Icon.vue"

defineProps({ announcements: { type: Array, default: () => [] } })
const router = useRouter()
</script>

<template>
  <Card>
    <CardHeader title="Announcements" icon="megaphone">
      <template #action>
        <Button variant="ghost" size="sm" label="All" @click="router.push('/announcements')">
          <template #suffix><Icon name="arrowRight" :size="15" /></template>
        </Button>
      </template>
    </CardHeader>
    <div v-if="announcements.length" class="flex flex-col">
      <div
        v-for="(a, i) in announcements"
        :key="a.id"
        class="cursor-pointer py-3"
        :class="i ? 'border-t border-outline-gray-1' : ''"
      >
        <div class="mb-1 flex items-center gap-2">
          <span class="text-[11.5px] text-ink-gray-5">{{ a.by }}</span>
          <span class="ml-auto text-[11.5px] text-ink-gray-5">{{ a.time }}</span>
        </div>
        <div class="text-[13.5px] font-medium text-ink-gray-9">{{ a.title }}</div>
        <div class="mt-0.5 line-clamp-2 text-[12.5px] leading-relaxed text-ink-gray-6">{{ a.excerpt }}</div>
      </div>
    </div>
    <div v-else class="py-4 text-center text-[13px] text-ink-gray-5">No announcements.</div>
  </Card>
</template>
