<script setup>
import { reactive, computed } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import Icon from "@/components/ui/Icon.vue"
import InitialsAvatar from "@/components/ui/InitialsAvatar.vue"
import FormDrawer from "@/components/ui/FormDrawer.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"
import { useCreate, useLinkOptions } from "@/composables/useDocActions"

const r = createResource({ url: "frappe_hr_ui.api.get_org_builder", auto: true })
const d = computed(() => r.data || {})

// Add department (in-app structural edit)
const add = useCreate("Department", { onDone: () => r.reload(), successLabel: "Department added" })
const departments = useLinkOptions("Department")
const form = reactive({ department_name: "", parent_department: "" })
const fields = computed(() => [
  { key: "department_name", label: "Department name", type: "text", placeholder: "e.g. Platform Engineering", cols: 2 },
  { key: "parent_department", label: "Reports under", type: "select", options: departments.value, cols: 2 },
])
function openAdd() {
  Object.assign(form, { department_name: "", parent_department: "" })
  add.openDrawer()
}
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader title="Org Chart Builder" subtitle="Company reporting structure">
      <template #actions><Button variant="solid" theme="blue" label="Add Department" @click="openAdd"><template #prefix><Icon name="plus" :size="15" /></template></Button></template>
    </PageHeader>
    <AsyncShell :resource="r" loading-text="Loading org chart…">
    <Card class="overflow-x-auto !p-10">
      <div class="flex min-w-[760px] flex-col items-center">
        <Card v-if="d.top" class="min-w-[190px] text-center !border-blue-100 !bg-blue-50 !px-4 !py-3">
          <div class="mb-2 flex justify-center"><InitialsAvatar :name="d.top.employee_name" :size="42" /></div>
          <div class="text-base font-medium text-ink-gray-9">{{ d.top.employee_name }}</div>
          <div class="text-xs text-ink-gray-7">{{ d.top.designation }}</div>
        </Card>
        <div v-if="(d.heads || []).length" class="h-6 w-0.5 bg-outline-gray-2" />
        <div v-if="(d.heads || []).length" class="relative flex flex-wrap justify-center gap-5">
          <div class="absolute left-[12%] right-[12%] top-0 h-0.5 bg-outline-gray-2" />
          <div v-for="h in d.heads" :key="h.name" class="flex flex-col items-center">
            <div class="h-6 w-0.5 bg-outline-gray-2" />
            <Card hover class="min-w-[140px] cursor-pointer text-center !px-3.5 !py-3">
              <div class="mb-1.5 flex justify-center"><InitialsAvatar :name="h.name" :size="34" /></div>
              <div class="text-xs font-medium text-ink-gray-9">{{ h.name }}</div>
              <div class="text-2xs text-ink-gray-5">{{ h.dept }}</div>
              <div class="mt-1.5"><StatusBadge tone="neutral" size="sm" :label="`${h.reports} reports`" /></div>
            </Card>
          </div>
        </div>
      </div>
    </Card>
    </AsyncShell>

    <FormDrawer :open="add.open" title="Add Department" subtitle="Add a team to the reporting structure"
      :fields="fields" v-model="form" :loading="add.create.loading" submit-label="Add Department"
      @close="add.open = false" @submit="add.submit(form, ['department_name'])" />
  </div>
</template>
