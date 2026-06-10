<script setup>
// Settings hub — the single home for all configuration, pulled out of the
// operational nav. macOS System-Settings layout: category rail on the left,
// a grid of cards on the right. Every card routes to an existing config page,
// so this is pure information architecture (no new CRUD here).
import { ref, computed, watch } from "vue"
import { useRouter } from "vue-router"
import PageHeader from "@/components/ui/PageHeader.vue"
import Icon from "@/components/ui/Icon.vue"
import EmptyState from "@/components/ui/EmptyState.vue"
import { SETTINGS } from "@/data/nav"
import { useUiStore } from "@/stores/ui"

const router = useRouter()
const ui = useUiStore()

// Only show categories the user can actually administer (by available workspace).
const categories = computed(() => {
  const ids = new Set(ui.availableRoles.map((r) => r.id))
  return SETTINGS.filter((c) => (c.roles || []).some((r) => ids.has(r)))
})

const active = ref(categories.value[0]?.label || "")
watch(categories, (cats) => {
  if (!cats.find((c) => c.label === active.value)) active.value = cats[0]?.label || ""
})
const current = computed(() => categories.value.find((c) => c.label === active.value) || categories.value[0])

function open(item) {
  router.push({ name: item.route })
}
</script>

<template>
  <div class="mx-auto max-w-[1100px] px-6 py-[22px]">
    <PageHeader title="Settings" subtitle="Configure your organization — masters, policies, access and system defaults" />

    <EmptyState v-if="!categories.length" icon="settings" title="No settings available" message="Your role doesn't manage any configuration yet." />

    <div v-else class="mt-5 grid gap-6" style="grid-template-columns: 200px minmax(0, 1fr)">
      <!-- Category rail -->
      <nav class="flex flex-col gap-0.5">
        <button
          v-for="cat in categories"
          :key="cat.label"
          class="flex h-9 items-center gap-2.5 rounded-md px-2.5 text-left text-[13px] transition-colors"
          :class="active === cat.label
            ? 'bg-surface-gray-3 font-medium text-ink-gray-9'
            : 'font-normal text-ink-gray-7 hover:bg-surface-gray-2'"
          @click="active = cat.label"
        >
          <Icon :name="cat.icon" :size="16" :class="active === cat.label ? 'text-ink-gray-8' : 'text-ink-gray-6'" />
          <span class="flex-1 truncate">{{ cat.label }}</span>
        </button>
      </nav>

      <!-- Cards for the active category -->
      <div>
        <h2 class="mb-3 text-[13px] font-medium text-ink-gray-5">{{ current.label }}</h2>
        <div class="grid gap-3" style="grid-template-columns: repeat(auto-fill, minmax(240px, 1fr))">
          <button
            v-for="item in current.items"
            :key="item.id"
            class="group flex items-start gap-3 rounded-xl border border-outline-gray-1 bg-surface-white p-4 text-left transition-all hover:border-outline-gray-3 hover:shadow-sm"
            @click="open(item)"
          >
            <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-surface-gray-2 text-ink-gray-7 group-hover:bg-surface-gray-3">
              <Icon :name="item.icon" :size="17" />
            </span>
            <span class="min-w-0 flex-1">
              <span class="flex items-center justify-between gap-2">
                <span class="truncate text-[13.5px] font-medium text-ink-gray-9">{{ item.label }}</span>
                <Icon name="chevRight" :size="15" class="shrink-0 text-ink-gray-4 transition-transform group-hover:translate-x-0.5 group-hover:text-ink-gray-6" />
              </span>
              <span class="mt-0.5 block text-[12px] leading-snug text-ink-gray-5">{{ item.desc }}</span>
            </span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
