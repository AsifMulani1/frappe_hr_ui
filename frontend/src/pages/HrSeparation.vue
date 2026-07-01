<script setup>
import { reactive, computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import CardHeader from "@/components/ui/CardHeader.vue"
import ProgressBar from "@/components/ui/ProgressBar.vue"
import EmptyState from "@/components/ui/EmptyState.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"
import FormDrawer from "@/components/ui/FormDrawer.vue"
import DetailDrawer from "@/components/ui/DetailDrawer.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"
import { useCreate, useLinkOptions } from "@/composables/useDocActions"

const r = createResource({ url: "frappe_hr_ui.api.get_separation", auto: true })
const rows = computed(() => r.data?.rows || [])

// Initiate exit (in-app)
const add = useCreate("Employee Separation", { onDone: () => r.reload(), successLabel: "Exit initiated" })
const employees = useLinkOptions("Employee")
const form = reactive({ employee: "", boarding_begins_on: "" })
const fields = computed(() => [
  { key: "employee", label: "Employee", type: "select", options: employees.value, cols: 2 },
  { key: "boarding_begins_on", label: "Exit process begins on", type: "date", cols: 2 },
])
function openAdd() {
  Object.assign(form, { employee: "", boarding_begins_on: "" })
  add.openDrawer()
}

// In-app detail view
const view = reactive({ open: false, name: "" })
function openView(s) {
  view.name = s.name
  view.open = true
}
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Separation & Exit" :subtitle="`${rows.length} employees on notice · manage clearances and F&F`">
      <template #actions><Button variant="solid" theme="blue" label="Initiate Exit" @click="openAdd"><template #prefix><Icon name="logout" :size="15" /></template></Button></template>
    </PageHeader>
    <AsyncShell :resource="r" loading-text="Loading separations…">
    <Card :pad="false">
      <div class="p-5 pb-3.5"><CardHeader title="On Notice Period" /></div>
      <EmptyState v-if="!rows.length && !r.loading" icon="logout" title="No active separations" compact />
      <div v-else class="flex flex-col">
        <div v-for="(s, i) in rows" :key="s.employee_name + i" class="flex items-center gap-4 border-t border-outline-gray-1 px-5 py-4">
          <InitialsAvatar :name="s.employee_name" :size="38" />
          <div class="w-40 min-w-0"><div class="text-sm font-medium text-ink-gray-9">{{ s.employee_name }}</div><div class="text-xs text-ink-gray-5">{{ s.designation }}</div></div>
          <div class="max-w-[200px] flex-1">
            <div class="mb-1.5 flex justify-between"><span class="text-xs text-ink-gray-5">LWD {{ s.lwd }}</span><span class="tnum text-xs font-medium">{{ s.progress }}%</span></div>
            <ProgressBar :value="s.progress" color="bg-orange-500" />
          </div>
          <Button variant="outline" theme="gray" size="sm" label="Clearance" @click="openView(s)"><template #suffix><Icon name="chevRight" :size="15" /></template></Button>
        </div>
      </div>
    </Card>
    </AsyncShell>

    <FormDrawer :open="add.open" title="Initiate Exit" subtitle="Start the separation process for an employee"
      :fields="fields" v-model="form" :loading="add.create.loading" submit-label="Initiate Exit"
      @close="add.open = false" @submit="add.submit(form, ['employee', 'boarding_begins_on'])" />
    <DetailDrawer :open="view.open" doctype="Employee Separation" :name="view.name" @close="view.open = false" />
  </div>
</template>
