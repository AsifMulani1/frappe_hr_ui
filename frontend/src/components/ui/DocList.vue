<script setup>
// Generic, metadata-driven list view for ANY hrms doctype, backed by the
// permission-aware engine. Pairs with DocForm for create/edit. No Desk needed.
import { ref, reactive, computed, watch } from "vue"
import { Button, createResource, toast, confirmDialog } from "frappe-ui"
import PageHeader from "./PageHeader.vue"
import Card from "./Card.vue"
import DataTable from "./DataTable.vue"
import StatusBadge from "./StatusBadge.vue"
import EmptyState from "./EmptyState.vue"
import Icon from "./Icon.vue"
import DocForm from "./DocForm.vue"

const props = defineProps({
  doctype: { type: String, required: true },
  title: String,
  subtitle: String,
})

const q = ref("")
const start = ref(0)
const PAGE = 20
const meta = createResource({ url: "frappe_hr_ui.doctype_api.get_meta", params: { doctype: props.doctype }, auto: true })
const list = createResource({ url: "frappe_hr_ui.doctype_api.get_list" })

function fetchList() {
  list.fetch({ doctype: props.doctype, search: q.value || undefined, start: start.value, page_length: PAGE })
}
watch(() => props.doctype, () => { start.value = 0; q.value = ""; fetchList() }, { immediate: true })
let t
watch(q, () => { clearTimeout(t); t = setTimeout(() => { start.value = 0; fetchList() }, 250) })

const rows = computed(() => list.data?.rows || [])
const columns = computed(() => {
  const cols = (list.data?.columns || ["name"]).filter((c) => c !== "docstatus")
  return cols.map((c) => ({ key: c, label: c === "name" ? "ID" : c.replace(/_/g, " ").replace(/\b\w/g, (m) => m.toUpperCase()) }))
    .concat(list.data?.is_submittable ? [{ key: "docstatus", label: "Status" }] : [])
})
const canCreate = computed(() => meta.data?.perms?.create)

const drawer = reactive({ open: false, name: null })
function openNew() { drawer.name = null; drawer.open = true }
function openRow(row) { drawer.name = row.name; drawer.open = true }
function onSaved() { fetchList() }

const del = createResource({ url: "frappe_hr_ui.doctype_api.delete_doc" })
function confirmDelete(row) {
  confirmDialog({
    title: `Delete ${props.doctype}`,
    message: `Delete “${row.name}”? This can't be undone.`,
    onConfirm: ({ hideDialog }) => {
      del.submit({ doctype: props.doctype, name: row.name }, {
        onSuccess: () => { toast.success("Deleted"); fetchList() },
        onError: (e) => toast.error(e?.messages?.[0] || "Couldn't delete"),
      })
      hideDialog()
    },
  })
}
const DOCSTATUS = { 0: ["Draft", "neutral"], 1: ["Submitted", "success"], 2: ["Cancelled", "danger"] }
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader :title="title || doctype" :subtitle="subtitle">
      <template #actions>
        <Button v-if="canCreate" variant="solid" theme="blue" :label="`New ${(title || doctype).replace(/s$/, '')}`" @click="openNew">
          <template #prefix><Icon name="plus" :size="15" /></template>
        </Button>
      </template>
    </PageHeader>

    <Card :pad="false">
      <div class="border-b border-outline-gray-1 p-3">
        <div class="flex h-[34px] items-center gap-1.5 rounded-md bg-surface-gray-2 px-2.5 text-ink-gray-5">
          <Icon name="search" :size="14" />
          <input v-model="q" placeholder="Search…" class="h-full flex-1 border-none bg-transparent text-[13px] text-ink-gray-9 outline-none ring-0 focus:outline-none focus:ring-0 placeholder:text-ink-gray-4" />
        </div>
      </div>
      <div class="p-3">
        <DataTable :columns="columns" :rows="rows" row-key="name" :loading="list.loading"
          empty-title="Nothing here yet" :empty-message="canCreate ? 'Create the first record above.' : 'No records.'"
          @row-click="openRow">
          <template #cell-docstatus="{ row }">
            <StatusBadge :tone="DOCSTATUS[row.docstatus]?.[1] || 'neutral'" size="sm" dot :label="DOCSTATUS[row.docstatus]?.[0] || '—'" />
          </template>
        </DataTable>
        <div v-if="rows.length || start" class="mt-3 flex items-center justify-between text-[12.5px] text-ink-gray-5">
          <Button variant="ghost" size="sm" label="Previous" :disabled="!start" @click="start = Math.max(0, start - PAGE); fetchList()" />
          <span>Showing {{ start + 1 }}–{{ start + rows.length }}</span>
          <Button variant="ghost" size="sm" label="Next" :disabled="!list.data?.has_more" @click="start += PAGE; fetchList()" />
        </div>
      </div>
    </Card>

    <DocForm :open="drawer.open" :doctype="doctype" :name="drawer.name" @close="drawer.open = false" @saved="onSaved" />
  </div>
</template>
