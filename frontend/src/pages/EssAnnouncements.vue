<script setup>
import { ref, computed } from "vue"
import { Button, createResource, toast } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import EmptyState from "@/components/ui/EmptyState.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"
import Icon from "@/components/ui/Icon.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"

const r = createResource({ url: "frappe_hr_ui.api.get_announcements_feed", auto: true })
const posts = computed(() => r.data?.posts || [])

function acknowledge(p) {
  toast.success("Marked as read")
}
function share(p) {
  const text = `${p.title}\n\n${p.body}`
  navigator.clipboard?.writeText(text)
  toast.success("Announcement copied to clipboard")
}
function openQuickLink(t) {
  toast.success(`Raise a request under Helpdesk to access the ${t.toLowerCase()}`)
}
</script>

<template>
  <div class="mx-auto max-w-[1100px] px-6 py-[22px]">
    <PageHeader title="Announcements" subtitle="Company-wide updates from leadership, People and Payroll" />
    <AsyncShell :resource="r" loading-text="Loading announcements…">
    <div class="grid items-start gap-5" style="grid-template-columns: minmax(0,1fr) 260px">
      <div class="flex flex-col gap-5">
        <Card v-for="p in posts" :key="p.id">
          <div class="mb-3 flex items-center gap-2.5">
            <InitialsAvatar :name="p.by" :size="36" />
            <div class="flex-1"><div class="text-sm font-medium text-ink-gray-9">{{ p.by }}</div><div class="text-xs text-ink-gray-5">{{ p.time }}</div></div>
          </div>
          <h3 class="mb-2 text-lg font-medium tracking-tight text-ink-gray-9">{{ p.title }}</h3>
          <p class="text-sm leading-relaxed text-ink-gray-7">{{ p.body }}</p>
          <div class="mt-4 flex items-center gap-5 border-t border-outline-gray-1 pt-3.5 text-sm font-medium text-ink-gray-6">
            <Button variant="ghost" size="sm" @click="acknowledge(p)"><template #prefix><Icon name="gift" :size="16" /></template>Acknowledge</Button>
            <Button variant="ghost" size="sm" @click="share(p)"><template #prefix><Icon name="external" :size="15" /></template>Share</Button>
          </div>
        </Card>
        <EmptyState v-if="!posts.length && !r.loading" icon="megaphone" title="No announcements yet" message="Company updates will appear here." />
      </div>
      <div class="flex flex-col gap-5">
        <Card>
          <div class="mb-3 text-md font-medium text-ink-gray-9">Quick Links</div>
          <div class="flex flex-col gap-0.5">
            <Button v-for="[ic, t] in [['file', 'Employee Handbook'], ['shield', 'Code of Conduct'], ['gift', 'Benefits Guide'], ['help', 'IT Support']]" :key="t"
              variant="ghost" class="w-full !justify-start"
              @click="openQuickLink(t)">
              <template #prefix><Icon :name="ic" :size="16" /></template>
              <span class="flex-1 text-left">{{ t }}</span>
              <template #suffix><Icon name="external" :size="13" class="text-ink-gray-4" /></template>
            </Button>
          </div>
        </Card>
      </div>
    </div>
    </AsyncShell>
  </div>
</template>
