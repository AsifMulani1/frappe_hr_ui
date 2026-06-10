<script setup>
import { ref, computed } from "vue"
import { Checkbox } from "frappe-ui"
import Icon from "./Icon.vue"
import EmptyState from "./EmptyState.vue"

// columns: [{ key, label, align?, width?, sortable? }]
// Per-column custom cells via scoped slot:  #cell-<key>="{ row, value, index }"
const props = defineProps({
  columns: { type: Array, default: () => [] },
  rows: { type: Array, default: () => [] },
  rowKey: { type: [String, Function], default: "name" },
  selectable: Boolean,
  dense: Boolean,
  loading: Boolean,
  emptyTitle: { type: String, default: "Nothing here yet" },
  emptyMessage: String,
})
const emit = defineEmits(["row-click"])

const keyOf = (r, i) =>
  typeof props.rowKey === "function" ? props.rowKey(r) : r[props.rowKey] ?? i

const sort = ref(null)
const sel = ref({})

const sorted = computed(() => {
  if (!sort.value) return props.rows
  const { key, dir } = sort.value
  return [...props.rows].sort((a, b) => {
    const va = a[key], vb = b[key]
    if (va < vb) return dir === "asc" ? -1 : 1
    if (va > vb) return dir === "asc" ? 1 : -1
    return 0
  })
})
function toggleSort(c) {
  if (!c.sortable) return
  sort.value =
    sort.value && sort.value.key === c.key && sort.value.dir === "asc"
      ? { key: c.key, dir: "desc" }
      : { key: c.key, dir: "asc" }
}
const selCount = computed(() => Object.values(sel.value).filter(Boolean).length)
const allChecked = computed(() => props.rows.length > 0 && props.rows.every((r, i) => sel.value[keyOf(r, i)]))
function toggleAll() {
  if (allChecked.value) sel.value = {}
  else {
    const s = {}
    props.rows.forEach((r, i) => (s[keyOf(r, i)] = true))
    sel.value = s
  }
}
</script>

<template>
  <div class="overflow-hidden rounded-[10px] border border-outline-gray-1 bg-surface-white">
    <div v-if="selectable && selCount" class="flex items-center gap-3 border-b border-blue-100 bg-blue-50 px-3.5 py-2 text-[13px]">
      <span class="font-medium text-blue-700">{{ selCount }} selected</span>
      <button class="text-ink-gray-6 hover:text-ink-gray-9" @click="sel = {}">Clear</button>
    </div>
    <div class="overflow-x-auto">
      <table class="w-full border-collapse text-[13.5px]">
        <thead>
          <tr class="bg-surface-gray-1">
            <th v-if="selectable" class="w-10 border-b border-outline-gray-1 pl-3.5">
              <Checkbox :model-value="allChecked" @update:model-value="toggleAll" />
            </th>
            <th
              v-for="c in columns"
              :key="c.key"
              class="select-none whitespace-nowrap border-b border-outline-gray-1 bg-surface-gray-1 text-[12px] font-medium text-ink-gray-5"
              :class="[dense ? 'px-3 py-2' : 'px-3.5 py-2.5', c.align === 'right' ? 'text-right' : 'text-left', c.sortable ? 'cursor-pointer' : '']"
              :style="c.width ? { width: c.width + 'px' } : {}"
              @click="toggleSort(c)"
            >
              <span class="inline-flex items-center gap-1" :class="c.align === 'right' ? 'justify-end' : ''">
                {{ c.label }}
                <Icon v-if="c.sortable && sort && sort.key === c.key" name="chevUpDown" :size="12" class="opacity-70" />
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(r, i) in sorted"
            :key="keyOf(r, i)"
            class="transition-colors hover:bg-surface-gray-1"
            :class="$attrs.onRowClick ? 'cursor-pointer' : ''"
            @click="emit('row-click', r)"
          >
            <td v-if="selectable" class="border-b border-outline-gray-1 pl-3.5" :class="i === sorted.length - 1 ? '!border-b-0' : ''" @click.stop>
              <Checkbox :model-value="!!sel[keyOf(r, i)]" @update:model-value="sel[keyOf(r, i)] = $event" />
            </td>
            <td
              v-for="c in columns"
              :key="c.key"
              class="border-b border-outline-gray-1 align-middle text-ink-gray-9"
              :class="[dense ? 'px-3 py-2' : 'px-3.5 py-[11px]', c.align === 'right' ? 'text-right' : 'text-left', i === sorted.length - 1 ? '!border-b-0' : '', c.wrap ? '' : 'whitespace-nowrap']"
            >
              <slot :name="`cell-${c.key}`" :row="r" :value="r[c.key]" :index="i">{{ r[c.key] }}</slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="!loading && !rows.length" class="border-t border-outline-gray-1">
      <EmptyState :title="emptyTitle" :message="emptyMessage" compact />
    </div>
    <div v-if="loading" class="p-8 text-center text-[13px] text-ink-gray-5">Loading…</div>
  </div>
</template>
