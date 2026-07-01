<script setup>
// Settings hub — the single home for all configuration, pulled out of the
// operational nav. macOS System-Settings layout: category rail on the left,
// a grid of cards on the right. Every card routes to an existing config page,
// so this is pure information architecture (no new CRUD here).
import { ref, computed, watch } from "vue"
import { useRouter } from "vue-router"
import { Button } from "frappe-ui"
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
        <Button
          v-for="cat in categories"
          :key="cat.label"
          :variant="active === cat.label ? 'subtle' : 'ghost'"
          theme="gray"
          class="w-full !justify-start text-left"
          @click="active = cat.label"
        >
          <div class="flex w-full items-center gap-2.5">
            <Icon :name="cat.icon" :size="16" :class="active === cat.label ? 'text-ink-gray-8' : 'text-ink-gray-6'" />
            <span class="flex-1 truncate text-sm" :class="active === cat.label ? 'font-medium text-ink-gray-9' : 'font-normal text-ink-gray-7'">{{ cat.label }}</span>
          </div>
        </Button>
      </nav>

      <!-- Cards for the active category -->
      <div>
        <h2 class="mb-3 text-sm font-medium text-ink-gray-5">{{ current.label }}</h2>
        <div class="grid gap-3" style="grid-template-columns: repeat(auto-fill, minmax(240px, 1fr))">
          <Button
            v-for="item in current.items"
            :key="item.id"
            variant="ghost"
            class="w-full !justify-start !h-auto text-left"
            @click="open(item)"
          >
            <span class="flex w-full items-start gap-3">
              <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-surface-gray-2 text-ink-gray-7">
                <Icon :name="item.icon" :size="17" />
              </span>
              <span class="min-w-0 flex-1">
                <span class="flex items-center justify-between gap-2">
                  <span class="truncate text-sm font-medium text-ink-gray-9">{{ item.label }}</span>
                  <Icon name="chevRight" :size="15" class="shrink-0 text-ink-gray-4" />
                </span>
                <span class="mt-0.5 block text-xs leading-snug text-ink-gray-5">{{ item.desc }}</span>
              </span>
            </span>
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>
