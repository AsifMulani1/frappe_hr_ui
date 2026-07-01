<script setup>
import { ref, reactive, computed, watch } from "vue"
import { Button, FormControl, TextInput, createResource, toast } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import Drawer from "@/components/ui/Drawer.vue"
import EmptyState from "@/components/ui/EmptyState.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"

const list = createResource({ url: "frappe_hr_ui.api.get_my_tickets", auto: true })
const thread = createResource({ url: "frappe_hr_ui.api.get_ticket_thread" })
const active = ref(null)
const open = ref(false)

const tickets = computed(() => list.data?.tickets || [])
watch(tickets, (t) => { if (t.length && !active.value) select(t[0].name) })
function select(name) { active.value = name; thread.fetch({ name }) }
const cur = computed(() => thread.data || {})
const STATUS_TONE = { Open: "info", Replied: "warning", Resolved: "success", Closed: "neutral" }

const form = reactive({ subject: "", description: "", priority: "Medium" })
const raise = createResource({
  url: "frappe_hr_ui.api.raise_ticket",
  onSuccess() {
    toast.success("Ticket raised")
    open.value = false
    Object.assign(form, { subject: "", description: "", priority: "Medium" })
    list.reload()
  },
  onError(e) { toast.error(e?.messages?.[0] || "Couldn't raise ticket") },
})
function submitTicket() {
  if (!form.subject) { toast.error("Add a subject"); return }
  raise.submit({ ...form })
}

const replyText = ref("")
const reply = createResource({
  url: "frappe_hr_ui.api.reply_ticket",
  onSuccess() {
    replyText.value = ""
    if (active.value) thread.fetch({ name: active.value })
    list.reload()
  },
  onError(e) { toast.error(e?.messages?.[0] || "Couldn't send reply") },
})
function sendReply() {
  if (!active.value) return
  if (!replyText.value.trim()) { toast.error("Write a message first"); return }
  reply.submit({ name: active.value, message: replyText.value })
}
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Helpdesk" subtitle="Raise and track requests to HR, Payroll and IT">
      <template #actions><Button variant="solid" theme="blue" label="Raise a ticket" @click="open = true"><template #prefix><Icon name="plus" :size="15" /></template></Button></template>
    </PageHeader>

    <AsyncShell :resource="list" loading-text="Loading tickets…">
    <EmptyState v-if="!tickets.length && !list.loading" icon="help" title="No tickets yet" message="Raise a ticket and track HR/IT responses here." />

    <div v-else class="grid items-start gap-5" style="grid-template-columns: 360px minmax(0,1fr)">
      <Card :pad="false">
        <div class="flex flex-col">
          <Button v-for="(t, i) in tickets" :key="t.name" @click="select(t.name)"
            :variant="active === t.name ? 'subtle' : 'ghost'" theme="gray"
            class="w-full !justify-start border-b border-outline-gray-1 last:border-b-0">
            <div class="w-full">
              <div class="mb-1 flex justify-between">
                <span class="tnum text-[11.5px] font-medium text-ink-gray-5">{{ t.name }}</span>
                <StatusBadge :tone="STATUS_TONE[t.status] || 'neutral'" size="sm" dot :label="t.status" />
              </div>
              <div class="text-[13.5px] font-medium leading-snug text-ink-gray-9">{{ t.subject }}</div>
              <div class="mt-1.5 text-[11.5px] text-ink-gray-5">{{ t.updated }}</div>
            </div>
          </Button>
        </div>
      </Card>

      <Card :pad="false" class="flex min-h-[540px] flex-col">
        <div v-if="cur.id" class="border-b border-outline-gray-1 px-5 py-4">
          <div class="flex items-center gap-2">
            <span class="tnum text-[11.5px] font-medium text-ink-gray-5">{{ cur.id }}</span>
            <StatusBadge :tone="STATUS_TONE[cur.status] || 'neutral'" size="sm" dot :label="cur.status" />
          </div>
          <div class="mt-1 text-[16px] font-medium text-ink-gray-9">{{ cur.subject }}</div>
          <div class="mt-1 text-[12.5px] text-ink-gray-5">{{ cur.cat }}</div>
        </div>
        <div class="flex-1 space-y-4 overflow-y-auto bg-surface-gray-1 p-5">
          <div v-for="(m, i) in cur.thread || []" :key="i" class="flex gap-2.5" :class="m.me ? 'flex-row-reverse' : ''">
            <InitialsAvatar :name="m.who" :size="32" />
            <div class="max-w-[70%]">
              <div class="mb-1 flex items-baseline gap-2" :class="m.me ? 'justify-end' : ''">
                <span class="text-[12.5px] font-medium text-ink-gray-9">{{ m.me ? "You" : m.who }}</span>
                <span class="text-[11px] text-ink-gray-5">{{ m.time }}</span>
              </div>
              <div class="rounded-[10px] px-3 py-2.5 text-[13px] leading-relaxed"
                :class="m.me ? 'bg-blue-600 text-white' : 'border border-outline-gray-1 bg-surface-white text-ink-gray-9'">{{ m.text }}</div>
            </div>
          </div>
          <EmptyState v-if="!(cur.thread || []).length" icon="inbox" title="No replies yet" compact />
        </div>
        <div class="flex items-center gap-2.5 border-t border-outline-gray-1 p-3.5">
          <TextInput v-model="replyText" :disabled="!cur.id" placeholder="Write a reply…" class="flex-1" @keyup.enter="sendReply" />
          <Button variant="solid" theme="blue" label="Send" :loading="reply.loading" :disabled="!cur.id" @click="sendReply"><template #suffix><Icon name="arrowRight" :size="15" /></template></Button>
        </div>
      </Card>
    </div>
    </AsyncShell>

    <Drawer :open="open" title="Raise a ticket" subtitle="We'll route it to the right team" @close="open = false">
      <div class="flex flex-col gap-4">
        <FormControl type="text" label="Subject" placeholder="Brief summary of your request" v-model="form.subject" />
        <FormControl type="select" label="Priority" :options="['Low', 'Medium', 'High']" v-model="form.priority" />
        <FormControl type="textarea" label="Description" placeholder="Describe your request in detail…" v-model="form.description" />
      </div>
      <template #footer><Button variant="ghost" label="Cancel" @click="open = false" /><Button variant="solid" theme="blue" label="Submit ticket" :loading="raise.loading" @click="submitTicket" /></template>
    </Drawer>
  </div>
</template>
