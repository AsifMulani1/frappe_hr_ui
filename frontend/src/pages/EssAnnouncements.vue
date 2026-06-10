<script setup>
import { ref, computed } from "vue"
import { createResource, toast } from "frappe-ui"
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
            <div class="flex-1"><div class="text-[13px] font-medium text-ink-gray-9">{{ p.by }}</div><div class="text-[11.5px] text-ink-gray-5">{{ p.time }}</div></div>
          </div>
          <h3 class="mb-2 text-[16.5px] font-medium tracking-tight text-ink-gray-9">{{ p.title }}</h3>
          <p class="text-[13.5px] leading-relaxed text-ink-gray-7">{{ p.body }}</p>
          <div class="mt-4 flex items-center gap-5 border-t border-outline-gray-1 pt-3.5 text-[13px] font-medium text-ink-gray-6">
            <button class="inline-flex items-center gap-1.5" @click="acknowledge(p)"><Icon name="gift" :size="16" /> Acknowledge</button>
            <button class="inline-flex items-center gap-1.5" @click="share(p)"><Icon name="external" :size="15" /> Share</button>
          </div>
        </Card>
        <EmptyState v-if="!posts.length && !r.loading" icon="megaphone" title="No announcements yet" message="Company updates will appear here." />
      </div>
      <div class="flex flex-col gap-5">
        <Card>
          <div class="mb-3 text-[15px] font-medium text-ink-gray-9">Quick links</div>
          <div class="flex flex-col gap-0.5">
            <button v-for="[ic, t] in [['file', 'Employee handbook'], ['shield', 'Code of conduct'], ['gift', 'Benefits guide'], ['help', 'IT support']]" :key="t"
              @click="openQuickLink(t)"
              class="flex items-center gap-2.5 rounded-md px-2 py-2 text-left text-ink-gray-7 hover:bg-surface-gray-1">
              <Icon :name="ic" :size="16" /><span class="flex-1 text-[13px] text-ink-gray-9">{{ t }}</span><Icon name="external" :size="13" class="text-ink-gray-4" />
            </button>
          </div>
        </Card>
      </div>
    </div>
    </AsyncShell>
  </div>
</template>
