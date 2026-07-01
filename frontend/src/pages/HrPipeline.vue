<script setup>
import { reactive, computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"
import FormDrawer from "@/components/ui/FormDrawer.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"
import { useCreate } from "@/composables/useDocActions"

const r = createResource({ url: "frappe_hr_ui.api.get_pipeline", auto: true })
const cols = computed(() => r.data?.columns || [])
const DOT = ["bg-ink-gray-4", "bg-blue-500", "bg-blue-500", "bg-green-500", "bg-ink-gray-4"]

const add = useCreate("Job Applicant", { onDone: () => r.reload(), successLabel: "Candidate added" })
const form = reactive({ applicant_name: "", email_id: "", status: "Open" })
const fields = computed(() => [
  { key: "applicant_name", label: "Applicant name", type: "text", cols: 2 },
  { key: "email_id", label: "Email", type: "email", cols: 2 },
  { key: "status", label: "Status", type: "select", options: ["Open", "Replied", "Shortlisted", "Rejected", "Hold", "Accepted"], cols: 2 },
])
function openAdd() {
  Object.assign(form, { applicant_name: "", email_id: "", status: "Open" })
  add.openDrawer()
}
</script>

<template>
  <div class="px-6 py-[22px]">
    <PageHeader title="Candidate Pipeline" subtitle="Drag candidates across stages">
      <template #actions><Button variant="solid" theme="blue" label="Add Candidate" @click="openAdd"><template #prefix><Icon name="plus" :size="15" /></template></Button></template>
    </PageHeader>
    <AsyncShell :resource="r" loading-text="Loading pipeline…">
    <div class="flex gap-3.5 overflow-x-auto pb-2">
      <div v-for="(col, ci) in cols" :key="col.id" class="flex flex-[0_0_268px] flex-col">
        <div class="flex items-center gap-2 px-1 pb-2.5">
          <span class="h-2 w-2 rounded-[3px]" :class="DOT[ci % DOT.length]" />
          <span class="text-sm font-medium">{{ col.label }}</span>
          <span class="rounded-full bg-surface-gray-2 px-2 text-xs text-ink-gray-5">{{ col.cards.length }}</span>
        </div>
        <div class="flex min-h-[200px] flex-col gap-2.5 rounded-[10px] border border-outline-gray-1 bg-surface-gray-1 p-2.5">
          <Card v-for="(c, i) in col.cards" :key="i" hover class="cursor-grab !p-3">
            <div class="flex gap-2.5">
              <InitialsAvatar :name="c.name" :size="34" />
              <div class="min-w-0"><div class="truncate text-sm font-medium text-ink-gray-9">{{ c.name }}</div><div class="truncate text-xs text-ink-gray-5">{{ c.role }}</div></div>
            </div>
          </Card>
          <div v-if="!col.cards.length" class="py-6 text-center text-xs text-ink-gray-5">Empty</div>
        </div>
      </div>
    </div>
    </AsyncShell>

    <FormDrawer :open="add.open" title="Add Candidate" subtitle="Add a new candidate to the pipeline"
      :fields="fields" v-model="form" :loading="add.create.loading" submit-label="Add Candidate"
      @close="add.open = false" @submit="add.submit(form, ['applicant_name', 'email_id'])" />
  </div>
</template>
