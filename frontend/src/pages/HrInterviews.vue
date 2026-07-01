<script setup>
import { ref, reactive, computed } from "vue"
import { Button, FormControl, createResource, toast } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import EmptyState from "@/components/ui/EmptyState.vue"
import Drawer from "@/components/ui/Drawer.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"
import FormDrawer from "@/components/ui/FormDrawer.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"
import { useCreate, useLinkOptions } from "@/composables/useDocActions"

const r = createResource({ url: "frappe_hr_ui.api.get_interviews", auto: true })
const items = computed(() => r.data?.interviews || [])

// Schedule interview (in-app)
const add = useCreate("Interview", { onDone: () => r.reload(), successLabel: "Interview scheduled" })
const interviewTypes = useLinkOptions("Interview Type")
const applicants = useLinkOptions("Job Applicant")
const form = reactive({ interview_type: "", job_applicant: "", scheduled_on: "", from_time: "", to_time: "", status: "Pending" })
const fields = computed(() => [
  { key: "job_applicant", label: "Candidate", type: "select", options: applicants.value, cols: 2 },
  { key: "interview_type", label: "Round", type: "select", options: interviewTypes.value, cols: 2 },
  { key: "scheduled_on", label: "Date", type: "date", cols: 2 },
  { key: "from_time", label: "From", type: "time", cols: 1 },
  { key: "to_time", label: "To", type: "time", cols: 1 },
])
function openAdd() {
  Object.assign(form, { interview_type: "", job_applicant: "", scheduled_on: "", from_time: "", to_time: "", status: "Pending" })
  add.openDrawer()
}

// Record feedback (in-app)
const fb = reactive({ open: false, interview: "", cand: "", result: "Cleared", note: "" })
const feedback = createResource({
  url: "frappe_hr_ui.api.set_interview_result",
  onSuccess() { toast.success("Feedback recorded"); fb.open = false; r.reload() },
  onError(e) { toast.error(e?.messages?.[0] || "Couldn't save feedback") },
})
function openFeedback(iv) {
  Object.assign(fb, { open: true, interview: iv.id, cand: iv.cand, result: "Cleared", note: "" })
}
function submitFeedback() {
  feedback.submit({ interview: fb.interview, result: fb.result, note: fb.note })
}
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Interview Scheduling" :subtitle="`${items.length} interviews`">
      <template #actions><Button variant="solid" theme="blue" label="Schedule Interview" @click="openAdd"><template #prefix><Icon name="plus" :size="15" /></template></Button></template>
    </PageHeader>
    <AsyncShell :resource="r" loading-text="Loading interviews…">
    <Card :pad="false">
      <div class="border-b border-outline-gray-1 p-5"><CardHeader title="Schedule" /></div>
      <EmptyState v-if="!items.length && !r.loading" icon="calendar" title="No interviews scheduled" compact />
      <div v-else class="flex flex-col">
        <div v-for="(iv, i) in items" :key="i" class="flex items-center gap-4 px-5 py-4" :class="i < items.length - 1 ? 'border-b border-outline-gray-1' : ''">
          <InitialsAvatar :name="iv.cand" :size="36" />
          <div class="flex-1"><div class="text-base font-medium text-ink-gray-9">{{ iv.cand }}</div><div class="text-xs text-ink-gray-7">{{ iv.round }} · {{ iv.when }}</div></div>
          <StatusBadge :tone="iv.status === 'Cleared' ? 'success' : 'neutral'" size="sm" :label="iv.status" />
          <Button variant="outline" theme="gray" size="sm" label="Feedback" @click="openFeedback(iv)" />
        </div>
      </div>
    </Card>
    </AsyncShell>

    <FormDrawer :open="add.open" title="Schedule Interview" subtitle="Set up an interview round"
      :fields="fields" v-model="form" :loading="add.create.loading" submit-label="Schedule"
      @close="add.open = false" @submit="add.submit(form, ['job_applicant', 'interview_type', 'scheduled_on', 'from_time', 'to_time'])" />

    <Drawer :open="fb.open" title="Interview Feedback" :subtitle="fb.cand" :width="440" @close="fb.open = false">
      <div class="flex flex-col gap-4">
        <FormControl type="select" label="Result" :options="['Cleared', 'Rejected', 'Under Review']" v-model="fb.result" />
        <FormControl type="textarea" label="Notes" placeholder="Summary of the round…" v-model="fb.note" />
      </div>
      <template #footer>
        <Button variant="ghost" label="Cancel" @click="fb.open = false" />
        <Button variant="solid" theme="blue" label="Save Feedback" :loading="feedback.loading" @click="submitFeedback" />
      </template>
    </Drawer>
  </div>
</template>
