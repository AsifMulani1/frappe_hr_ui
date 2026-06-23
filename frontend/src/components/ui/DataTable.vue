<script setup>
import { computed } from "vue"
import { ListView } from "frappe-ui"
import EmptyState from "./EmptyState.vue"

// Thin wrapper over frappe-ui's ListView that keeps this app's table API:
//   columns: [{ key, label, align?, width?, sortable? }]   (sortable is unused — kept for API compat)
//   Per-column custom cells via scoped slot:  #cell-<key>="{ row, value, index }"
const props = defineProps({
  columns: { type: Array, default: () => [] },
  rows: { type: Array, default: () => [] },
  rowKey: { type: String, default: "name" },
  selectable: Boolean,
  dense: Boolean,
  loading: Boolean,
  emptyTitle: { type: String, default: "Nothing here yet" },
  emptyMessage: String,
})
const emit = defineEmits(["row-click"])

// ListView reads column width into a CSS grid template where a bare number means "fr".
// Our columns use pixel widths, so stringify numbers as px and leave the rest as flex (1fr).
const listColumns = computed(() =>
  props.columns.map((c) => ({
    ...c,
    width: typeof c.width === "number" ? `${c.width}px` : c.width,
  }))
)

const options = computed(() => ({
  selectable: props.selectable,
  showTooltip: false,
  onRowClick: (row) => emit("row-click", row),
  emptyState: { title: props.emptyTitle, description: props.emptyMessage },
}))

const indexOf = (row) => props.rows.indexOf(row)
const showEmpty = computed(() => !props.loading && !props.rows.length)
</script>

<template>
  <div class="overflow-hidden rounded-[10px] border border-outline-gray-1 bg-surface-white">
    <ListView
      v-if="!showEmpty"
      :columns="listColumns"
      :rows="rows"
      :row-key="rowKey"
      :options="options"
      class="!overflow-visible px-2 text-[13.5px]"
    >
      <template #cell="{ column, row, item }">
        <slot :name="`cell-${column.key}`" :row="row" :value="item" :index="indexOf(row)">
          {{ item }}
        </slot>
      </template>
    </ListView>
    <EmptyState v-else :title="emptyTitle" :message="emptyMessage" compact />
    <div v-if="loading" class="p-8 text-center text-[13px] text-ink-gray-5">Loading…</div>
  </div>
</template>
