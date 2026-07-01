<script setup>
import { ref, computed, watch } from "vue"
import { Button, createResource, confirmDialog, toast } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import AmountRow from "@/components/ui/AmountRow.vue"
import EmptyState from "@/components/ui/EmptyState.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"

const r = createResource({ url: "frappe_hr_ui.api.get_team_approvals", auto: true })
const action = createResource({
  url: "frappe_hr_ui.api.act_on_approval",
  onSuccess: () => r.reload(),
  onError: (e) => toast.error(e?.messages?.[0] || "Couldn't update the request"),
})
function runAction(item, a) {
  action.submit({ kind: item.kind, name: item.id, action: a }, {
    onSuccess: () => toast.success(a === "reject" ? "Request rejected" : "Request approved"),
  })
}
const sel = ref(null)
const items = computed(() => r.data?.items || [])
watch(items, (i) => { if (i.length && !sel.value) sel.value = i[0].id })
const cur = computed(() => items.value.find((x) => x.id === sel.value) || items.value[0])
function act(item, a) {
  if (a === "reject") {
    confirmDialog({
      title: "Reject request",
      message: `Reject this ${String(item.kind).toLowerCase()} from ${item.person}? This can't be undone.`,
      onConfirm: ({ hideDialog }) => { runAction(item, "reject"); hideDialog() },
    })
    return
  }
  runAction(item, a)
}
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Approvals" :subtitle="`${items.length} item(s) waiting on you`" />
    <AsyncShell :resource="r" loading-text="Loading approvals…">
    <EmptyState v-if="!items.length && !r.loading" icon="check" title="All caught up" message="No pending approvals to review." />
    <div v-else class="grid items-start gap-5" style="grid-template-columns: minmax(0,1fr) 380px">
      <Card :pad="false">
        <div class="flex flex-col">
          <div v-for="(a, i) in items" :key="a.id" @click="sel = a.id"
            class="flex cursor-pointer items-center gap-3 px-4 py-3.5" :class="[i < items.length - 1 ? 'border-b border-outline-gray-1' : '', cur && cur.id === a.id ? 'bg-blue-50' : '']">
            <div class="flex h-[34px] w-[34px] items-center justify-center rounded-md bg-surface-gray-2 text-ink-gray-7"><Icon :name="a.icon" :size="16" /></div>
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-2"><span class="text-sm font-medium text-ink-gray-9">{{ a.person }}</span><StatusBadge :tone="a.tone" size="sm" :label="a.kind" /></div>
              <div class="mt-0.5 text-xs text-ink-gray-7">{{ a.detail }} · <span class="tnum font-medium text-ink-gray-9">{{ a.amount }}</span></div>
            </div>
            <div class="flex gap-1.5" @click.stop>
              <Button variant="outline" theme="gray" size="sm" icon="lucide-x" @click="act(a, 'reject')" />
              <Button variant="solid" theme="blue" size="sm" icon="lucide-check" @click="act(a, 'approve')" />
            </div>
          </div>
        </div>
      </Card>
      <Card v-if="cur">
        <div class="mb-4 flex items-center gap-3">
          <InitialsAvatar :name="cur.person" :size="44" />
          <div><div class="text-md font-medium text-ink-gray-9">{{ cur.person }}</div><div class="tnum text-xs text-ink-gray-5">{{ cur.pid }}</div></div>
        </div>
        <div class="mb-4 flex flex-col gap-0.5">
          <AmountRow label="Request type" :value="cur.kind" />
          <AmountRow label="Reference" :value="cur.id" />
          <AmountRow label="Details" :value="cur.detail" />
          <AmountRow label="Amount / duration" :value="cur.amount" bold />
          <AmountRow label="Reason" :value="cur.sub" :border="false" />
        </div>
        <div class="flex gap-2">
          <Button variant="subtle" theme="red" class="flex-1" label="Reject" @click="act(cur, 'reject')"><template #prefix><Icon name="x" :size="15" /></template></Button>
          <Button variant="solid" theme="blue" class="flex-1" label="Approve" @click="act(cur, 'approve')"><template #prefix><Icon name="check" :size="15" /></template></Button>
        </div>
      </Card>
    </div>
    </AsyncShell>
  </div>
</template>
