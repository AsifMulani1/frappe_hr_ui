<script setup>
// Generic employee self-service request screen: lists the employee's own records
// of an ESS doctype and lets them raise a new one. Driven by route props, backed
// by create_doc (employee forced server-side) + get_my_docs.
import { ref, reactive, computed, watch } from "vue"
import { Button, createResource } from "frappe-ui"
import PageHeader from "@/components/ui/PageHeader.vue"
import Card from "@/components/ui/Card.vue"
import DataTable from "@/components/ui/DataTable.vue"
import StatusBadge from "@/components/ui/StatusBadge.vue"
import Icon from "@/components/ui/Icon.vue"
import FormDrawer from "@/components/ui/FormDrawer.vue"
import AsyncShell from "@/components/ui/AsyncShell.vue"
import { useCreate } from "@/composables/useDocActions"

const props = defineProps({
  doctype: { type: String, required: true },
  title: String,
  subtitle: String,
  addLabel: { type: String, default: "New Request" },
  fields: { type: Array, default: () => [] },     // [{key,label,type,linkDoctype?,select?,cols?,placeholder?}]
  required: { type: Array, default: () => [] },
  listColumns: { type: Array, default: () => [{ key: "name", label: "Reference" }] },
})

const r = createResource({ url: "frappe_hr_ui.api.get_my_docs", auto: true, params: { doctype: props.doctype } })
watch(() => props.doctype, () => r.fetch({ doctype: props.doctype }))
const rows = computed(() => r.data?.rows || [])

const linkOpts = reactive({})
function loadLinks() {
  props.fields.filter((f) => f.linkDoctype).forEach(async (f) => {
    const res = await createResource({ url: "frappe_hr_ui.doctype_api.search_link" }).fetch({ doctype: f.linkDoctype })
    linkOpts[f.key] = res?.options || []
  })
}
loadLinks()

const add = useCreate(props.doctype, { onDone: () => r.reload(), successLabel: "Request submitted" })
const form = reactive({})
function openNew() {
  Object.keys(form).forEach((k) => delete form[k])
  add.openDrawer()
}
const drawerFields = computed(() =>
  props.fields.map((f) => ({
    key: f.key, label: f.label, type: f.type, cols: f.cols || 2,
    placeholder: f.placeholder, options: f.linkDoctype ? linkOpts[f.key] : f.select,
  }))
)
const cols = computed(() => {
  const c = [...props.listColumns]
  if (r.data?.is_submittable && !c.find((x) => x.key === "docstatus")) c.push({ key: "docstatus", label: "Status" })
  return c
})
const DOCSTATUS = { 0: ["Draft", "neutral"], 1: ["Submitted", "success"], 2: ["Cancelled", "danger"] }
</script>

<template>
  <div class="mx-auto max-w-[1100px] px-6 py-[22px]">
    <PageHeader :title="title || doctype" :subtitle="subtitle">
      <template #actions>
        <Button variant="solid" theme="blue" :label="addLabel" @click="openNew"><template #prefix><Icon name="plus" :size="15" /></template></Button>
      </template>
    </PageHeader>

    <AsyncShell :resource="r" loading-text="Loading your requests…">
      <Card :pad="false" class="p-3">
        <DataTable :columns="cols" :rows="rows" row-key="name" :loading="r.loading"
          empty-title="No requests yet" :empty-message="`Raise a ${(title || doctype).toLowerCase()} using the button above.`">
          <template #cell-docstatus="{ row }">
            <StatusBadge :tone="DOCSTATUS[row.docstatus]?.[1] || 'neutral'" size="sm" dot :label="DOCSTATUS[row.docstatus]?.[0] || '—'" />
          </template>
        </DataTable>
      </Card>
    </AsyncShell>

    <FormDrawer :open="add.open" :title="addLabel" :subtitle="subtitle" :fields="drawerFields" v-model="form"
      :loading="add.create.loading" submit-label="Submit" @close="add.open = false" @submit="add.submit(form, required)" />
  </div>
</template>
