<script setup>
import { computed } from "vue"
import { Button, createResource, toast } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import EmptyState from "@/components/ui/EmptyState.vue"
import Icon from "@/components/ui/Icon.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"

const r = createResource({ url: "frappe_hr_ui.api.get_survey", auto: true })
const surveys = computed(() => r.data?.surveys || [])

function newSurvey() {
  toast.success("Pulse surveys are published by People Ops — raise a Helpdesk request to launch one.")
}
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Survey Builder" subtitle="Pulse surveys, eNPS and feedback forms">
      <template #actions><Button variant="solid" theme="blue" label="New Survey" @click="newSurvey"><template #prefix><Icon name="plus" :size="15" /></template></Button></template>
    </PageHeader>
    <AsyncShell :resource="r" loading-text="Loading surveys…">
    <Card>
      <EmptyState v-if="!surveys.length" icon="edit" title="No surveys yet" message="Create a pulse survey or eNPS to gather feedback." />
    </Card>
    </AsyncShell>
  </div>
</template>
