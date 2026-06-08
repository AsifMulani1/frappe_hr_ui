<script setup>
import { computed, inject } from "vue"
import { useRoute } from "vue-router"
import { Avatar, Dropdown } from "frappe-ui"
import Icon from "@/components/ui/Icon.vue"
import { useUiStore } from "@/stores/ui"
import { session } from "@/data/session"

const ui = useUiStore()
const route = useRoute()
const user = inject("$user")

const workspace = computed(() => ui.nav.label)

const title = computed(() => {
  const items = ui.nav.items || ui.nav.groups.flatMap((g) => g.items)
  const found = items.find((i) => i.route && i.route === route.name)
  return found ? found.label : route.meta?.title || "Home"
})

const fullName = computed(() => user?.data?.full_name || session.user || "User")

const userMenu = computed(() => [
  { label: "My profile" },
  { label: "Preferences" },
  { label: "Sign out", onClick: () => session.logout.submit() },
])
</script>

<template>
  <header
    class="flex h-12 shrink-0 items-center gap-3 border-b border-outline-gray-1 bg-surface-white pl-5 pr-4"
  >
    <!-- Breadcrumb -->
    <div class="flex min-w-0 flex-1 items-center gap-1.5">
      <span class="whitespace-nowrap text-sm text-ink-gray-5">{{ workspace }}</span>
      <Icon name="chevRight" :size="14" class="text-ink-gray-4" />
      <span class="truncate text-sm font-medium text-ink-gray-9">{{ title }}</span>
    </div>

    <!-- Right actions -->
    <div class="flex items-center gap-1">
      <button class="flex h-9 w-9 items-center justify-center rounded-md text-ink-gray-7 hover:bg-surface-gray-2">
        <Icon name="help" :size="18" />
      </button>
      <button class="relative flex h-9 w-9 items-center justify-center rounded-md text-ink-gray-7 hover:bg-surface-gray-2">
        <Icon name="bell" :size="18" />
        <span class="absolute right-1.5 top-1.5 h-[7px] w-[7px] rounded-full bg-red-500 ring-2 ring-surface-white" />
      </button>
      <div class="mx-1.5 h-[22px] w-px bg-outline-gray-1" />
      <Dropdown :options="userMenu" placement="right">
        <button class="flex items-center gap-2 rounded-md py-1 pl-1 pr-2 hover:bg-surface-gray-2">
          <Avatar :label="fullName" size="sm" />
          <span class="whitespace-nowrap text-[13px] font-medium text-ink-gray-9">{{ fullName.split(" ")[0] }}</span>
          <Icon name="chevDown" :size="14" class="text-ink-gray-5" />
        </button>
      </Dropdown>
    </div>
  </header>
</template>
