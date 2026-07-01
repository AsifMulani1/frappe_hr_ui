<script setup>
defineProps({ week: { type: Array, default: () => [] } })

// status -> { container classes, label }
const MAP = {
  present: "border-green-200 bg-green-50 text-green-700",
  active: "border-blue-200 bg-blue-50 text-blue-700 outline outline-1 outline-blue-500",
  leave: "border-orange-200 bg-orange-50 text-orange-700",
  upcoming: "border-outline-gray-1 bg-surface-white text-ink-gray-5",
  weekoff: "border-outline-gray-1 bg-surface-gray-1 text-ink-gray-5",
}
</script>

<template>
  <div class="grid grid-cols-7 gap-2">
    <div
      v-for="(d, i) in week"
      :key="i"
      class="rounded-md border px-1.5 py-2 text-center"
      :class="MAP[d.status] || MAP.upcoming"
    >
      <div class="text-2xs font-medium text-ink-gray-5">{{ d.d }}</div>
      <div class="tnum my-0.5 text-lg font-medium text-ink-gray-9">{{ d.date }}</div>
      <div class="text-2xs font-medium">
        <span v-if="d.status === 'present'">Present</span>
        <span v-else-if="d.status === 'active'">Today</span>
        <span v-else-if="d.status === 'leave'">Leave</span>
        <span v-else-if="d.status === 'weekoff'" class="text-ink-gray-5">Off</span>
        <span v-else class="text-ink-gray-5">—</span>
      </div>
    </div>
  </div>
</template>
