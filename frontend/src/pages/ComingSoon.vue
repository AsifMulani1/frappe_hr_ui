<script setup>
import { computed } from "vue"
import { useRoute } from "vue-router"
import EmptyState from "@/components/ui/EmptyState.vue"
import PageHeader from "@/components/ui/PageHeader.vue"
import { NAV } from "@/data/nav"

const route = useRoute()
const label = computed(() => {
  for (const role of Object.keys(NAV)) {
    const cfg = NAV[role]
    const items = cfg.items || cfg.groups.flatMap((g) => g.items)
    const it = items.find((i) => i.id === route.params.id)
    if (it) return it.label
  }
  return "Screen"
})
</script>

<template>
  <div class="mx-auto max-w-[1320px] px-6 py-[22px]">
    <PageHeader :title="label" />
    <EmptyState
      icon="layers"
      :title="`${label} — coming up`"
      message="This screen is part of the build and will be wired to live data shortly."
    />
  </div>
</template>
